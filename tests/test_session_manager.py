import pytest
import os
import time
from agent import answer, session_manager

# Skip OpenAI tests if API key is not set
skip_openai = not os.getenv("OPENAI_API_KEY")

@pytest.mark.skipif(skip_openai, reason="OpenAI API key not set")
def test_session_message_counter_real():
    """Test that session messages are properly incremented for each interaction using real API calls."""
    # Create a new session
    session_id = session_manager.create_session()
    print(f"\nCreated new test session: {session_id}")

    try:
        # Log initial state
        messages = session_manager.get_messages(session_id)
        print(f"Initial message count: {len(messages)}")
        assert len(messages) == 0, "Session should start with 0 messages"

        # First simple message/response pair
        print("Sending first message...")
        response1, result1 = answer("What is 2+2?", session_id=session_id)
        print(f"Response: {response1[:50]}...")

        # Check message count after first interaction
        messages = session_manager.get_messages(session_id)
        print(f"Message count after first Q&A: {len(messages)}")
        for i, msg in enumerate(messages):
            print(f"  Message[{i}]: {msg['role']} - {msg['content'][:30]}...")

        assert len(messages) == 2, f"Session should have 2 messages after first Q&A, got {len(messages)}"
        assert messages[0]["role"] == "user"
        assert messages[1]["role"] == "assistant"

        # Short pause to avoid rate limiting
        time.sleep(1)

        # Second message/response pair
        print("Sending second message...")
        response2, result2 = answer(
            "Can you explain the answer in more detail?",
            session_id=session_id,
            prev_result=result1
        )
        print(f"Response: {response2[:50]}...")

        # Check message count after second interaction
        messages = session_manager.get_messages(session_id)
        print(f"Message count after second Q&A: {len(messages)}")
        for i, msg in enumerate(messages):
            print(f"  Message[{i}]: {msg['role']} - {msg['content'][:30]}...")

        assert len(messages) == 4, f"Session should have 4 messages after second Q&A, got {len(messages)}"
        assert messages[2]["role"] == "user"
        assert messages[3]["role"] == "assistant"

        # Short pause to avoid rate limiting
        time.sleep(1)

        # Third message/response pair to verify consistency
        print("Sending third message...")
        response3, result3 = answer(
            "Thank you for explaining.",
            session_id=session_id,
            prev_result=result2
        )
        print(f"Response: {response3[:50]}...")

        # Check message count after third interaction
        messages = session_manager.get_messages(session_id)
        print(f"Message count after third Q&A: {len(messages)}")
        for i, msg in enumerate(messages[-2:]):  # Show just the last conversation pair
            idx = len(messages) - 2 + i
            print(f"  Message[{idx}]: {msg['role']} - {msg['content'][:30]}...")

        assert len(messages) == 6, f"Session should have 6 messages after third Q&A, got {len(messages)}"
        assert messages[4]["role"] == "user"
        assert messages[5]["role"] == "assistant"

    finally:
        # Clean up
        print(f"Cleaning up test session: {session_id}")
        session_manager.delete_session(session_id)

@pytest.mark.skipif(skip_openai, reason="OpenAI API key not set")
def test_session_clear_real():
    """Test that clearing a session properly resets the message counter."""
    # Create a new session
    session_id = session_manager.create_session()
    print(f"\nCreated new test session for clear test: {session_id}")

    try:
        # Add some messages with real API call
        print("Sending test message...")
        response, result = answer("What's the weather today?", session_id=session_id)
        print(f"Response: {response[:50]}...")

        # Verify we have messages
        messages = session_manager.get_messages(session_id)
        print(f"Message count before clear: {len(messages)}")
        assert len(messages) == 2, "Session should have 2 messages"

        # Clear the session
        print("Clearing session...")
        session_manager.clear_session(session_id)

        # Verify messages are cleared
        messages = session_manager.get_messages(session_id)
        print(f"Message count after clear: {len(messages)}")
        assert len(messages) == 0, "Session should have 0 messages after clearing"

        # Test another message after clearing
        print("Sending new message after clear...")
        response2, result2 = answer("Hello after clearing", session_id=session_id)
        print(f"Response: {response2[:50]}...")

        # Verify new message count
        messages = session_manager.get_messages(session_id)
        print(f"Message count after new message: {len(messages)}")
        assert len(messages) == 2, "Session should have 2 messages after new conversation"

    finally:
        # Clean up
        print(f"Cleaning up test session: {session_id}")
        session_manager.delete_session(session_id)