import shelve
import logging
import os
from app.config import Config # Ensure this import is correct
import datetime # datetime not needed for shelve directly

logger = logging.getLogger(__name__)

# Path to the directory where shelve files will be stored
# Use a subdirectory in the project root
SHELVE_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

# Ensure the data directory exists
os.makedirs(SHELVE_DIR, exist_ok=True)
logger.info(f"Shelve directory set to: {SHELVE_DIR}")
logger.info(f"Shelve directory exists: {os.path.exists(SHELVE_DIR)}")

# File names for shelve databases (Python adds extensions like .db, .dat, .dir)
THREADS_SHELVE_FILE = os.path.join(SHELVE_DIR, 'user_threads_shelve')
PROCESSED_MESSAGES_SHELVE_FILE = os.path.join(SHELVE_DIR, 'processed_messages_shelve')


class StateManager:
    # No need for a class-level pool or connection object with shelve
    # Each get/set operation will open and close the shelve file using 'with'


    def __init__(self):
        # Shelve files are created automatically on first write if they don't exist
        # Initializing ensures the directory exists.
        logger.info("StateManager (Shelve) initialized.")

    def get_thread_id(self, user_id: str) -> str | None:
        """Retrieves the thread ID for a given user ID from the shelve file."""
        # Use 'with' statement to ensure the shelve file is closed even if errors occur
        try:
            with shelve.open(THREADS_SHELVE_FILE, 'r') as shelf: # Open in read mode
                thread_id = shelf.get(user_id, None) # Use .get for safe retrieval
            if thread_id:
                logger.info(f"Retrieved thread {thread_id} for user {user_id} from shelve.")
            else:
                logger.info(f"No thread found for user {user_id} in shelve.")
            return thread_id
        except Exception as e:
            logger.error(f"Error getting thread ID for user {user_id} from shelve: {e}")
            return None # Indicate failure to retrieve

    def set_thread_id(self, user_id: str, thread_id: str):
        """Stores or updates the thread ID for a given user ID in the shelve file."""
        try:
            # Use 'with' and writeback=True to modify the dictionary in place
            # writeback=True can have performance implications for large shelves
            # For safety in threaded env and simple state, it's often preferred.
            with shelve.open(THREADS_SHELVE_FILE, 'c', writeback=True) as shelf: # 'c' mode creates if not exists
                shelf[user_id] = thread_id
            logger.info(f"Set/Updated thread {thread_id} for user {user_id} in shelve.")
        except Exception as e:
            logger.error(f"Error setting thread ID for user {user_id} to {thread_id} in shelve: {e}")
            # Error logging is done, but consider error propagation


    # --- Methods for Processed Message IDs (Deduplication) ---

    def has_processed_message(self, message_id: str) -> bool:
        """Checks if a message ID has already been processed using a separate shelve file."""
        try:
            # Open in read mode
            with shelve.open(PROCESSED_MESSAGES_SHELVE_FILE, 'r') as shelf:
                # Check if the message_id exists as a key
                already_processed = message_id in shelf
            if already_processed:
                 logger.info(f"Message ID {message_id} found in processed messages shelve. Already processed.")
            return already_processed
        except Exception as e:
            # Log error but don't fail processing - treat as not processed to be safe
            logger.error(f"Error checking processed message ID {message_id} from shelve: {e}. Assuming not processed.")
            return False # Default to false if check fails

    def add_processed_message(self, message_id: str):
        """Adds a message ID to the processed messages shelve file."""
        try:
            # Open in write mode, create if not exists, use writeback
            with shelve.open(PROCESSED_MESSAGES_SHELVE_FILE, 'c', writeback=True) as shelf:
                # Store the message_id. The value can be anything, e.g., a timestamp.
                shelf[message_id] = datetime.now() # Store timestamp of processing

            logger.info(f"Added message ID {message_id} to processed messages shelve.")
        except Exception as e:
            logger.error(f"Error adding processed message ID {message_id} to shelve: {e}")
            # Error logging is done, but consider error propagation

    # Optional: Cleanup old entries from the processed messages shelve
    # This requires iterating through the shelve, which can be slow.
    # Could be triggered by a separate script or a timer.
    # from datetime import timedelta
    # def cleanup_processed_messages(self, days_to_keep: int = 30):
    #     try:
    #         cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    #         with shelve.open(PROCESSED_MESSAGES_SHELVE_FILE, 'c', writeback=True) as shelf:
    #             keys_to_delete = [key for key, timestamp in shelf.items() if isinstance(timestamp, datetime) and timestamp < cutoff_date]
    #             for key in keys_to_delete:
    #                 del shelf[key]
    #                 logger.info(f"Cleaned up old processed message ID: {key}")
    #             logger.info(f"Cleanup completed. Removed {len(keys_to_delete)} old message IDs.")
    #     except Exception as e:
    #         logger.error(f"Error during processed messages cleanup: {e}")


# Instantiate StateManager once when the module is imported
state_manager = StateManager()

# Optional: Add a function to explicitly close shelve files on shutdown
# shelve automatically syncs on close, but explicit is safer.
# For a simple Flask dev server, this might not be reliable.
# import atexit
# @atexit.register
# def close_shelve_files():
#     try:
#          # Shelve objects are global/module level within the StateManager methods
#          # This explicit closing is tricky with the 'with' pattern per method.
#          # If using a single shared shelve object per manager instance, you'd close it here.
#          # With 'with' per method, each operation syncs/closes, so this is less crucial.
#          logger.info("Attempting to sync/close shelve files...")
#          # shelve.open(THREADS_SHELVE_FILE, 'r').close() # Example, might need error handling
#          # shelve.open(PROCESSED_MESSAGES_SHELVE_FILE, 'r').close() # Example
#          logger.info("Shelve files should be synced.")
#     except Exception as e:
#          logger.error(f"Error during shelve cleanup: {e}")









# import sqlite3
# import logging
# import os
# from app.config import Config
# from datetime import datetime

# logger = logging.getLogger(__name__)

# # Path to the SQLite database file
# # Ensure this path is correct relative to your project root
# DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'bot_state.db')

# # Ensure the data directory exists
# os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
# logger.info(f"Database path set to: {DATABASE_PATH}")
# logger.info(f"Data directory exists: {os.path.exists(os.path.dirname(DATABASE_PATH))}") # Check dir existence


# class StateManager:
#     def __init__(self):
#         self._conn = None
#         # Establish connection and initialize DB immediately on creation
#         # This ensures the connection is ready when get/set are called.
#         try:
#             self._conn = self._get_db_connection()
#             self._initialize_database()
#             logger.info("StateManager initialized successfully.")
#         except Exception as e:
#             logger.error(f"Failed to initialize StateManager: {e}")
#             # If initialization fails, subsequent DB operations will likely fail.
#             # Consider handling this critically upstream if necessary.


#     def _get_db_connection(self):
#         """Gets or establishes a database connection."""
#         # Check if connection is None or closed/stale
#         if self._conn is None: # Or potentially add logic to check if self._conn is closed
#              logger.info(f"Attempting to connect to SQLite DB at: {DATABASE_PATH}")
#              try:
#                  # check_same_thread=False is needed for threading
#                  self._conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
#                  # Use row_factory for easier access by column name
#                  self._conn.row_factory = sqlite3.Row
#                  logger.info(f"Connected to SQLite database: {DATABASE_PATH}")
#              except Exception as e:
#                  logger.error(f"Error connecting to SQLite database {DATABASE_PATH}: {e}")
#                  self._conn = None # Ensure it's None on failure
#                  raise # Re-raise the exception


#         # Optional: Basic check if connection is still usable before returning
#         try:
#             self._conn.execute("SELECT 1").fetchone()
#             # logger.debug("Connection check successful.")
#         except Exception as e:
#             logger.warning(f"SQLite connection seems stale: {e}. Attempting to reconnect.")
#             self._conn.close() # Close the stale connection
#             self._conn = None # Force reconnection on the next call
#             return self._get_db_connection() # Recursively call to get a new connection


#         return self._conn


#     def _initialize_database(self):
#         """Creates the necessary table if it doesn't exist."""
#         conn = self._get_db_connection()
#         cursor = None # Define cursor outside try for logging in except
#         try:
#             cursor = conn.cursor() # Get a cursor
#             cursor.execute('''
#                 CREATE TABLE IF NOT EXISTS user_threads (
#                     user_id TEXT PRIMARY KEY,
#                     thread_id TEXT UNIQUE,
#                     created_at DATETIME DEFAULT CURRENT_TIMESTAMP
#                 )
#             ''')
#             conn.commit() # Explicitly commit the CREATE TABLE statement
#             logger.info("SQLite database table 'user_threads' ensured to exist and committed.")
#         except Exception as e:
#             logger.error(f"Error initializing SQLite database table: {e}")
#             # Consider rolling back if an error occurred after getting cursor but before commit
#             if conn:
#                 conn.rollback()
#             raise


#     def get_thread_id(self, user_id: str) -> str | None:
#         """Retrieves the thread ID for a given user ID from the database."""
#         conn = self._get_db_connection()
#         cursor = None # Define cursor outside try for logging in except
#         try:
#             cursor = conn.cursor() # Get a cursor
#             # Log the SQL query being executed
#             logger.debug(f"Executing SELECT query for user_id: {user_id}")
#             cursor.execute("SELECT thread_id FROM user_threads WHERE user_id = ?", (user_id,))
#             row = cursor.fetchone() # Fetchone returns a dictionary if row_factory is set
#             #thread_id = row['thread_id'] if row and 'thread_id' in row else None
#             thread_id = row['thread_id'] if row else None

#             if thread_id:
#                 logger.info(f"Retrieved thread {thread_id} for user {user_id} from SQLite DB.")
#             else:
#                 logger.info(f"No thread found for user {user_id} in SQLite DB.")

#             return thread_id
#         except Exception as e:
#             logger.error(f"Error getting thread ID for user {user_id} from SQLite DB: {e}")
#             return None # Indicate failure to retrieve
#         finally:
#              if cursor:
#                   cursor.close() # Close cursor


#     def set_thread_id(self, user_id: str, thread_id: str):
#         """Stores or updates the thread ID for a given user ID in the database."""
#         conn = self._get_db_connection()
#         cursor = None # Define cursor outside try for logging in except
#         try:
#             cursor = conn.cursor() # Get a cursor
#             # Log the SQL query being executed
#             logger.debug(f"Executing INSERT OR REPLACE query for user_id: {user_id}, thread_id: {thread_id}")
#             cursor.execute('''
#                 INSERT OR REPLACE INTO user_threads (user_id, thread_id)
#                 VALUES (?, ?)
#             ''', (user_id, thread_id))

#             conn.commit() # --- EXPLICITLY COMMIT THE TRANSACTION ---
#             logger.info(f"Set/Updated thread {thread_id} for user {user_id} in SQLite DB and committed.")
#         except Exception as e:
#             logger.error(f"Error setting thread ID for user {user_id} to {thread_id} in SQLite DB: {e}")
#             # Rollback the transaction on error
#             if conn:
#                 conn.rollback()
#             # Consider raising for upstream handling
#         finally:
#              if cursor:
#                   cursor.close() # Close cursor


#     # Optional: Close the connection when the application shuts down (basic attempt)
#     # This is good practice, though simple scripts might not need it.
#     def close_connection(self):
#         if self._conn:
#             try:
#                 self._conn.close()
#                 logger.info("SQLite database connection explicitly closed.")
#             except Exception as e:
#                 logger.error(f"Error closing SQLite database connection: {e}")
#             finally:
#                 self._conn = None # Ensure it's set to None after closing


# # Instantiate StateManager once when the module is imported
# # Its __init__ will handle connection and DB initialization.
# state_manager = StateManager()

# # Optional: Register a function to close the connection on Flask app shutdown
# # This is a bit more advanced and requires Flask context awareness.
# # For the simple threading model, it might not be strictly necessary but is good.
# # from flask import Flask
# # @app.teardown_appcontext # Needs Flask app context
# # def close_db_connection(exception):
# #     global state_manager # Access the module-level instance
# #     if state_manager and state_manager._conn:
# #         state_manager.close_connection()
# #         # Re-instantiate StateManager for the next request context if needed,
# #         # or ensure _get_db_connection handles re-opening. The current _get_db_connection
# #         # *does* handle re-opening if _conn is None. So closing here is okay.