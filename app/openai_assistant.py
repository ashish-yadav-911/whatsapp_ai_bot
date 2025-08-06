# # import time
# # import json
# # import requests
# # import logging
# # from openai import OpenAI
# # from app.config import Config # Ensure this import is correct
# # from app.state_manager import StateManager
# # from app.whatsapp_api import send_message
# # from dateutil.parser import parse as parse_datetime
# # from datetime import timedelta, datetime

# # logger = logging.getLogger(__name__)

# # client = OpenAI(api_key=Config.OPENAI_API_KEY)
# # state_manager = StateManager()

# # # --- Your API Interaction Functions (Adapted) ---

# # # Keep get_access_token as is, it looks correct for fetching the token
# # def get_access_token(doctor_id, clinic_id, api_key):
# #     """
# #     Gets a one-time access token using doctor and clinic ID.
# #     Uses Config for BASE_URL and API_KEY.
# #     """
# #     if not Config.CRM_API_BASE_URL or not api_key:
# #         logger.error("Scheduling API base URL or API key not configured for token request.")
# #         return None

# #     url = f"{Config.CRM_API_BASE_URL}/auth/one-time-token/"
# #     headers = {
# #         'X-API-KEY': api_key, # Use X-API-KEY based on your previous example
# #         'Content-Type': 'application/json',
# #     }
# #     payload = {
# #         "doctor_id": doctor_id,
# #         "clinic_id": clinic_id
# #     }

# #     try:
# #         response = requests.post(url, headers=headers, data=json.dumps(payload))
# #         logger.info(f"Token API response status: {response.status_code}")
# #         # logger.debug(f"Token API response body: {response.text}") # Uncomment for detailed debugging
# #         response.raise_for_status()

# #         response_data = response.json()
# #         token = response_data.get('access_token') # Adjust key name here based on YOUR API response

# #         if not token:
# #             logger.error("Access token not found in token response JSON.")
# #             return None
# #         return token
# #     except requests.exceptions.RequestException as e:
# #         logger.error(f"[Error fetching token] Request failed: {e}")
# #         if e.response is not None:
# #              logger.error(f"Response status: {e.response.status_code}, Response body: {e.response.text}")
# #         return None
# #     except json.JSONDecodeError:
# #          logger.error("[Error fetching token] Failed to decode JSON response.")
# #          return None
# #     except ValueError as e:
# #          logger.error(f"[Error fetching token] {e}")
# #          return None
# #     except Exception as e:
# #         logger.error(f"[Error fetching token] An unexpected error occurred: {e}")
# #         return None


# # # --- MODIFIED schedule_meeting function ---
# # def schedule_meeting(access_token: str, name: str, phone: str, email: str, date_time_iso: str, procedure_id: int, health_operator_id: int):
# #     """
# #     Schedules a meeting using the access token and details directly from the Assistant.
# #     Uses Config for BASE_URL, PROCEDURE_ID, HEALTH_OPERATOR_ID.
# #     date_time_iso should be in 'YYYY-MM-DDTHH:mm:ss.000Z' format.
# #     """
# #     if not Config.CRM_API_BASE_URL or not access_token:
# #         logger.error("Scheduling API base URL or access token missing.")
# #         return None

# #     url = f"{Config.CRM_API_BASE_URL}/appointment/create/" # Endpoint confirmed by curl
# #     headers = {
# #         'Authorization': f'Bearer {access_token}', # Auth header confirmed by curl
# #         'Content-Type': 'application/json',        # Content-Type confirmed by curl
# #     }
# #     payload = {
# #         "name": name,                       # From Assistant
# #         "phone": phone,                     # From Assistant
# #         "email": email,                     # From Assistant
# #         "procedure": str(procedure_id),     # From Config, cast to string if API expects string
# #         "health_operator": str(health_operator_id), # From Config, cast to string
# #         "date": date_time_iso               # From Assistant (parsed/formatted)
# #     }

# #     logger.info(f"Attempting to schedule meeting with payload: {payload}")
# #     try:
# #         response = requests.post(url, headers=headers, data=json.dumps(payload))
# #         logger.info(f"Schedule meeting API response status: {response.status_code}")
# #         # logger.debug(f"Schedule meeting API response body: {response.text}") # Uncomment for detailed debugging
# #         response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

# #         logger.info("Meeting scheduling API call successful.")
# #         return response.json() # Return the response JSON
# #     except requests.exceptions.RequestException as e:
# #         logger.error(f"Error scheduling meeting: Request failed: {e}")
# #         if e.response is not None:
# #              logger.error(f"Response status: {e.response.status_code}, Response body: {e.response.text}")
# #              try:
# #                  # Log the response body if it contains API-specific error details
# #                  logger.error(f"Response body JSON: {e.response.json()}")
# #              except json.JSONDecodeError:
# #                  pass # Ignore if response body isn't JSON
# #         return None
# #     except json.JSONDecodeError:
# #          logger.error("Error scheduling meeting: Failed to decode JSON response.")
# #          return None
# #     except Exception as e:
# #         logger.error(f"Error scheduling meeting: An unexpected error occurred: {e}")
# #         return None


# # # --- Helper Functions ---

# # # REMOVE or comment out get_or_create_patient_id as it's not needed for this API

# # # --- MODIFIED parse_and_format_datetime function ---
# # def parse_and_format_datetime(datetime_str: str) -> str | None:
# #     """
# #     Parses a natural language datetime string and formats it into
# #     'YYYY-MM-DDTHH:mm:ss.000Z' format required by the API.
# #     Assumes the time refers to today or the near future if no date is specified.
# #     """
# #     if not datetime_str:
# #         return None

# #     try:
# #         # dateutil.parser is good at handling various formats
# #         start_dt = parse_datetime(datetime_str)

# #         # Basic check to push date forward if time is in the past (heuristic)
# #         # As before, robust date resolution is complex. This is a basic attempt.
# #         now = datetime.now()
# #         # If parsed time is today but in the past, move to tomorrow.
# #         if start_dt.date() == now.date() and start_dt.time() < now.time():
# #              # Add a buffer (e.g., 5 minutes) before considering it "past"
# #              if start_dt < now - timedelta(minutes=5):
# #                  logger.info(f"Parsed datetime {start_dt} is in the past. Assuming next occurrence tomorrow.")
# #                  start_dt = start_dt + timedelta(days=1)
# #         elif start_dt < now - timedelta(minutes=5):
# #              # If the parsed date itself is clearly in the past,
# #              # dateutil might have handled it (e.g., "last Friday").
# #              # If it still results in a past date here, it's likely not intended.
# #              # Log a warning, but we'll proceed with the parsed date for now.
# #              logger.warning(f"Parsed datetime {start_dt} is significantly in the past. Proceeding but may cause API error.")


# #         # Format to 'YYYY-MM-DDTHH:mm:ss.000Z'
# #         # The API expects UTC ('Z'). If parse_datetime gives a naive datetime,
# #         # we need to make it timezone aware (e.g., assume local time) and convert to UTC.
# #         # Using isoformat() with fromisoformat() often handles this if the input string is timezone aware.
# #         # If the input from AI is naive (like '2025-05-30 10:30 AM'), parse_datetime gives a naive datetime.
# #         # We *must* correctly convert this to UTC before formatting with 'Z'.

# #         # Correct Timezone Handling: Assume naive time from AI is local time, convert to UTC.
# #         try:
# #             from dateutil.tz import tzlocal, tzutc
# #             if start_dt.tzinfo is None:
# #                 # Assume naive datetime is in the local timezone
# #                 start_dt = start_dt.replace(tzinfo=tzlocal()).astimezone(tzutc())
# #             elif start_dt.tzinfo != tzutc():
# #                  # If timezone aware but not UTC, convert to UTC
# #                  start_dt = start_dt.astimezone(tzutc())
# #             # Now start_dt is UTC aware
# #             start_time_iso = start_dt.isoformat(timespec='milliseconds').replace('+00:00', 'Z')

# #         except Exception as tz_e:
# #             logger.error(f"Error during timezone conversion: {tz_e}. Formatting naive datetime potentially incorrectly.")
# #             # Fallback to simpler formatting if timezone conversion fails (less robust)
# #             start_time_iso = start_dt.strftime('%Y-%m-%dT%H:%M:%S.000Z') # Simple format, ignores original timezone

# #         logger.info(f"Parsed '{datetime_str}' into formatted date string='{start_time_iso}'")
# #         return start_time_iso

# #     except ValueError as e:
# #         logger.error(f"Error parsing datetime string '{datetime_str}': {e}")
# #         return None
# #     except Exception as e:
# #         logger.error(f"An unexpected error occurred during datetime parsing/formatting: {e}")
# #         return None


# # # --- Tool Handler Implementations ---

# # # handle_collect_scheduling_info (Keep as is)
# # def handle_collect_scheduling_info(user_id: str, name: str = None, email: str = None, phone: str = None, datetime: str = None):
# #     logger.info(f"User {user_id}: Assistant provided scheduling info: Name={name}, Email={email}, Phone={phone}, Datetime={datetime}")
# #     gathered_info = {}
# #     if name: gathered_info["name"] = name
# #     if email: gathered_info["email"] = email
# #     if phone: gathered_info["phone"] = phone
# #     if datetime: gathered_info["datetime"] = datetime
# #     if not gathered_info:
# #          return "Assistant attempted to collect info but provided no details."
# #     info_summary = ", ".join([f"{k}: {v}" for k, v in gathered_info.items()])
# #     return f"Acknowledged collection of scheduling info: {info_summary}. I will use this when scheduling if confirmed."


# # # --- MODIFIED handle_schedule_meeting_with_dr_inae ---
# # def handle_schedule_meeting_with_dr_inae(user_id: str, name: str, email: str, phone: str, datetime: str):
# #     """
# #     Orchestrates scheduling a meeting using the new API payload structure.
# #     """
# #     logger.info(f"User {user_id}: Attempting to schedule meeting for Dr. Inae with: Name={name}, Email={email}, Phone={phone}, Datetime={datetime}")

# #     # 1. Validate required inputs from the Assistant (matches tool definition required fields)
# #     if not all([name, email, phone, datetime]):
# #         logger.error(f"User {user_id}: Missing required scheduling info from Assistant. Name={name}, Email={email}, Phone={phone}, Datetime={datetime}")
# #         return "Error: Missing required information (name, email, phone, or date/time) to schedule the meeting."

# #     # 2. Ensure Scheduling API configuration is complete (including new IDs)
# #     if not Config.CRM_API_BASE_URL or not Config.CRM_API_KEY or Config.DOCTOR_ID is None or Config.CLINIC_ID is None or Config.PROCEDURE_ID is None or Config.HEALTH_OPERATOR_ID is None:
# #         logger.error(f"User {user_id}: CRM/Scheduling API details (URL, Key, Doctor/Clinic/Procedure/Operator IDs) not fully set or are invalid.")
# #         return "Error: The meeting scheduling system is not fully configured. Please contact HR directly."

# #     # 3. Parse and format datetime
# #     # Use the modified function to get the single formatted date string
# #     date_time_iso = parse_and_format_datetime(datetime)
# #     if not date_time_iso:
# #         logger.error(f"User {user_id}: Failed to parse or format datetime string: {datetime}")
# #         return f"Error: Could not understand the requested date and time '{datetime}'. Please provide it in a clearer format (e.g., 'YYYY-MM-DD HH:mm')."

# #     # 4. Get Access Token (requires Doctor and Clinic IDs from Config)
# #     access_token = get_access_token(Config.DOCTOR_ID, Config.CLINIC_ID, Config.CRM_API_KEY)
# #     if not access_token:
# #         logger.error(f"User {user_id}: Failed to get access token.")
# #         return "Error: Could not get authorization to schedule the meeting. Please try again."

# #     # 5. Schedule the meeting
# #     # Call the modified schedule_meeting function with the new parameters
# #     scheduling_result = schedule_meeting(
# #         access_token=access_token,
# #         name=name,
# #         phone=phone,
# #         email=email,
# #         date_time_iso=date_time_iso, # Pass the single formatted date string
# #         procedure_id=Config.PROCEDURE_ID, # From Config
# #         health_operator_id=Config.HEALTH_OPERATOR_ID # From Config
# #     )

# #     # 6. Process scheduling result and return response for Assistant
# #     if scheduling_result:
# #         # Assuming scheduling_result is the JSON response from the API on success
# #         # You might need to inspect the actual API response to get confirmation details
# #         confirmation_details = scheduling_result.get("appointment_id", "N/A") # Example key, ADJUST THIS
# #         logger.info(f"User {user_id}: Meeting scheduled successfully. API Response: {scheduling_result}")
# #         return f"Success: Meeting with Dr. Inae scheduled successfully. Confirmation ID: {confirmation_details}"
# #     else:
# #         logger.error(f"User {user_id}: Scheduling API call failed.")
# #         return "Error: Failed to schedule the meeting through the system. Please try again or contact HR directly."


# # # handle_transfer_chat_to_whatsapp (Keep as is after adding summary logic)
# # def handle_transfer_chat_to_whatsapp(user_id: str, user_name: str = None, conversation_summary: str = None, message_to_user: str = None):
# #     """
# #     Handles the request to transfer the chat.
# #     Sends a transfer message to the user AND sends summary/details to the transfer number.
# #     """
# #     transfer_number = Config.WHATSAPP_TRANSFER_NUMBER

# #     if not transfer_number or transfer_number == "ANOTHER_WHATSAPP_PHONE_NUMBER":
# #         logger.error(f"User {user_id}: WhatsApp transfer number not configured.")
# #         user_feedback = "Error: Chat transfer is not currently configured. Please contact HR directly."
# #         send_message(recipient_id=user_id, text=user_feedback)
# #         return "Error: Chat transfer functionality is not configured."

# #     logger.info(f"User {user_id}: Attempting to transfer chat to number: {transfer_number}")

# #     user_transfer_message = message_to_user if message_to_user else (
# #         f"Okay, I will transfer you to a human agent. You can contact them directly on WhatsApp at {transfer_number}. "
# #         "Please provide them with your name and your query again for context."
# #     )
# #     user_msg_success = send_message(recipient_id=user_id, text=user_transfer_message)

# #     if not user_msg_success:
# #         logger.error(f"User {user_id}: Failed to send transfer confirmation message to user.")

# #     summary_parts = [
# #         "--- Chat Transfer Request ---",
# #         f"From WhatsApp User: {user_id}",
# #         f"User Name (if known): {user_name if user_name else 'N/A'}"
# #     ]

# #     if conversation_summary:
# #         summary_parts.append(f"\nConversation Summary:\n{conversation_summary}")
# #     else:
# #         summary_parts.append("\nNote: No conversation summary was provided by the bot.")
# #         logger.warning(f"User {user_id}: Assistant did not provide a conversation_summary for transfer.")

# #     agent_summary_message = "\n".join(summary_parts)
# #     agent_msg_success = send_message(recipient_id=transfer_number, text=agent_summary_message)

# #     if user_msg_success and agent_msg_success:
# #         logger.info(f"User {user_id}: Both user confirmation and agent summary messages sent successfully.")
# #         return f"Chat transfer initiated. User notified ({user_id}). Summary sent to agent number ({transfer_number})."
# #     elif user_msg_success and not agent_msg_success:
# #         logger.warning(f"User {user_id}: User notified, but failed to send summary to agent number ({transfer_number}).")
# #         return f"Chat transfer initiated, but failed to send conversation summary to the agent. Please inform the agent manually."
# #     elif not user_msg_success and agent_msg_success:
# #          logger.error(f"User {user_id}: Failed to notify user, but summary sent to agent number ({transfer_number}).")
# #          return "Error: Failed to notify you about the chat transfer, but a summary was sent to the agent. Please contact them directly."
# #     else:
# #         logger.error(f"User {user_id}: Failed to send both user notification and agent summary.")
# #         return "Error: Failed to initiate chat transfer. Neither user nor agent could be notified."


# # # cancel_existing_runs, execute_tool_call, run_assistant_with_tool_handling,
# # # get_assistant_response, get_or_create_thread, add_message_to_thread
# # # (Keep these functions as they were in the previous step, assuming you added cancel_existing_runs)

# # # ... [Paste cancel_existing_runs, execute_tool_call, run_assistant_with_tool_handling, get_assistant_response, get_or_create_thread, add_message_to_thread functions here] ...

# # def cancel_existing_runs(thread_id: str):
# #     """
# #     Checks for and cancels any non-terminal runs on a given thread.
# #     """
# #     try:
# #         runs = client.beta.threads.runs.list(thread_id=thread_id, limit=10)
# #         active_runs = [ run for run in runs.data if run.status in ['queued', 'in_progress', 'cancelling', 'requires_action'] ]
# #         if not active_runs:
# #             logger.info(f"No active runs found on thread {thread_id}.")
# #             return False
# #         logger.warning(f"Found {len(active_runs)} active run(s) on thread {thread_id}. Attempting to cancel...")
# #         cancellation_attempted = False
# #         for run in active_runs:
# #             try:
# #                 logger.warning(f"Cancelling run {run.id} with status {run.status} on thread {thread_id}.")
# #                 client.beta.threads.runs.cancel(thread_id=thread_id, run_id=run.id)
# #                 cancellation_attempted = True
# #             except Exception as e:
# #                 logger.error(f"Failed to cancel run {run.id} on thread {thread_id}: {e}")
# #         return cancellation_attempted
# #     except Exception as e:
# #         logger.error(f"Error listing or attempting to cancel runs for thread {thread_id}: {e}")
# #         return False

# # def execute_tool_call(user_id: str, function_name: str, arguments: dict):
# #     tool_functions = {
# #         "collect_scheduling_info": handle_collect_scheduling_info,
# #         "schedule_meeting_with_dr_inae": handle_schedule_meeting_with_dr_inae,
# #         "transfer_chat_to_whatsapp": handle_transfer_chat_to_whatsapp,
# #     }
# #     if function_name in tool_functions:
# #         try:
# #             result = tool_functions[function_name](user_id=user_id, **arguments)
# #             return str(result)
# #         except TypeError as e:
# #              logger.error(f"User {user_id}: Error calling tool function '{function_name}': Invalid arguments provided by Assistant. Details: {e}")
# #              return f"Error: Function '{function_name}' received incorrect arguments. Details: {e}"
# #         except Exception as e:
# #             logger.error(f"User {user_id}: Error executing tool function '{function_name}': {e}")
# #             return f"Error executing function '{function_name}': {e}"
# #     else:
# #         logger.warning(f"User {user_id}: Unknown tool function requested by Assistant: {function_name}")
# #         return f"Error: Unknown function requested: {function_name}"

# # def run_assistant_with_tool_handling(user_id: str, thread_id: str):
# #     if not Config.OPENAI_ASSISTANT_ID:
# #         logger.error("OPENAI_ASSISTANT_ID not set in config.")
# #         return None
# #     try:
# #         logger.info(f"Running assistant {Config.OPENAI_ASSISTANT_ID} on thread {thread_id} for user {user_id}...")
# #         run = client.beta.threads.runs.create(
# #             thread_id=thread_id,
# #             assistant_id=Config.OPENAI_ASSISTANT_ID,
# #         )
# #         timeout_seconds = 120
# #         start_time = time.time()
# #         while run.status in ['queued', 'in_progress', 'cancelling', 'requires_action']:
# #             if time.time() - start_time > timeout_seconds:
# #                 logger.warning(f"Run for user {user_id} timed out after {timeout_seconds} seconds. Status: {run.status}")
# #                 try: client.beta.threads.runs.cancel(thread_id=thread_id, run_id=run.id)
# #                 except Exception as cancel_e: logger.error(f"Failed to cancel run {run.id}: {cancel_e}")
# #                 return None
# #             time.sleep(1)
# #             run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
# #             logger.info(f"Run status for user {user_id}: {run.status}")
# #             if run.status == 'requires_action':
# #                 logger.info(f"Run requires action for user {user_id} (tool calling)...")
# #                 tool_outputs = []
# #                 try:
# #                     for tool_call in run.required_action.submit_tool_outputs.tool_calls:
# #                         call_id = tool_call.id
# #                         function_name = tool_call.function.name
# #                         try: arguments = json.loads(tool_call.function.arguments)
# #                         except json.JSONDecodeError as e:
# #                             logger.error(f"User {user_id}: Error decoding tool call arguments for ID {call_id}: {e}")
# #                             output = f"Error: Invalid JSON arguments for function {function_name}."
# #                             tool_outputs.append({"tool_call_id": call_id, "output": output})
# #                             continue
# #                         logger.info(f"User {user_id}: Tool call requested: ID={call_id}, Name={function_name}, Args={arguments}")
# #                         output = execute_tool_call(user_id, function_name, arguments)
# #                         tool_outputs.append({"tool_call_id": call_id, "output": output})
# #                         logger.info(f"User {user_id}: Tool call executed. Output: {output}")
# #                     logger.info(f"User {user_id}: Submitting tool outputs...")
# #                     run = client.beta.threads.runs.submit_tool_outputs(
# #                         thread_id=thread_id,
# #                         run_id=run.id,
# #                         tool_outputs=tool_outputs
# #                     )
# #                     logger.info(f"User {user_id}: Tool outputs submitted. New run status: {run.status}")
# #                 except Exception as tool_handling_e:
# #                     logger.error(f"User {user_id}: An error occurred during tool call handling: {tool_handling_e}")
# #                     return None
# #             elif run.status in ['queued', 'in_progress']: pass
# #             elif run.status in ['completed', 'failed', 'cancelled', 'expired']: break
# #         if run.status == 'completed':
# #             logger.info(f"Run completed successfully for user {user_id}.")
# #             return run
# #         else:
# #             logger.warning(f"Run ended with non-completed status for user {user_id}: {run.status}")
# #             if run.last_error: logger.error(f"Run Last Error Details: {run.last_error.code} - {run.last_error.message}")
# #             return None
# #     except Exception as e:
# #         logger.error(f"User {user_id}: An error occurred creating or polling run: {e}")
# #         return None


# # def get_assistant_response(thread_id: str, run_id: str):
# #     """
# #     Retrieves the latest assistant messages from a thread *that belong to a specific run*.
# #     """
# #     try:
# #         # List messages in descending order
# #         # We can fetch a reasonable limit (e.g., 20) and then filter by run_id
# #         messages = client.beta.threads.messages.list(
# #           thread_id=thread_id,
# #           order="desc", # Newest messages first
# #           limit=20 # Fetch enough messages to likely include all from the last run
# #         )

# #         assistant_messages = []
# #         # Iterate through messages from newest to oldest
# #         for msg in messages.data:
# #             # --- KEY CHANGE HERE ---
# #             # Only include messages where the role is 'assistant' AND
# #             # the run_id matches the specific run we just completed.
# #             if msg.role == 'assistant' and msg.run_id == run_id:
# #                 # Assuming text content for simplicity
# #                 text_content = "".join([
# #                     block.text.value for block in msg.content if block.type == 'text'
# #                 ])
# #                 if text_content: # Only add non-empty messages
# #                     assistant_messages.append(text_content)
          

# #         assistant_messages.reverse() # Put them back in chronological order (oldest new message first)
# #         return assistant_messages

# #     except Exception as e:
# #         logger.error(f"Error retrieving messages from thread {thread_id} for run {run_id}: {e}")
# #         return []


# # def get_or_create_thread(user_id):
# #     thread_id = state_manager.get_thread_id(user_id)
# #     if not thread_id:
# #         logger.info(f"No thread found for user {user_id}. Creating a new one.")
# #         try:
# #             thread = client.beta.threads.create()
# #             thread_id = thread.id
# #             state_manager.set_thread_id(user_id, thread_id)
# #             logger.info(f"New thread created: {thread_id}")
# #         except Exception as e:
# #             logger.error(f"Error creating thread: {e}")
# #             return None
# #     else:
# #          logger.info(f"Using existing thread {thread_id} for user {user_id}.")
# #     return thread_id

# # def add_message_to_thread(thread_id, content):
# #     try:
# #         message = client.beta.threads.messages.create(
# #           thread_id=thread_id, role="user", content=content,
# #         )
# #         logger.info(f"Message added to thread {thread_id}: {message.id}")
# #         return message
# #     except Exception as e:
# #         logger.error(f"Error adding message to thread {thread_id}: {e}")
# #         return None












import time
import json
import requests
import logging
from openai import OpenAI
from app.config import Config
from app.state_manager import StateManager
from app.whatsapp_api import send_message
from dateutil.parser import parse as parse_datetime
from datetime import timedelta, datetime
from typing import List, Dict, Any
import pytz
import locale # Import locale

logger = logging.getLogger(__name__)

# --- Attempt to set locale globally for date formatting ---
try:
    # Try setting locale for Portuguese time formatting
    # Needs the locale to be installed on the system (e.g., pt_BR.UTF-8)
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    logger.info("Set locale to pt_BR.UTF-8 for date formatting.")
except locale.Error:
    logger.warning("Could not set locale to pt_BR.UTF-8. Date formatting may be in English.")
    # Fallback: try a common alias or just log warning
    try:
         locale.setlocale(locale.LC_TIME, 'pt_BR')
         logger.info("Set locale to pt_BR for date formatting.")
    except locale.Error:
         logger.warning("Could not set locale to pt_BR either. Date formatting will be default.")


client = OpenAI(api_key=Config.OPENAI_API_KEY)
state_manager = StateManager() # StateManager now uses SQLite


# --- API Interaction Functions (Keep as is, assuming get_access_token returns full response) ---
# ... (get_access_token, schedule_meeting functions here) ...
def get_access_token(doctor_id: int, clinic_id: int, api_key: str) -> Dict[str, Any] | None:
    if not Config.CRM_API_BASE_URL or not api_key or doctor_id is None or clinic_id is None:
        logger.error("Scheduling API base URL, API key, doctor ID, or clinic ID not configured for token request.")
        return None
    url = f"{Config.CRM_API_BASE_URL}/auth/one-time-token/"
    headers = { 'X-API-KEY': api_key, 'Content-Type': 'application/json', }
    payload = { "doctor_id": doctor_id, "clinic_id": clinic_id }
    logger.info(f"Attempting to fetch token and availability from {url} with payload {payload}")
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        logger.info(f"Token/Availability API response status: {response.status_code}")
        response.raise_for_status()
        response_data = response.json()
        if 'access_token' not in response_data or 'appointments' not in response_data:
            logger.error("Token/Availability API response missing expected keys ('access_token' or 'appointments').")
            return None
        logger.info("Access token and availability data fetched successfully.")
        return response_data
    except requests.exceptions.RequestException as e:
        logger.error(f"[Error fetching token/availability] Request failed: {e}")
        if e.response is not None: logger.error(f"Response status: {e.response.status_code}, Response body: {e.response.text}")
        return None
    except json.JSONDecodeError: logger.error("[Error fetching token/availability] Failed to decode JSON response.") ; return None
    except ValueError as e: logger.error(f"[Error fetching token/availability] {e}") ; return None
    except Exception as e: logger.error(f"[Error fetching token/availability] An unexpected error occurred: {e}") ; return None

def schedule_meeting(access_token: str, name: str, phone: str, email: str, date: str, procedure_id: int, health_operator_id: int) -> Dict[str, Any] | None:
    if not Config.CRM_API_BASE_URL or not access_token:
        logger.error("Scheduling API base URL or access token missing for schedule request.")
        return None
    if not name or not phone or not email or not date or procedure_id is None or health_operator_id is None:
         logger.error(f"Missing required scheduling data: Name={name}, Phone={phone}, Email={email}, Date={date}, Procedure={procedure_id}, Operator={health_operator_id}")
         return None
    url = f"{Config.CRM_API_BASE_URL}/appointment/create/"
    headers = { 'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json', }
    payload = {
        "name": name, "phone": phone, "email": email,
        "procedure": procedure_id,
        "health_operator": health_operator_id,
        "date": date
    }
    logger.info(f"Attempting to schedule meeting with payload: {payload}")
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        logger.info(f"Schedule meeting API response status: {response.status_code}")
        response.raise_for_status()
        logger.info("Meeting scheduling API call successful.")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error scheduling meeting: Request failed: {e}")
        if e.response is not None:
             logger.error(f"Response status: {e.response.status_code}")
             try: logger.error(f"Response body JSON: {e.response.json()}")
             except json.JSONDecodeError: logger.error(f"Response body text: {e.response.text}")
        return None
    except json.JSONDecodeError: logger.error("Error scheduling meeting: Failed to decode JSON response.") ; return None
    except Exception as e: logger.error(f"Error scheduling meeting: An unexpected error occurred: {e}") ; return None


# --- Helper Functions (Fix strftime, Message Consolidation) ---

# parse_user_datetime (Keep as is)
def parse_user_datetime(datetime_str: str) -> datetime | None:
    if not datetime_str: return None
    try:
        parsed_dt = parse_datetime(datetime_str)
        now = datetime.now()
        if parsed_dt.date() == now.date() and parsed_dt.time() < now.time():
             if parsed_dt < now - timedelta(minutes=5):
                 logger.info(f"Parsed datetime {parsed_dt} is in the past. Assuming next occurrence tomorrow.")
                 parsed_dt = parsed_dt + timedelta(days=1)
        elif parsed_dt < now - timedelta(minutes=5):
             logger.warning(f"Parsed datetime {parsed_dt} is significantly in the past.")
        logger.info(f"Parsed user datetime '{datetime_str}' into datetime object: {parsed_dt}")
        return parsed_dt
    except ValueError as e: logger.error(f"Error parsing datetime string '{datetime_str}': {e}") ; return None
    except Exception as e: logger.error(f"An unexpected error occurred during datetime parsing: {e}") ; return None

# format_datetime_for_api (Keep as is, assuming locale is set globally)
def format_datetime_for_api(dt_object: datetime) -> str | None:
    """
    Formats a datetime object (assumed to be local time) into 'YYYY-MM-DDTHH:mm:ss.000Z' (UTC).
    Correctly handles timezone conversion using clinic's local timezone.
    Assumes locale is set globally for strftime if needed elsewhere.
    """
    try:
        # Use the local timezone (Adjust this to your clinic's timezone)
        local_tz = pytz.timezone('America/Sao_Paulo')
        # Make the naive datetime timezone aware in the local timezone
        dt_object_local = local_tz.localize(dt_object)
        # Convert the local datetime to UTC
        utc_dt_object = dt_object_local.astimezone(pytz.utc)

        # Format to YYYY-MM-DDTHH:mm:ss.000Z
        # Use utcfromtimestamp if starting from a timestamp, but here we have a datetime object
        formatted_str = utc_dt_object.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        logger.info(f"Formatted datetime object {dt_object} (Local assumed) to API string {formatted_str} (UTC)")
        return formatted_str

    except Exception as tz_e:
        logger.error(f"Error during timezone conversion and formatting for API: {tz_e}. Cannot format datetime correctly.")
        return None

# find_matching_appointment (Keep as is, assuming locale is set globally)
def find_matching_appointment(requested_dt: datetime, available_appointments: List[Dict[str, str]], tolerance_minutes: int = 5) -> datetime | None:
    if not requested_dt or not available_appointments: return None
    available_dts = []
    local_tz = pytz.timezone('America/Sao_Paulo') # *** ADJUST THIS ***

    for appt in available_appointments:
        try:
            appt_start_str = appt.get('start')
            if appt_start_str:
                appt_dt = parse_datetime(appt_start_str)

                # Assuming API times are UTC ('Z'), parse_datetime gives UTC-aware datetime.
                # Ensure consistency: make requested_dt timezone-aware (local) and compare with API's UTC times
                if appt_dt.tzinfo is None: appt_dt = pytz.utc.localize(appt_dt)

                # Convert requested_dt to UTC for consistent comparison
                if requested_dt.tzinfo is None:
                    requested_dt_aware_utc = local_tz.localize(requested_dt).astimezone(pytz.utc)
                else:
                    requested_dt_aware_utc = requested_dt.astimezone(pytz.utc)

                available_dts.append(appt_dt)
        except Exception as e:
            logger.warning(f"Could not parse available appointment time string '{appt.get('start')}': {e}")

    available_dts_utc = [dt.astimezone(pytz.utc) for dt in available_dts if dt.tzinfo is not None]

    for appt_dt_utc in available_dts_utc:
        time_difference = abs((appt_dt_utc - requested_dt_aware_utc).total_seconds())
        if time_difference <= tolerance_minutes * 60:
            logger.info(f"Matched requested UTC time {requested_dt_aware_utc} with available UTC slot {appt_dt_utc} within {tolerance_minutes} minutes tolerance.")
            # Find the original datetime object from the list to return
            original_appt_dt = next((dt for dt in available_dts if dt.astimezone(pytz.utc) == appt_dt_utc), None)
            return original_appt_dt # Return the exact datetime object from the available slot

    logger.info(f"No available appointment found matching requested UTC time {requested_dt_aware_utc} within {tolerance_minutes} minutes tolerance.")
    return None


# --- Tool Handler Implementations (Update success output for transfer tool) ---
# ... (handle_collect_scheduling_info, handle_schedule_meeting_with_dr_inae here) ...

def handle_collect_scheduling_info(user_id: str, name: str = None, email: str = None, phone: str = None, datetime: str = None):
    logger.info(f"User {user_id}: Assistant provided scheduling info: Name={name}, Email={email}, Phone={phone}, Datetime={datetime}")
    gathered_info = {}
    if name: gathered_info["name"] = name
    if email: gathered_info["email"] = email
    if phone: gathered_info["phone"] = phone
    if datetime: gathered_info["datetime"] = datetime
    if not gathered_info: return "Assistant attempted to collect info but provided no details."
    info_summary = ", ".join([f"{k}: {v}" for k, v in gathered_info.items()])
    return f"Acknowledged collection of scheduling info: {info_summary}. I will use this when scheduling if confirmed."

def handle_schedule_meeting_with_dr_inae(user_id: str, name: str, email: str, phone: str, datetime: str):
    logger.info(f"User {user_id}: Attempting to schedule meeting for Dr. Inaê with raw info: Name={name}, Email={email}, Phone={phone}, Datetime={datetime}")
    final_phone = phone if phone and phone.strip() else user_id
    final_name = name if name and name.strip() else final_phone
    if not final_name or not final_phone or not email or not email.strip():
        missing = []
        if not final_name: missing.append("name")
        if not final_phone: missing.append("phone")
        if not email or not email.strip(): missing.append("email")
        logger.error(f"User {user_id}: Missing required scheduling info after auto-picking. Missing: {', '.join(missing)}")
        return f"Error: Cannot schedule meeting. Missing required information: {', '.join(missing)}. Please provide your full name, phone number, and email address."
    if not all(isinstance(val, str) for val in [name, phone, email, datetime]) and datetime is not None:
         logger.error(f"User {user_id}: Received non-string inputs from Assistant. Name={type(name)}, Phone={type(phone)}, Email={type(email)}, Datetime={type(datetime)}")
         return "Error: Received invalid data formats. Please provide your information as text."
    if not Config.CRM_API_BASE_URL or not Config.CRM_API_KEY or Config.DOCTOR_ID is None or Config.CLINIC_ID is None or Config.PROCEDURE_ID is None or Config.HEALTH_OPERATOR_ID is None:
        logger.error(f"User {user_id}: CRM/Scheduling API details (URL, Key, Doctor/Clinic/Procedure/Operator IDs) not fully set or are invalid integers.")
        return "Error: The meeting scheduling system is not fully configured. Please contact HR directly."
    token_availability_data = get_access_token(Config.DOCTOR_ID, Config.CLINIC_ID, Config.CRM_API_KEY)
    if not token_availability_data:
        logger.error(f"User {user_id}: Failed to get access token or availability data.")
        return "Error: Could not get authorization or check availability for scheduling. Please try again."
    access_token = token_availability_data.get('access_token')
    logger.info(f"access token recived {access_token}")
    available_appointments = token_availability_data.get('appointments', [])
    if not access_token: logger.error(f"User {user_id}: Access token missing from availability response data."); return "Error: Could not get authorization token for scheduling."
    if not available_appointments: logger.warning(f"User {user_id}: No available appointment slots returned by the API."); return "Sorry, there are currently no available appointment slots with Dra. Inaê."
    requested_dt = parse_user_datetime(datetime)
    if not requested_dt:
        logger.error(f"User {user_id}: Failed to parse user's requested datetime string: {datetime}")
        return f"Error: Could not understand the requested date and time '{datetime}'. Please provide it in a clearer format (e.g., 'DD/MM/YYYY HH:mm')."
    matched_dt_object = find_matching_appointment(requested_dt, available_appointments)
    if not matched_dt_object:
        logger.warning(f"User {user_id}: User requested time '{datetime}' did not match any available slots.")
        available_dates_str = ", ".join(
            sorted(list(set(
                pytz.utc.localize(parse_datetime(appt['start'])).astimezone(pytz.timezone('America/Sao_Paulo')).strftime('%d/%m/%Y %H:%M')
                for appt in available_appointments if appt.get('start')
            )))
        )
        max_display_length = 300
        if len(available_dates_str) > max_display_length: available_dates_str = available_dates_str[:max_display_length] + "..."
        return f"Desculpe, o horário '{datetime}' não está disponível. Por favor, escolha entre estes horários disponíveis: {available_dates_str}"
    date_time_iso = format_datetime_for_api(matched_dt_object)
    if not date_time_iso: logger.error(f"User {user_id}: Failed to format matched datetime object {matched_dt_object} for API."); return "Error: Could not format the chosen appointment time for scheduling."
    scheduling_result = schedule_meeting( access_token=access_token, name=final_name, phone=final_phone, email=email, date=date_time_iso, procedure_id=Config.PROCEDURE_ID, health_operator_id=Config.HEALTH_OPERATOR_ID )
    if scheduling_result:
        confirmation_details = scheduling_result.get("appointment_id", "N/A") # ADJUST THIS KEY NAME
        logger.info(f"User {user_id}: Meeting scheduled successfully. API Response: {scheduling_result}")
        try:
            scheduled_dt_local = matched_dt_object.astimezone(pytz.timezone('America/Sao_Paulo'))
            # Use locale-aware formatting
            scheduled_time_str = scheduled_dt_local.strftime('%d de %B de %Y, às %H:%M') # Example: "06 de junho de 2025, às 14:30"
        except Exception as format_e:
            logger.error(f"Error formatting final scheduled time for user message: {format_e}")
            scheduled_time_str = "o horário solicitado"
        return f"Sucesso: Sua consulta com a Dra. Inaê foi agendada com sucesso para {scheduled_time_str}. Um email de confirmação será enviado para {email}."
    else:
        logger.error(f"User {user_id}: Scheduling API call failed after trying to schedule.")
        return "Erro: Não foi possível agendar a consulta através do sistema. Por favor, tente novamente ou entre em contato com a clínica diretamente."


# --- MODIFIED handle_transfer_chat_to_whatsapp (Update success output) ---
def handle_transfer_chat_to_whatsapp(user_id: str, user_name: str = None, conversation_summary: str = None, message_to_user: str = None):
    transfer_number = Config.WHATSAPP_TRANSFER_NUMBER

    if not transfer_number or transfer_number == "ANOTHER_WHATSAPP_PHONE_NUMBER":
        logger.error(f"User {user_id}: WhatsApp transfer number not configured.")
        user_feedback = "Erro: A função de transferência de chat não está configurada. Por favor, entre em contato com a clínica diretamente."
        send_message(recipient_id=user_id, text=user_feedback)
        return "Error: Chat transfer functionality is not configured." # Return English code

    logger.info(f"User {user_id}: Attempting to transfer chat to number: {transfer_number}")

    # 1. Send a message to the user confirming the transfer
    user_transfer_message = message_to_user if message_to_user else (
        f"Ok, vou transferir você para um agente humano. Você pode entrar em contato diretamente pelo WhatsApp no número {transfer_number}. "
        "Por favor, forneça seu nome e um breve resumo do seu problema para que a equipe possa ajudar você mais rápido."
    )
    user_msg_success = send_message(recipient_id=user_id, text=user_transfer_message)

    if not user_msg_success:
        logger.error(f"User {user_id}: Failed to send transfer confirmation message to user.")

    # 2. Prepare and send the summary message to the transfer number
    summary_parts = [
        "--- Solicitação de Transferência de Chat ---",
        f"Usuário WhatsApp: {user_id}",
        f"Nome do Usuário (se conhecido): {user_name if user_name else 'N/A'}"
    ]
    if conversation_summary: summary_parts.append(f"\nResumo da Conversa:\n{conversation_summary}")
    else: summary_parts.append("\nNota: Nenhum resumo da conversa foi fornecido pelo bot."); logger.warning(f"User {user_id}: Assistant did not provide a conversation_summary for transfer.")
    agent_summary_message = "\n".join(summary_parts)
    agent_msg_success = send_message(recipient_id=transfer_number, text=agent_summary_message)

    # 3. Return the result back to the Assistant
    if user_msg_success and agent_msg_success:
        logger.info(f"User {user_id}: Both user confirmation and agent summary messages sent successfully.")
        # --- Use simple, unambiguous code for success ---
        return "TRANSFER_SUCCESS"
    elif user_msg_success and not agent_msg_success:
        logger.warning(f"User {user_id}: User notified, but failed to send summary to agent number ({transfer_number}).")
        return "TRANSFER_PARTIAL_FAILURE_AGENT"
    elif not user_msg_success and agent_msg_success:
         logger.error(f"User {user_id}: Failed to notify user, but summary sent to agent number ({transfer_number}).")
         return "TRANSFER_PARTIAL_FAILURE_USER"
    else:
        logger.error(f"User {user_id}: Failed to send both user notification and agent summary.")
        # --- Keep detailed error for full failure ---
        return "Error: Failed to initiate chat transfer. Neither user nor agent could be notified."


# cancel_existing_runs (Keep as is)
def cancel_existing_runs(thread_id: str):
    try:
        runs = client.beta.threads.runs.list(thread_id=thread_id, limit=10)
        active_runs = [ run for run in runs.data if run.status in ['queued', 'in_progress', 'cancelling', 'requires_action'] ]
        if not active_runs:
            logger.info(f"No active runs found on thread {thread_id}.")
            return False
        logger.warning(f"Found {len(active_runs)} active run(s) on thread {thread_id}. Attempting to cancel...")
        cancellation_attempted = False
        for run in active_runs:
            try:
                logger.warning(f"Cancelling run {run.id} with status {run.status} on thread {thread_id}.")
                client.beta.threads.runs.cancel(thread_id=thread_id, run_id=run.id)
                cancellation_attempted = True
            except Exception as e:
                # Log the specific error from OpenAI if available
                if hasattr(e, 'response') and e.response is not None and hasattr(e.response, 'json'):
                     try:
                         error_data = e.response.json()
                         logger.error(f"Failed to cancel run {run.id} (OpenAI Error): Code={error_data.get('error',{}).get('code')}, Message={error_data.get('error',{}).get('message')}")
                     except:
                          logger.error(f"Failed to cancel run {run.id}: {e}")
                else:
                     logger.error(f"Failed to cancel run {run.id}: {e}")
                # IMPORTANT: If cancellation fails because the run is already cancelling,
                # we must still return True to signal *an attempt was made* and allow
                # the retry logic in the caller to wait. Check the error message.
                if "Cannot cancel run with status 'cancelling'." in str(e):
                    logger.info(f"Run {run.id} was already in 'cancelling' status. Treating as successful cancellation attempt for retry logic.")
                    cancellation_attempted = True # Treat this specific error as a successful *attempt* for retries

        return cancellation_attempted
    except Exception as e:
        logger.error(f"Error listing or attempting to cancel runs for thread {thread_id}: {e}")
        return False

# execute_tool_call (Keep as is)
def execute_tool_call(user_id: str, function_name: str, arguments: dict):
    tool_functions = {
        "collect_scheduling_info": handle_collect_scheduling_info,
        "schedule_meeting_with_dr_inae": handle_schedule_meeting_with_dr_inae,
        "transfer_chat_to_whatsapp": handle_transfer_chat_to_whatsapp,
    }
    if function_name in tool_functions:
        try:
            result = tool_functions[function_name](user_id=user_id, **arguments)
            return str(result)
        except TypeError as e: logger.error(f"User {user_id}: Error calling tool function '{function_name}': Invalid arguments provided by Assistant. Details: {e}") ; return f"Error: Function '{function_name}' received incorrect arguments. Details: {e}"
        except Exception as e: logger.error(f"User {user_id}: Error executing tool function '{function_name}': {e}") ; return f"Error executing function '{function_name}': {e}"
    else: logger.warning(f"User {user_id}: Unknown tool function requested by Assistant: {function_name}"); return f"Error: Unknown function requested: {function_name}"


# --- MODIFIED run_assistant_with_tool_handling (Fix strftime, use locale) ---
def run_assistant_with_tool_handling(user_id: str, thread_id: str):
    if not Config.OPENAI_ASSISTANT_ID:
        logger.error("OPENAI_ASSISTANT_ID not set in config.")
        return None
    try:
        logger.info(f"Running assistant {Config.OPENAI_ASSISTANT_ID} on thread {thread_id} for user {user_id}...")

        # --- Dynamically add current date to instructions ---
        # Use the locale set globally at the top of the file
        try:
            # Get current date in the local timezone of the clinic
            sao_paulo_tz = pytz.timezone('America/Sao_Paulo') # *** ADJUST THIS ***
            now_local = datetime.now(sao_paulo_tz)
            # Format using locale-aware strftime
            current_date_str = f"Hoje é {now_local.strftime('%A, %d de %B de %Y')}." # No 'locale' arg needed here
            logger.info(f"Generated dynamic date string for instructions: {current_date_str}")

            # Fetch current base instructions from the Assistant
            assistant_obj = client.beta.assistants.retrieve(Config.OPENAI_ASSISTANT_ID)
            base_instructions = assistant_obj.instructions or ""

            # Optional: Remove the old hardcoded date line from base instructions if it exists
            base_instructions_lines = base_instructions.splitlines()
            filtered_lines = [line for line in base_instructions_lines if not line.strip().startswith('# ##Note Today\'s date is :')]
            base_instructions_cleaned = "\n".join(filtered_lines)

            # Prepend the dynamic date at the beginning of the instructions
            dynamic_instructions = f"{current_date_str}\n\n{base_instructions_cleaned}"
            # logger.debug(f"Full dynamic instructions:\n{dynamic_instructions}")

        except Exception as fetch_e:
             logger.error(f"Failed to generate dynamic instructions or fetch base instructions: {fetch_e}. Running with base instructions only.")
             dynamic_instructions = None # Use default instructions if fetching/generation fails


        # Create the run, overriding instructions if dynamically generated
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=Config.OPENAI_ASSISTANT_ID,
            instructions=dynamic_instructions if dynamic_instructions else None
        )
        logger.info(f"Created run: {run.id} with status: {run.status}")

        timeout_seconds = 120
        start_time = time.time()

        while run.status in ['queued', 'in_progress', 'cancelling', 'requires_action']:
            if time.time() - start_time > timeout_seconds:
                logger.warning(f"Run for user {user_id} timed out after {timeout_seconds} seconds. Status: {run.status}")
                try: client.beta.threads.runs.cancel(thread_id=thread_id, run_id=run.id)
                except Exception as cancel_e: logger.error(f"Failed to cancel run {run.id}: {cancel_e}")
                return None
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            logger.info(f"Polling run {run.id}. Status: {run.status}")

            if run.status == 'requires_action':
                logger.info(f"Run {run.id} requires action for user {user_id} (tool calling)...")
                tool_outputs = []
                try:
                    if run.required_action and run.required_action.type == 'submit_tool_outputs':
                         logger.info(f"Run {run.id} requested {len(run.required_action.submit_tool_outputs.tool_calls)} tool call(s).")
                         for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                             call_id = tool_call.id
                             function_name = tool_call.function.name
                             logger.info(f"Tool call requested: ID={call_id}, Name='{function_name}', Arguments='{tool_call.function.arguments}'")
                             try:
                                 arguments = json.loads(tool_call.function.arguments)
                             except json.JSONDecodeError as e:
                                 logger.error(f"User {user_id}: Error decoding tool call arguments for ID {call_id}: {e}")
                                 output = f"Error: Invalid JSON arguments for function {function_name}."
                                 tool_outputs.append({"tool_call_id": call_id, "output": output})
                                 continue
                             output = execute_tool_call(user_id, function_name, arguments)
                             logger.info(f"Tool call executed for ID={call_id}. Output: '{output}'")
                             tool_outputs.append({
                                 "tool_call_id": call_id,
                                 "output": output
                             })
                    logger.info(f"Submitting {len(tool_outputs)} tool outputs for run {run.id}...")
                    run = client.beta.threads.runs.submit_tool_outputs(
                        thread_id=thread_id,
                        run_id=run.id,
                        tool_outputs=tool_outputs
                    )
                    logger.info(f"Tool outputs submitted for run {run.id}. New run status: {run.status}")
                except Exception as tool_handling_e:
                    logger.error(f"User {user_id}: An error occurred during tool call handling for run {run.id}: {tool_handling_e}")
                    return None
            elif run.status in ['queued', 'in_progress', 'cancelling']: # Include cancelling here to keep polling if cancellation is pending
                 pass
            elif run.status in ['completed', 'failed', 'expired']:
                 logger.info(f"Run {run.id} reached terminal status: {run.status}")
                 if run.status == 'failed' and run.last_error:
                     logger.error(f"Run {run.id} failed. Error: {run.last_error.code} - {run.last_error.message}")
                 break # Break the loop on terminal statuses

        # Exit the loop. Check the final status.
        if run.status == 'completed':
            logger.info(f"Run {run.id} completed successfully for user {user_id}.")
            return run
        else:
            logger.warning(f"Run {run.id} ended with non-completed status for user {user_id}: {run.status}")
            if run.last_error:
                 logger.error(f"Run {run.id} Last Error Details: {run.last_error.code} - {run.last_error.message}")
            return None


    except Exception as e:
        logger.error(f"User {user_id}: An error occurred creating or polling run: {e}")
        # This catch block is for errors BEFORE/DURING polling setup or initial create.
        # If a run was successfully created, it should be handled by the loop's final check.
        # If an error happens here (e.g., Thread locked on initial create), we need a retry.
        logger.error(f"Initial run creation/polling failed for user {user_id}. Error: {e}")
        # This initial creation failure is often due to a thread lock from a previous,
        # possibly cancelled, run. Implement retry logic here.
        return None # Indicate failure, rely on retry in caller if implemented

# get_assistant_response (Add message consolidation)
def get_assistant_response(thread_id: str, run_id: str) -> List[str]:
    """
    Retrieves the content of the *latest* assistant message for a specific run.
    Returns a list containing a single string (the message content), or an empty list.
    """
    try:
        # List messages in descending order (newest first)
        messages = client.beta.threads.messages.list(
          thread_id=thread_id,
          order="desc",
          limit=5 # We only need to check a few recent messages to find the latest one from this run
        )

        # Iterate through messages from newest to oldest
        for msg in messages.data:
            # Find the first message that belongs to THIS run and is from the assistant
            if msg.role == 'assistant' and msg.run_id == run_id:
                # We found the latest assistant message created by this run.
                # Extract its text content.
                text_content = "".join([
                    block.text.value for block in msg.content if block.type == 'text'
                ])
                if text_content:
                    logger.info(f"Retrieved latest assistant response for run {run_id}: {text_content[:100]}...") # Log snippet
                    return [text_content] # Return a list containing ONLY this message (as a single string)

        # If the loop finishes without finding any assistant message for this run
        logger.warning(f"No assistant messages found for run {run_id}.")
        return []

    except Exception as e:
        logger.error(f"Error retrieving latest message from thread {thread_id} for run {run_id}: {e}")
        return []

# get_or_create_thread (Keep as is)
def get_or_create_thread(user_id):
    thread_id = state_manager.get_thread_id(user_id) # Uses persistent state now
    if not thread_id:
        logger.info(f"No thread found for user {user_id}. Creating a new one.")
        try:
            thread = client.beta.threads.create()
            thread_id = thread.id
            state_manager.set_thread_id(user_id, thread_id) # Saves to persistent state
            logger.info(f"New thread created: {thread_id}")
        except Exception as e:
            logger.error(f"Error creating thread: {e}")
            return None
    else:
         logger.info(f"Using existing thread {thread_id} for user {user_id}.")
    return thread_id

# add_message_to_thread (Keep as is)
def add_message_to_thread(thread_id, content):
    try:
        message = client.beta.threads.messages.create(
          thread_id=thread_id, role="user", content=content,
        )
        logger.info(f"Message added to thread {thread_id}: {message.id}")
        return message
    except Exception as e:
        # Log error details specifically for thread lock
        if hasattr(e, 'response') and e.response is not None and hasattr(e.response, 'json'):
             try:
                 error_data = e.response.json()
                 logger.error(f"Error adding message to thread {thread_id} (OpenAI Error): Code={error_data.get('error',{}).get('code')}, Message={error_data.get('error',{}).get('message')}")
             except:
                 logger.error(f"Error adding message to thread {thread_id}: {e}")
        else:
            logger.error(f"Error adding message to thread {thread_id}: {e}")
        raise e # Re-raise the error so the caller can handle retries