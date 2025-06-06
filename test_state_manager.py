import os
import sys
import logging
from datetime import datetime
import time
DATABASE_PATH= os.path.join(os.path.dirname(__file__), 'data', 'bot_state.db')
# Adjust path to project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Configure logging *before* importing modules that use it
# Set level to DEBUG temporarily for testing
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__) # Get logger after basicConfig

# Load config and import StateManager
try:
    # Config import triggers its own logging setup, but basicConfig is already done
    from app.config import Config
    from app.state_manager import StateManager # StateManager is imported by Config and instantiated

except ImportError as e:
    logger.error(f"Error importing required modules: {e}")
    print(f"Error importing required modules: {e}")
    print("Ensure you are running this script from the project root and your virtual environment is active.")
    sys.exit(1)
except Exception as e:
     logger.error(f"An error occurred during initial setup or config loading: {e}")
     print(f"An error occurred during initial setup or config loading: {e}")
     sys.exit(1)


# Access the module-level StateManager instance created on import
state_manager = StateManager()

def test_state_manager_persistence():
    logger.info("--- Starting StateManager persistence test ---")

    # --- Test Run 1: Set a value ---
    print("\n--- Running Test Pass 1: Setting value ---")
    logger.info("Running Test Pass 1: Setting value.")

    # Access the globally instantiated state_manager
    # state_manager = StateManager() # No, use the module-level one

    user_id = "test_user_12345_unique" # Use a unique ID for testing
    initial_thread_id = f"test_thread_{int(time.time())}" # Use timestamp for uniqueness

    # Ensure no previous data for this test user (clean slate)
    # Manually delete data/bot_state.db before the *first* run of this script
    # OR add a specific delete method to StateManager for testing.
    # Let's assume manual deletion of the .db file initially.

    logger.info(f"Attempting to set thread ID {initial_thread_id} for user {user_id}")
    try:
        state_manager.set_thread_id(user_id, initial_thread_id)
        logger.info("Set operation completed (check logs for success confirmation).")
        print("Set operation completed (check logs for success confirmation).")
    except Exception as e:
        logger.error(f"Error during set_thread_id in Test Pass 1: {e}", exc_info=True)
        print(f"Error during set_thread_id in Test Pass 1: {e}. Check logs.")
        # Don't return, proceed to check immediate retrieval even if set failed

    # Test Getting immediately after setting
    logger.info(f"Attempting to retrieve thread ID immediately for user {user_id}")
    try:
         retrieved_thread_id_1 = state_manager.get_thread_id(user_id)
         logger.info(f"Immediately retrieved thread ID: {retrieved_thread_id_1}")
         print(f"Immediately retrieved thread ID: {retrieved_thread_id_1}")
         if retrieved_thread_id_1 == initial_thread_id:
             logger.info("Immediate retrieval matched.")
         else:
             logger.error("Immediate retrieval DID NOT match the set value!")
             print("Immediate retrieval DID NOT match the set value!")

    except Exception as e:
         logger.error(f"Error during immediate get_thread_id in Test Pass 1: {e}", exc_info=True)
         print(f"Error during immediate get_thread_id in Test Pass 1: {e}. Check logs.")


    # Instruct user on next step
    print("\n---------------------------------------------------")
    print("Test Pass 1 Complete.")
    print(f"Thread ID '{initial_thread_id}' was set for user '{user_id}'.")
    print(f"Check the file: {DATABASE_PATH}")
    print("To verify persistence, STOP this script (Ctrl+C), then RUN IT AGAIN immediately.")
    print("The second run will try to retrieve the value you just set.")
    print("---------------------------------------------------")


def test_state_manager_retrieval():
    logger.info("--- Starting StateManager retrieval test ---")
    print("\n--- Running Test Pass 2: Retrieving value ---")
    logger.info("Running Test Pass 2: Retrieving value.")

    # Access the globally instantiated state_manager
    # state_manager = StateManager() # No, use the module-level one

    user_id = "test_user_12345_unique" # Use the same user ID as Test Pass 1

    logger.info(f"Attempting to retrieve thread ID after simulated restart for user {user_id}")
    try:
         retrieved_thread_id_2 = state_manager.get_thread_id(user_id)
         logger.info(f"After simulated restart, retrieved thread ID: {retrieved_thread_id_2}")
         print(f"After simulated restart, retrieved thread ID: {retrieved_thread_id_2}")

         if retrieved_thread_id_2 is not None:
              logger.info("Persistence test PASSED! Successfully retrieved thread ID after restart.")
              print("Persistence test PASSED! Successfully retrieved thread ID after restart.")
         else:
              logger.error("Persistence test FAILED! Did NOT retrieve thread ID after restart.")
              print("Persistence test FAILED! Did NOT retrieve thread ID after restart.")

    except Exception as e:
         logger.error(f"Error during get_thread_id in Test Pass 2: {e}", exc_info=True)
         print(f"Error during get_thread_id in Test Pass 2: {e}. Check logs.")


    print("\n---------------------------------------------------")
    print("Test Pass 2 Complete.")
    print(f"Check the file: {DATABASE_PATH}")
    print("Check logs and console output to see if the thread ID was retrieved.")
    print("---------------------------------------------------")


if __name__ == "__main__":
    print("Run this script twice:")
    print("First run: Saves a test value.")
    print("Second run: Attempts to retrieve the saved value.")
    choice = input("Enter '1' to run Test Pass 1 (Save) or '2' to run Test Pass 2 (Retrieve): ").strip()

    if choice == '1':
        # Optional: Manually delete data/bot_state.db before the *first* run if you want to start fresh
        db_file = os.path.join(os.path.dirname(__file__), 'data', 'bot_state.db')
        # if os.path.exists(db_file):
        #     print(f"Deleting existing DB file: {db_file}")
        #     os.remove(db_file) # USE CAUTION - THIS DELETES YOUR DB

        test_state_manager_persistence() # This runs the "set" part
    elif choice == '2':
        test_state_manager_retrieval() # This runs the "get" part
    else:
        print("Invalid choice.")

    # Optional: Close connection when the script exits (basic attempt)
    # try:
    #      if state_manager and state_manager._conn:
    #           state_manager.close_connection()
    # except Exception as e:
    #      logger.error(f"Error closing connection on script exit: {e}")