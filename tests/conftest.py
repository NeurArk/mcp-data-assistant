import warnings
from _pytest.runner import runtestprotocol
import asyncio
import gc

def pytest_configure(config):
    """Register custom marks and configure test environment."""
    config.addinivalue_line(
        "markers", "integration: mark a test as an integration test"
    )

    # Completely disable all coroutine warnings
    warnings.filterwarnings("ignore",
                          message="coroutine '.*' was never awaited",
                          category=RuntimeWarning)

# Add a hook to run after each test to ensure no warnings are shown
def pytest_runtest_protocol(item, nextitem):
    # Run the standard test protocol
    reports = runtestprotocol(item, nextitem=nextitem)

    # Clean up any pending tasks that might cause warnings

    # Force garbage collection to clean up unattended coroutines
    gc.collect()

    # Try to cancel any pending tasks
    try:
        # First try with get_running_loop() which doesn't create a new loop
        try:
            loop = asyncio.get_running_loop()
            if not loop.is_closed():
                pending = asyncio.all_tasks(loop=loop)
                for task in pending:
                    if not task.done() and not task.cancelled():
                        task.cancel()
        except RuntimeError:
            # No running loop, try to get or create one
            try:
                loop = asyncio.get_event_loop()
                if not loop.is_closed():
                    pending = asyncio.all_tasks(loop=loop)
                    for task in pending:
                        if not task.done() and not task.cancelled():
                            task.cancel()

                    # Allow cancelled tasks to complete
                    if pending:
                        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            except Exception:
                # No event loop is available or other error, which is fine
                pass
    except Exception:
        # Catch any other exceptions during cleanup
        pass

    # Clean up httpx related resources
    try:
        # Explicitly clean up any httpx resources
        import httpx
        for client in gc.get_objects():
            if isinstance(client, httpx.AsyncClient):
                try:
                    # Create a new event loop just to close the client
                    temp_loop = asyncio.new_event_loop()
                    temp_loop.run_until_complete(client.aclose())
                    temp_loop.close()
                except Exception:
                    # Ignore errors during cleanup
                    pass
    except Exception:
        # Ignore import or other errors
        pass

    return reports
