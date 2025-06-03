# from app.config import Config

# Config.load_env()

# v1=Config.VAR1
# v2=Config.VAR2

# v3=v1+v2
# print(f"v1: {v1}")
# print(f"v2: {v2}")
# print(f"v3: {v3}")


import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants (replace with actual values)
API_KEY = '2422b02f-6139-4ee4-9a2a-fabe7eda2f08'
BASE_URL = 'https://hml.onlineclinic.com.br/api/v1'
DOCTOR_ID = 1498
CLINIC_ID = 297


def get_access_token(doctor_id, clinic_id, api_key):
    """
    Gets a one-time access token using doctor and clinic ID.
    """
    url = f"{BASE_URL}/auth/one-time-token/"
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json',
    }
    payload = {
        "doctor_id": doctor_id,
        "clinic_id": clinic_id
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))  # CHANGED to POST
        print("Status code:", response.status_code)
        print("Response:", response.text)
        response.raise_for_status()

        token = response.json().get('access_token')  # Or adjust key name here
        if not token:
            raise ValueError("Access token not found in response.")
        return token
    except Exception as e:
        print(f"[Error fetching token] {e}")
        return None



def schedule_meeting(access_token, doctor_id, clinic_id, patient_id, start_time, end_time, description=""):
    """
    Schedules a meeting using the access token.
    """
    url = "https://hml.onlineclinic.com.br/api/v1/appointment/create/"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    payload = {
        "doctor_id": doctor_id,
        "clinic_id": clinic_id,
        "patient_id": patient_id,
        "start_time": start_time,
        "end_time": end_time,
        "description": description
    }

    logging.info("Scheduling meeting...")
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        logging.info("Meeting scheduled successfully.")
        return response.json()
    except Exception as e:
        logging.error(f"Error scheduling meeting: {e}")
        return None


# === Example usage ===
if __name__ == "__main__":
    logging.info("Starting script...")
    API_KEY = '2422b02f-6139-4ee4-9a2a-fabe7eda2f08'
    DOCTOR_ID = 1498
    CLINIC_ID = 297


    patient_id = 1234  # Replace with real patient ID
    start_time = "2025-05-15T14:00:00Z"
    end_time = "2025-05-15T14:30:00Z"
    description = "Routine check-up"

    token = get_access_token(DOCTOR_ID, CLINIC_ID, API_KEY)
    if token:
        logging.info("Access token obtained. Proceeding to schedule meeting...")
        result = schedule_meeting(token, DOCTOR_ID, CLINIC_ID, patient_id, start_time, end_time, description)
        if result:
            logging.info("Appointment scheduled successfully.")
            print("✅ Appointment scheduled successfully:")
            print(json.dumps(result, indent=2))
        else:
            logging.error("Failed to schedule appointment.")
            print("❌ Failed to schedule appointment.")
    else:
        logging.error("Could not retrieve access token.")
        print("❌ Could not retrieve access token.")
