import requests
import json
from app.config import Config

WHATSAPP_API_URL = "https://graph.facebook.com/v22.0" # Use current API version
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
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "text",
        "text": {
            "body": text
        }
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        print(f"Message sent successfully to {recipient_id}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to {recipient_id}: {e}")
        # You might want to log the response body for more details
        # print(f"Response body: {response.text}")
        return False