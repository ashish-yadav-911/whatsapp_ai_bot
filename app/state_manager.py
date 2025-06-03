# In-memory dictionary to store user_id -> thread_id mapping
# WARNING: This is not persistent and will reset when the application restarts.
# Use a database (like SQLite, Redis, etc.) for production.
user_threads = {}

class StateManager:
    def get_thread_id(self, user_id):
        """Retrieves the thread ID for a given user ID."""
        return user_threads.get(user_id)

    def set_thread_id(self, user_id, thread_id):
        """Stores the thread ID for a given user ID."""
        user_threads[user_id] = thread_id
        print(f"State updated: user {user_id} mapped to thread {thread_id}")

    # In a real application, add methods for loading/saving state from/to storage