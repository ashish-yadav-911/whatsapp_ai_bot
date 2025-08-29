import requests
import json
from app.config import Config
import logging

logger = logging.getLogger(__name__)

WHATSAPP_API_URL = "https://graph.facebook.com/v23.0" # Use current API version
#https://graph.facebook.com/v22.0/411874855341199/messages
def verify_webhook(request_args):
    """
    Handles webhook verification requests.
    """
    mode = request_args.get("hub.mode")
    token = request_args.get("hub.verify_token")
    challenge = request_args.get("hub.challenge")

    if mode == "subscribe" and token == Config.WHATSAPP_VERIFY_TOKEN:
        print("Webhook verified successfully!")
        return challenge, 200
    else:
        print("Webhook verification failed.")
        return "Verification failed", 403

# def send_message(recipient_id, text):
#     """
#     Sends a text message back to the WhatsApp user.
#     recipient_id is the user's phone number.
#     """
#     if not Config.WHATSAPP_TOKEN or not Config.WHATSAPP_PHONE_NUMBER_ID:
#          print("Warning: WhatsApp API keys/tokens not fully set. Cannot send message.")
#          return False

#     url = f"{WHATSAPP_API_URL}/{Config.WHATSAPP_PHONE_NUMBER_ID}/messages"
#     headers = {
#         "Authorization": f"Bearer {Config.WHATSAPP_TOKEN}",
#         "Content-Type": "application/json",
#     }
#     payload = {
#         "messaging_product": "whatsapp",
#         "to": recipient_id,
#         "type": "text",
#         "text": {
#             "body": text
#         }
#     }

#     try:
#         response = requests.post(url, headers=headers, data=json.dumps(payload))
#         response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
#         print(f"Message sent successfully to {recipient_id}")
#         return True
#     except requests.exceptions.RequestException as e:
#         print(f"Error sending message to {recipient_id}: {e}")
#         # You might want to log the response body for more details
#         # print(f"Response body: {response.text}")
#         return False



# def send_message(recipient_id, text):
#     """
#     Sends a WhatsApp message back to the user.
#     Tries free-form text first; if rejected (outside 24h window), falls back to a template.
#     """
#     if not Config.WHATSAPP_TOKEN or not Config.WHATSAPP_PHONE_NUMBER_ID:
#         print("Warning: WhatsApp API keys/tokens not fully set. Cannot send message.")
#         return False

#     url = f"{WHATSAPP_API_URL}/{Config.WHATSAPP_PHONE_NUMBER_ID}/messages"
#     headers = {
#         "Authorization": f"Bearer {Config.WHATSAPP_TOKEN}",
#         "Content-Type": "application/json",
#     }
#     logger.info(f"recipient_id is {recipient_id} and text is {text}")
#     # --- Try free text message first ---
#     payload = {
#         "messaging_product": "whatsapp",
#         "to": recipient_id,
#         "type": "text",
#         "text": {"body": text}
#     }

#     try:
#         response = requests.post(url, headers=headers, json=payload)
#         response.raise_for_status()
#         print(f"✅ Free text message sent to {recipient_id}")
#         return True

#     except requests.exceptions.HTTPError as e:
#         if response.status_code == 400:
#             print(f"⚠️ Free text rejected for {recipient_id}, falling back to template...")

#             # --- Fallback to template message ---
#             fallback_payload = {
#                 "messaging_product": "whatsapp",
#                 "to": recipient_id,
#                 "type": "template",
#                 "template": {
#                     "name": "hello_world",  # must be a pre-approved template
#                     "language": {"code": "en_US"}
#                 }
#             }
#             try:
#                 response = requests.post(url, headers=headers, json=fallback_payload)
#                 response.raise_for_status()
#                 print(f"✅ Template message sent to {recipient_id}")
#                 return True
#             except requests.exceptions.RequestException as e2:
#                 print(f"❌ Failed to send template message to {recipient_id}: {e2}")
#                 print(f"Response body: {response.text}")
#                 return False
#         else:
#             print(f"❌ HTTP error sending to {recipient_id}: {e}")
#             print(f"Response body: {response.text}")
#             return False

#     except requests.exceptions.RequestException as e:
#         print(f"❌ Request error sending message to {recipient_id}: {e}")
#         return False



def send_message(recipient_id, text):
    """
    Sends a text message back to the WhatsApp user.
    recipient_id is the user's phone number.
    """
    if not Config.WHATSAPP_TOKEN or not Config.WHATSAPP_PHONE_NUMBER_ID:
        print("Warning: WhatsApp API keys/tokens not fully set. Cannot send message.")
        return False

    url = f"{WHATSAPP_API_URL}/{Config.WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {Config.WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    text=str(text)
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "text",
        "text": {"body": text},
    }

    try:
        response = requests.post(url, headers=headers, json=payload)  # 👈 changed
        response.raise_for_status()
        print(f"✅ Message sent successfully to {recipient_id}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending message to {recipient_id}: {e}")
        if response is not None:
            print(f"Response body: {response.text}")
        return False