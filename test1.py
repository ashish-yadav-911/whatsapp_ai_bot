


from app.openai_assistant import handle_collect_scheduling_info, handle_schedule_meeting_with_dr_inae, schedule_meeting, get_access_token

import logging

#def schedule_meeting(access_token: str, name: str, phone: str, email: str, date_time_iso: str, procedure_id: int, health_operator_id: int) -> Dict[str, Any] | None:

API_KEY = '2422b02f-6139-4ee4-9a2a-fabe7eda2f08'
BASE_URL = 'https://hml.onlineclinic.com.br/api/v1'
DOCTOR_ID = 1498
CLINIC_ID = 297

# Get access token
data = get_access_token(DOCTOR_ID, CLINIC_ID, API_KEY)
#print(data)
token = data['access_token']
# Example patient info
name = "John Doe"
phone = "+1234567890"
email = "john.doe@example.com"
#date = "2025-08-7T14:00:00Z"
date = "2025-08-06T18:30:00.000Z"
procedure_id = 6170  # Replace with actual procedure ID
health_operator_id = 644  # Replace with actual health operator ID





schedule_meeting = schedule_meeting(access_token=token, name=name, phone=phone, email=email, date=date, procedure_id=procedure_id, health_operator_id=health_operator_id)

print("Meeting Status:", schedule_meeting)