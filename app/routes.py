from flask import Flask, request, jsonify, Blueprint
from app.whatsapp_api import verify_webhook, send_message
from app.openai_assistant import (
    get_or_create_thread,
    add_message_to_thread,
    run_assistant_with_tool_handling,
    get_assistant_response,
    cancel_existing_runs,
    state_manager # Import the state_manager instance
)
import json
import logging
import threading
import time
from openai import APIStatusError

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)

# --- REMOVE THIS OLD LINE ---
# processed_message_ids = set() # <--- ENSURE THIS IN-MEMORY SET IS GONE


# --- Background processing function with Deduplication and Retries ---
def process_whatsapp_message(from_number, text_content, whatsapp_message_id):
    """
    Handles the Assistant interaction for a single incoming message.
    Runs in a separate thread. Includes persistent deduplication and retry logic.
    """
    # --- Persistent Deduplication Check (FIRST STEP) ---
    # Use state_manager to check/add the message ID
    if state_manager.has_processed_message(whatsapp_message_id):
        logger.info(f"Message ID {whatsapp_message_id} already processed (persistent check). Skipping.")
        return # Exit the background task if already processed

    # If not processed, mark it as processed NOW before doing more work
    state_manager.add_processed_message(whatsapp_message_id)
    logger.info(f"Message ID {whatsapp_message_id} marked as processed.")

    logger.info(f"Starting background processing for message ID {whatsapp_message_id} from {from_number}")

    thread_id = None
    max_retries = 5
    retry_delay_seconds = 1 # Reduced initial delay slightly

    for attempt in range(max_retries):
        try:
            # 1. Get or Create OpenAI Thread for this user (Uses persistent state)
            thread_id = get_or_create_thread(from_number)
            if not thread_id:
                logger.error(f"Failed to get/create thread for {from_number} after {attempt+1} attempts.")
                if attempt == max_retries - 1:
                     send_message(from_number, "Sorry, I couldn't start our conversation thread. Please try again later.")
                time.sleep(retry_delay_seconds * (attempt + 1))
                continue # Retry loop

            # 2. Cancel any existing runs (Improved handling in openai_assistant)
            cancel_existing_runs(thread_id)
            # Give OpenAI a brief moment to process cancellation
            time.sleep(0.5) # Small fixed delay after cancelling

            # 3. Add User Message to the Thread (Includes retry logic for thread lock)
            try:
                 add_message_to_thread(thread_id, text_content)
                 message_added_success = True
            except APIStatusError as e:
                 if e.status_code == 400 and e.response is not None and 'active run' in e.response.text:
                      logger.warning(f"Thread {thread_id} locked when adding message for user {from_number} (Attempt {attempt+1}/{max_retries}). Retrying...")
                      message_added_success = False
                 else:
                     logger.error(f"Failed to add message to thread {thread_id} for {from_number} with unexpected API error: {e}")
                     send_message(from_number, "Sorry, there was a temporary issue processing your message. Please try sending it again.")
                     return # Exit background task on unexpected error
            except Exception as e:
                 logger.error(f"Failed to add message to thread {thread_id} for {from_number} with unexpected error: {e}")
                 send_message(from_number, "Sorry, there was a temporary issue processing your message. Please try sending it again.")
                 return # Exit background task on unexpected error

            if not message_added_success:
                 time.sleep(retry_delay_seconds * (attempt + 1))
                 continue # Retry the whole process

            # 4. Run the Assistant on the Thread (Handles its own polling/tool calls)
            try:
                run = run_assistant_with_tool_handling(from_number, thread_id)
                if run is None:
                     logger.warning(f"run_assistant_with_tool_handling returned None for user {from_number} (Attempt {attempt+1}/{max_retries}). Retrying...")
                     time.sleep(retry_delay_seconds * (attempt + 1))
                     continue # Retry loop

            except APIStatusError as e:
                 if e.status_code == 400 and e.response is not None and 'active run' in e.response.text:
                      logger.warning(f"Thread {thread_id} locked when creating run for user {from_number} (Attempt {attempt+1}/{max_retries}). Retrying...")
                      time.sleep(retry_delay_seconds * (attempt + 1))
                      continue # Retry loop
                 else:
                     logger.error(f"Failed to create run for thread {thread_id} for user {from_number} with unexpected API error: {e}")
                     send_message(from_number, "Sorry, I encountered an issue starting the process for your request. Please try again.")
                     return # Exit background task

            except Exception as e:
                 logger.error(f"Failed to create run for thread {thread_id} for user {from_number} with unexpected error: {e}")
                 send_message(from_number, "Sorry, I encountered an issue starting the process for your request. Please try again.")
                 return # Exit background task

            # If we successfully processed (either completed or failed after starting run), break the retry loop
            if run and run.status in ['completed', 'failed', 'expired', 'cancelled']: # Break on any terminal status
                break # Exit the retry loop after processing one run

            # If run is still in_progress or requires_action after run_assistant_with_tool_handling returns,
            # it means the timeout was hit or there was an unhandled state.
            # The run_assistant_with_tool_handling should ideally poll until terminal.
            # If it returns early in a non-terminal state, there might be an issue there.
            # For robustness, we might need a different retry strategy or longer timeout.
            # For now, assume run_assistant_with_tool_handling polls to terminal or None.


        except Exception as e:
             logger.exception(f"An unexpected error occurred during message processing for {from_number} (Attempt {attempt+1}/{max_retries}):")
             if attempt == max_retries - 1:
                  send_message(from_number, "Sorry, I'm having trouble processing your request right now. Please try again in a few moments.")
             time.sleep(retry_delay_seconds * (attempt + 1))


    # End of retry loop. Check if processing was successful or failed after max retries.
    if attempt == max_retries - 1 and (run is None or run.status not in ['completed', 'failed', 'expired', 'cancelled']):
         logger.error(f"Failed to complete message processing for message {whatsapp_message_id} for user {from_number} after {max_retries} attempts.")
         # A final error message to the user might be needed if not sent within the loop
         # But the loop attempts to send on failures.


@main_bp.route('/webhook', methods=['GET'])
def webhook_get():
    return verify_webhook(request.args)

@main_bp.route('/webhook', methods=['POST'])
def webhook_post():
    try:
        data = request.get_json()
        # logger.debug(json.dumps(data, indent=2))

        if data and 'object' in data and data['object'] == 'whatsapp_business_account':
            for entry in data.get('entry', []):
                for change in entry.get('changes', []):
                    if change.get('field') == 'messages':
                        for message in change.get('value', {}).get('messages', []):
                            if message.get('type') == 'text' and 'from' in message and 'id' in message:
                                from_number = message['from']
                                text_content = message['text']['body']
                                whatsapp_message_id = message['id']

                                # --- Start Processing in Background ---
                                logger.info(f"Webhook received message ID {whatsapp_message_id} from {from_number}. Starting background task.")
                                thread = threading.Thread(target=process_whatsapp_message, args=(from_number, text_content, whatsapp_message_id))
                                thread.start()

                                # --- Immediately Return 200 OK ---
                                logger.info(f"Returning 200 OK for message ID {whatsapp_message_id}")
                                return jsonify({"status": "processing", "message_id": whatsapp_message_id}), 200

        return jsonify({"status": "success"}), 200

    except Exception as e:
        logger.exception("An unexpected error occurred during initial webhook parsing:")
        return jsonify({"status": "error", "message": "Internal server error"}), 200
    

    
# from flask import Flask, request, jsonify, Blueprint
# from app.whatsapp_api import verify_webhook, send_message
# from app.openai_assistant import (
#     get_or_create_thread,
#     add_message_to_thread,
#     run_assistant_with_tool_handling,
#     get_assistant_response,
#     cancel_existing_runs
# )
# import json
# import logging
# import threading # Import threading
# import time # For potential delay if needed

# logger = logging.getLogger(__name__)

# main_bp = Blueprint('main', __name__)

# # Optional: Simple in-memory set to track processed message IDs for deduplication
# # WARNING: This is not persistent and will reset when the server restarts.
# # Use Redis, database, etc. for production.
# processed_message_ids = set()
# # Simple cleanup for the in-memory set (optional)
# def cleanup_processed_ids():
#     # In a real system, expire old IDs
#     processed_message_ids.clear() # Basic clear, not time-based
#     logger.info("Cleaned up processed_message_ids set.")
#     # threading.Timer(3600, cleanup_processed_ids).start() # Schedule periodic cleanup (e.g., hourly)
# # cleanup_processed_ids() # Start initial cleanup timer


# # --- Background processing function ---
# def process_whatsapp_message(from_number, text_content, whatsapp_message_id):
#     """
#     Handles the Assistant interaction for a single incoming message.
#     Runs in a separate thread.
#     """
#     # --- Deduplication Check ---
#     if whatsapp_message_id in processed_message_ids:
#         logger.info(f"Message ID {whatsapp_message_id} already processed. Skipping.")
#         return
#     processed_message_ids.add(whatsapp_message_id)
#     # Optional: Add a mechanism to remove old IDs from the set

#     logger.info(f"Starting background processing for message ID {whatsapp_message_id} from {from_number}")

#     try:
#         thread_id = get_or_create_thread(from_number)
#         if not thread_id:
#             send_message(from_number, "Sorry, I couldn't start our conversation thread. Please try again later.")
#             logger.error(f"Failed to get/create thread for {from_number} in background task.")
#             return # Exit background task

#         # Cancel any existing runs
#         # Might need a small delay after cancellation request if issues persist
#         cancel_existing_runs(thread_id)
#         # time.sleep(0.5) # Small delay after cancelling, before adding new message

#         try:
#             add_message_to_thread(thread_id, text_content)
#         except Exception as e:
#              logger.error(f"Failed to add message to thread {thread_id} for {from_number} in background task: {e}")
#              # Send a user message if adding fails
#              send_message(from_number, "Sorry, there was a temporary issue processing your message. Please try sending it again.")
#              return # Exit background task


#         run = run_assistant_with_tool_handling(from_number, thread_id)

#         if run and run.status == 'completed':
#             logger.info(f"Run completed for user {from_number} in background task. Retrieving response messages for run {run.id}.")
#             assistant_responses = get_assistant_response(thread_id, run.id) # Pass run.id

#             if assistant_responses:
#                 for response_text in assistant_responses:
#                     # send_message will log success/failure internally
#                     send_message(from_number, response_text)
#             else:
#                  logger.info(f"Run {run.id} completed in background task but no text response generated for user {from_number}.")

#         else:
#             logger.error(f"Assistant run failed or did not complete for user {from_number} in background task. Status: {run.status if run else 'N/A'}. Run ID: {run.id if run else 'N/A'}")
#             error_message = "Sorry, I encountered an issue processing your request. Please try again."
#             if run and run.last_error:
#                  logger.error(f"Run Error Details for run {run.id}: Code={run.last_error.code}, Message={run.last_error.message}")

#             send_message(from_number, error_message)

#     except Exception as e:
#         logger.exception(f"An unexpected error occurred during background message processing for {from_number}:")
#         # Avoid sending message to user here as it might be sent multiple times by retries


# @main_bp.route('/webhook', methods=['GET'])
# def webhook_get():
#     """Endpoint for WhatsApp webhook verification."""
#     return verify_webhook(request.args)

# @main_bp.route('/webhook', methods=['POST'])
# def webhook_post():
#     """Endpoint for receiving incoming WhatsApp messages."""
#     try:
#         data = request.get_json()
#         # logger.debug(json.dumps(data, indent=2)) # Use debug level

#         # Parse the WhatsApp webhook payload
#         if data and 'object' in data and data['object'] == 'whatsapp_business_account':
#             for entry in data.get('entry', []):
#                 for change in entry.get('changes', []):
#                     if change.get('field') == 'messages':
#                         for message in change.get('value', {}).get('messages', []):
#                             if message.get('type') == 'text' and 'from' in message and 'id' in message:
#                                 from_number = message['from']
#                                 text_content = message['text']['body']
#                                 whatsapp_message_id = message['id']

#                                 # --- Start Processing in Background ---
#                                 logger.info(f"Webhook received message ID {whatsapp_message_id} from {from_number}. Starting background task.")
#                                 thread = threading.Thread(target=process_whatsapp_message, args=(from_number, text_content, whatsapp_message_id))
#                                 thread.start()

#                                 # --- Immediately Return 200 OK ---
#                                 # This is crucial to prevent WhatsApp retries
#                                 return jsonify({"status": "processing"}), 200 # Return immediately after starting background task

#         # If the webhook didn't contain a relevant text message, still return 200 OK
#         return jsonify({"status": "success"}), 200

#     except Exception as e:
#         # Catch any unexpected errors during initial webhook parsing/handling
#         logger.exception("An unexpected error occurred during initial webhook parsing:")
#         # Always return 200 OK to WhatsApp to prevent retries
#         # A more specific error message could be included if not successful
#         return jsonify({"status": "error", "message": "Internal server error"}), 200