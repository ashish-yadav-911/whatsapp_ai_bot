

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

# logger = logging.getLogger(__name__)

# main_bp = Blueprint('main', __name__)

# @main_bp.route('/webhook', methods=['GET'])
# def webhook_get():
#     """Endpoint for WhatsApp webhook verification."""
#     return verify_webhook(request.args)

# @main_bp.route('/webhook', methods=['POST'])
# def webhook_post():
#     """Endpoint for receiving incoming WhatsApp messages."""
#     try:
#         data = request.get_json()
#         logger.info("Received webhook data.")
#         # logger.debug(json.dumps(data, indent=2))

#         if data and 'object' in data and data['object'] == 'whatsapp_business_account':
#             for entry in data.get('entry', []):
#                 for change in entry.get('changes', []):
#                     if change.get('field') == 'messages':
#                         for message in change.get('value', {}).get('messages', []):
#                             if message.get('type') == 'text' and 'from' in message and 'id' in message:
#                                 from_number = message['from']
#                                 text_content = message['text']['body']
#                                 whatsapp_message_id = message['id']

#                                 logger.info(f"Processing message ID {whatsapp_message_id} from {from_number}: {text_content}")

#                                 thread_id = get_or_create_thread(from_number)
#                                 if not thread_id:
#                                     send_message(from_number, "Sorry, I couldn't start our conversation thread. Please try again later.")
#                                     return jsonify({"status": "error", "message": "Failed to get/create thread"}), 200

#                                 # Cancel any existing runs
#                                 cancel_existing_runs(thread_id)

#                                 try:
#                                     add_message_to_thread(thread_id, text_content)
#                                 except Exception as e:
#                                      logger.error(f"Failed to add message to thread {thread_id} after cancellation attempt: {e}")
#                                      # Send a user message if adding fails, but still return 200 to WhatsApp
#                                      send_message(from_number, "Sorry, there was a temporary issue processing your message. Please try sending it again.")
#                                      return jsonify({"status": "error", "message": "Failed to add message to thread"}), 200


#                                 # Run the Assistant, handling tool calls
#                                 run = run_assistant_with_tool_handling(from_number, thread_id)


#                                 # Check the final run status and retrieve/send response
#                                 if run and run.status == 'completed':
#                                     logger.info(f"Run completed for user {from_number}. Retrieving response messages for run {run.id}.")
#                                     # --- KEY CHANGE HERE ---
#                                     # Pass the run.id to get_assistant_response
#                                     assistant_responses = get_assistant_response(thread_id, run.id)

#                                     if assistant_responses:
#                                         for response_text in assistant_responses:
#                                             send_message(from_number, response_text)
#                                     else:
#                                          # This is expected if the Assistant completed successfully
#                                          # by only calling a tool that didn't result in a final message.
#                                          logger.info(f"Run {run.id} completed but no text response generated for user {from_number}.")
#                                          # Optional: send a subtle acknowledgement if no text response
#                                          # send_message(from_number, "Okay, got it.")


#                                 else:
#                                     logger.error(f"Assistant run failed or did not complete for user {from_number}. Status: {run.status if run else 'N/A'}. Run ID: {run.id if run else 'N/A'}")
#                                     error_message = "Sorry, I encountered an issue processing your request. Please try again."
#                                     if run and run.last_error:
#                                          logger.error(f"Run Error Details for run {run.id}: Code={run.last_error.code}, Message={run.last_error.message}")

#                                     send_message(from_number, error_message)


#                                 break # Process only the first text message
#                         break
#                 break

#             return jsonify({"status": "success"}), 200

#     except Exception as e:
#         logger.exception("An unexpected error occurred during webhook handling:")
#         # Even on unexpected errors, return 200 to WhatsApp to prevent retries
#         return jsonify({"status": "error", "message": "Internal server error"}), 200









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

# logger = logging.getLogger(__name__)

# main_bp = Blueprint('main', __name__)

# @main_bp.route('/webhook', methods=['GET'])
# def webhook_get():
#     """Endpoint for WhatsApp webhook verification."""
#     return verify_webhook(request.args)

# @main_bp.route('/webhook', methods=['POST'])
# def webhook_post():
#     """Endpoint for receiving incoming WhatsApp messages."""
#     try:
#         data = request.get_json()
#         logger.info("Received webhook data.")
#         # logger.debug(json.dumps(data, indent=2))

#         if data and 'object' in data and data['object'] == 'whatsapp_business_account':
#             for entry in data.get('entry', []):
#                 for change in entry.get('changes', []):
#                     if change.get('field') == 'messages':
#                         for message in change.get('value', {}).get('messages', []):
#                             if message.get('type') == 'text' and 'from' in message and 'id' in message:
#                                 from_number = message['from']
#                                 text_content = message['text']['body']
#                                 whatsapp_message_id = message['id']

#                                 logger.info(f"Processing message ID {whatsapp_message_id} from {from_number}: {text_content}")

#                                 thread_id = get_or_create_thread(from_number)
#                                 if not thread_id:
#                                     send_message(from_number, "Sorry, I couldn't start our conversation thread. Please try again later.")
#                                     return jsonify({"status": "error", "message": "Failed to get/create thread"}), 200

#                                 cancel_existing_runs(thread_id)

#                                 try:
#                                     add_message_to_thread(thread_id, text_content)
#                                 except Exception as e:
#                                      logger.error(f"Failed to add message to thread {thread_id} after cancellation attempt: {e}")
#                                      send_message(from_number, "Sorry, there was a temporary issue processing your message. Please try sending it again.")
#                                      return jsonify({"status": "error", "message": "Failed to add message to thread"}), 200


#                                 run = run_assistant_with_tool_handling(from_number, thread_id)

#                                 if run and run.status == 'completed':
#                                     logger.info(f"Run completed for user {from_number}. Retrieving response messages for run {run.id}.")
#                                     # --- Pass the run.id here ---
#                                     assistant_responses = get_assistant_response(thread_id, run.id) # Make sure run.id is passed

#                                     if assistant_responses:
#                                         for response_text in assistant_responses:
#                                             send_message(from_number, response_text)
#                                     else:
#                                          logger.info(f"Run {run.id} completed but no text response generated for user {from_number}.")

#                                 else:
#                                     logger.error(f"Assistant run failed or did not complete for user {from_number}. Status: {run.status if run else 'N/A'}. Run ID: {run.id if run else 'N/A'}")
#                                     error_message = "Sorry, I encountered an issue processing your request. Please try again."
#                                     if run and run.last_error:
#                                          logger.error(f"Run Error Details for run {run.id}: Code={run.last_error.code}, Message={run.last_error.message}")

#                                     send_message(from_number, error_message)

#                                 break
#                         break
#                 break

#             return jsonify({"status": "success"}), 200

#     except Exception as e:
#         logger.exception("An unexpected error occurred during webhook handling:")
#         return jsonify({"status": "error", "message": "Internal server error"}), 200




from flask import Flask, request, jsonify, Blueprint
from app.whatsapp_api import verify_webhook, send_message
from app.openai_assistant import (
    get_or_create_thread,
    add_message_to_thread,
    run_assistant_with_tool_handling,
    get_assistant_response,
    cancel_existing_runs
)
import json
import logging
import threading # Import threading
import time # For potential delay if needed

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)

# Optional: Simple in-memory set to track processed message IDs for deduplication
# WARNING: This is not persistent and will reset when the server restarts.
# Use Redis, database, etc. for production.
processed_message_ids = set()
# Simple cleanup for the in-memory set (optional)
def cleanup_processed_ids():
    # In a real system, expire old IDs
    processed_message_ids.clear() # Basic clear, not time-based
    logger.info("Cleaned up processed_message_ids set.")
    # threading.Timer(3600, cleanup_processed_ids).start() # Schedule periodic cleanup (e.g., hourly)
# cleanup_processed_ids() # Start initial cleanup timer


# --- Background processing function ---
def process_whatsapp_message(from_number, text_content, whatsapp_message_id):
    """
    Handles the Assistant interaction for a single incoming message.
    Runs in a separate thread.
    """
    # --- Deduplication Check ---
    if whatsapp_message_id in processed_message_ids:
        logger.info(f"Message ID {whatsapp_message_id} already processed. Skipping.")
        return
    processed_message_ids.add(whatsapp_message_id)
    # Optional: Add a mechanism to remove old IDs from the set

    logger.info(f"Starting background processing for message ID {whatsapp_message_id} from {from_number}")

    try:
        thread_id = get_or_create_thread(from_number)
        if not thread_id:
            send_message(from_number, "Sorry, I couldn't start our conversation thread. Please try again later.")
            logger.error(f"Failed to get/create thread for {from_number} in background task.")
            return # Exit background task

        # Cancel any existing runs
        # Might need a small delay after cancellation request if issues persist
        cancel_existing_runs(thread_id)
        # time.sleep(0.5) # Small delay after cancelling, before adding new message

        try:
            add_message_to_thread(thread_id, text_content)
        except Exception as e:
             logger.error(f"Failed to add message to thread {thread_id} for {from_number} in background task: {e}")
             # Send a user message if adding fails
             send_message(from_number, "Sorry, there was a temporary issue processing your message. Please try sending it again.")
             return # Exit background task


        run = run_assistant_with_tool_handling(from_number, thread_id)

        if run and run.status == 'completed':
            logger.info(f"Run completed for user {from_number} in background task. Retrieving response messages for run {run.id}.")
            assistant_responses = get_assistant_response(thread_id, run.id) # Pass run.id

            if assistant_responses:
                for response_text in assistant_responses:
                    # send_message will log success/failure internally
                    send_message(from_number, response_text)
            else:
                 logger.info(f"Run {run.id} completed in background task but no text response generated for user {from_number}.")

        else:
            logger.error(f"Assistant run failed or did not complete for user {from_number} in background task. Status: {run.status if run else 'N/A'}. Run ID: {run.id if run else 'N/A'}")
            error_message = "Sorry, I encountered an issue processing your request. Please try again."
            if run and run.last_error:
                 logger.error(f"Run Error Details for run {run.id}: Code={run.last_error.code}, Message={run.last_error.message}")

            send_message(from_number, error_message)

    except Exception as e:
        logger.exception(f"An unexpected error occurred during background message processing for {from_number}:")
        # Avoid sending message to user here as it might be sent multiple times by retries


@main_bp.route('/webhook', methods=['GET'])
def webhook_get():
    """Endpoint for WhatsApp webhook verification."""
    return verify_webhook(request.args)

@main_bp.route('/webhook', methods=['POST'])
def webhook_post():
    """Endpoint for receiving incoming WhatsApp messages."""
    try:
        data = request.get_json()
        # logger.debug(json.dumps(data, indent=2)) # Use debug level

        # Parse the WhatsApp webhook payload
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
                                # This is crucial to prevent WhatsApp retries
                                return jsonify({"status": "processing"}), 200 # Return immediately after starting background task

        # If the webhook didn't contain a relevant text message, still return 200 OK
        return jsonify({"status": "success"}), 200

    except Exception as e:
        # Catch any unexpected errors during initial webhook parsing/handling
        logger.exception("An unexpected error occurred during initial webhook parsing:")
        # Always return 200 OK to WhatsApp to prevent retries
        # A more specific error message could be included if not successful
        return jsonify({"status": "error", "message": "Internal server error"}), 200