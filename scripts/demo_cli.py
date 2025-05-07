#!/usr/bin/env python
import os
import sys
import time
import traceback
import logging
from pathlib import Path

# Add parent directory to path to import the agent module
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("demo_cli")


def main():
    from agent import answer
    if not os.getenv("OPENAI_API_KEY"):
        print("Set OPENAI_API_KEY first.")
        exit(1)

    prompt = " ".join(sys.argv[1:]) or \
             "Give me total sales for 2024 and create a PDF report"
    print("USER:", prompt)

    try:
        # Check reports folder state before
        reports_dir = parent_dir / "reports"
        before_files = list(reports_dir.glob("*.pdf"))
        logger.info(f"PDF files before: {len(before_files)}")
        if before_files:
            logger.info(
                f"Latest PDF before: "
                f"{max(before_files, key=lambda p: p.stat().st_mtime)}"
            )

        # Execute the agent
        logger.info("Calling agent...")
        response = answer(prompt)
        print("ASSISTANT:", response)

        # Check reports folder state after
        after_files = list(reports_dir.glob("*.pdf"))
        logger.info(f"PDF files after: {len(after_files)}")
        if after_files:
            latest = max(after_files, key=lambda p: p.stat().st_mtime)
            logger.info(f"Latest PDF after: {latest}")

            # Check if new files were created
            new_files = [f for f in after_files if f not in before_files]
            if new_files:
                logger.info(f"New PDF files created: {new_files}")

                # Check size and age of latest file
                latest_age = os.path.getmtime(latest) - time.time()
                logger.info(
                    f"Latest PDF age: {latest_age:.1f}s, "
                    f"size: {latest.stat().st_size} bytes"
                )

    except Exception as e:
        logger.error(f"Error in demo_cli: {str(e)}")
        logger.error(traceback.format_exc())
        print("ASSISTANT: An error occurred processing your request.")


if __name__ == "__main__":
    start_time = time.time()
    main()
    logger.info(f"Total execution time: {time.time() - start_time:.2f}s")
