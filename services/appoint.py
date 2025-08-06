# import os
# import json
# import logging
# import requests
# import regex
# from datetime import datetime
# from typing import Dict, List, Optional
# from requests.exceptions import RequestException
# from requests.adapters import HTTPAdapter
# from urllib3.util.retry import Retry
# from pydantic import BaseModel, Field, field_validator, validator

# # -----------------------------
# # Logging Configuration
# # -----------------------------
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
#     handlers=[logging.StreamHandler()]
# )
# logger = logging.getLogger(__name__)

# # -----------------------------
# # Helper to safely get env vars
# # -----------------------------
# def _get_env_int(var_name: str) -> int:
#     value = os.getenv(var_name)
#     if not value:
#         raise ValueError(f"Missing environment variable: {var_name}")
#     try:
#         return int(value)
#     except ValueError:
#         raise ValueError(f"{var_name} must be an integer, got '{value}'")

# # -----------------------------
# # Pydantic Models
# # -----------------------------
# class HealthOperator(BaseModel):
#     id: int
#     name: str

# class Procedure(BaseModel):
#     id: int
#     name: str
#     time: int
#     price: float
#     health_operators: List[HealthOperator]

# class AppointmentSlot(BaseModel):
#     start: datetime
#     end: datetime

#     @field_validator("end")
#     def end_after_start(cls, v, values):
#         if "start" in values and v <= values["start"]:
#             raise ValueError("End time must be after start time")
#         return v

# class WorkingHours(BaseModel):
#     weekday: int
#     start: str
#     end: str

# class OneTimeTokenResponse(BaseModel):
#     access_token: str
#     procedures: List[Procedure]
#     appointments: List[AppointmentSlot]
#     working_hours: List[WorkingHours]

# class ScheduleMeetingRequest(BaseModel):
#     name: str = Field(..., min_length=1, description="Full name of the patient")
#     email: str = Field(..., pattern=r'^[^@\s]+@[^@\s]+\.[^@\s]+$', description="Email address of the patient")
#     phone: str = Field(..., min_length=8, description="Phone number of the patient")
#     datetime: str = Field(..., description="ISO format datetime for the appointment")
#     procedure_id: int = Field(default=6170, description="ID of the procedure to schedule")
#     health_operator_id: int = Field(default=644, description="ID of the health operator")

#     @field_validator('datetime')
#     def validate_datetime(cls, v):
#         try:
#             datetime.fromisoformat(v)
#         except ValueError:
#             raise ValueError("Datetime must be in ISO format (e.g., '2025-05-15T12:00:00')")
#         return v

# # -----------------------------
# # Main API Client
# # -----------------------------
# class OnlineClinicAPI:
#     def __init__(
#         self,
#         base_url: str = None,
#         api_key: str = "2422b02f-6139-4ee4-9a2a-fabe7eda2f08",
#         doctor_id: int = None,
#         clinic_id: int = None,
#         timeout: int = 30
#     ):
#         doctor_id=1498
#         clinic_id=297
#         self.base_url = base_url or os.getenv('ONLINE_CLINIC_BASE_URL',"https://hml.onlineclinic.com.br/api/v1")
#         self.api_key = api_key or os.getenv('ONLINE_CLINIC_API_KEY',"2422b02f-6139-4ee4-9a2a-fabe7eda2f08")
#         self.doctor_id = doctor_id or 1498
#         self.clinic_id = clinic_id or 297
#         self.timeout = timeout

#         if not all([self.base_url, self.api_key, self.doctor_id, self.clinic_id]):
#             raise ValueError("Missing required environment variables or constructor parameters.")

#         self.session = requests.Session()
#         self.session.headers.update({
#             "X-API-KEY": self.api_key,
#             "Content-Type": "application/json"
#         })

#         # Add retry logic
#         retries = Retry(total=3, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
#         adapter = HTTPAdapter(max_retries=retries)
#         self.session.mount("http://", adapter)
#         self.session.mount("https://", adapter)

#     def _handle_response(self, response: requests.Response) -> Dict:
#         try:
#             response.raise_for_status()
#             return response.json()
#         except json.JSONDecodeError as e:
#             logger.exception(f"JSON decode error")
#             raise ValueError(f"Invalid JSON response: {response.text}")
#         except RequestException as e:
#             logger.exception("Request failed")
#             raise

#     def get_one_time_token(self) -> OneTimeTokenResponse:
#         url = f"{self.base_url}/auth/one-time-token/"
#         logger.info(f"Requesting one-time token for doctor {self.doctor_id} at clinic {self.clinic_id} with url {url}, api_key {self.api_key}")
#         payload = {
#             "doctor_id": self.doctor_id,
#             "clinic_id": self.clinic_id
#         }

#         logger.info(f"Payload: {payload}")

#         try:
#             response = self.session.post(
#                 url,
#                 json=payload,
#                 timeout=self.timeout
#             )
#             data = self._handle_response(response)
#             return OneTimeTokenResponse(**data)
#         except Exception as e:
#             logger.exception("Failed to get one-time token")
#             raise

#     def schedule_appointment(self, request: ScheduleMeetingRequest) -> Dict:
#         token_response = self.get_one_time_token()

#         url = f"{self.base_url}/scheduler/appointments/"
#         headers = {
#             "Authorization": f"Bearer {token_response.access_token}",
#             "Content-Type": "application/json"
#         }

#         payload = {
#             "patient_name": request.name,
#             "patient_email": request.email,
#             "patient_phone": request.phone,
#             "start": request.datetime,
#             "procedure_id": request.procedure_id,
#             "health_operator_id": request.health_operator_id,
#             "doctor_id": self.doctor_id,
#             "clinic_id": self.clinic_id
#         }

#         try:
#             response = self.session.post(
#                 url,
#                 json=payload,
#                 headers=headers,
#                 timeout=self.timeout
#             )
#             return self._handle_response(response)
#         except Exception as e:
#             logger.exception("Failed to schedule appointment")
#             raise

# # -----------------------------
# # Helper for OpenAI Tool Call
# # -----------------------------
# def schedule_meeting_with_dr_inae(
#     name: str,
#     email: str,
#     phone: str,
#     datetime: str,
#     procedure_id: int = 6170,
#     health_operator_id: int = 644
# ) -> Dict:
#     """
#     Schedules a meeting with Dr. Inae using the Online Clinic API.
#     """
#     try:
#         request = ScheduleMeetingRequest(
#             name=name,
#             email=email,
#             phone=phone,
#             datetime=datetime,
#             procedure_id=procedure_id,
#             health_operator_id=health_operator_id
#         )

#         api = OnlineClinicAPI()
#         result = api.schedule_appointment(request)

#         logger.info(f"Successfully scheduled appointment: {result}")
#         return {
#             "status": "success",
#             "data": result,
#             "message": "Appointment scheduled successfully"
#         }
#     except Exception as e:
#         logger.error(f"Error scheduling appointment: {e}", exc_info=True)
#         return {
#             "status": "error",
#             "message": str(e),
#             "error_type": e.__class__.__name__
#         }

# # -----------------------------
# # CLI for Manual Testing
# # -----------------------------
# if __name__ == "__main__":
#     result = schedule_meeting_with_dr_inae(
#         name="John Doe",
#         email="john.doe@example.com",
#         phone="+5511999999999",
#         datetime="2025-07-18T14:00:00"
#     )
#     print(json.dumps(result, indent=2, ensure_ascii=False))








# import os
# import json
# import logging
# import requests
# from datetime import datetime
# from typing import List, Dict
# from requests.exceptions import RequestException
# from requests.adapters import HTTPAdapter
# from urllib3.util.retry import Retry

# # Logging setup
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
#     handlers=[logging.StreamHandler()]
# )
# logger = logging.getLogger(__name__)


# # --- Data Models (Simple) ---

# class HealthOperator:
#     def __init__(self, data: Dict):
#         self.id = data.get("id")
#         self.name = data.get("name")


# class Procedure:
#     def __init__(self, data: Dict):
#         self.id = data.get("id")
#         self.name = data.get("name")
#         self.time = data.get("time")
#         self.price = data.get("price")
#         self.health_operators = [HealthOperator(op) for op in data.get("health_operators", [])]


# class AppointmentSlot:
#     def __init__(self, data: Dict):
#         self.start = datetime.fromisoformat(data["start"])
#         self.end = datetime.fromisoformat(data["end"])
#         if self.end <= self.start:
#             raise ValueError("End time must be after start time")


# class WorkingHours:
#     def __init__(self, data: Dict):
#         self.weekday = data.get("weekday")
#         self.start = data.get("start")
#         self.end = data.get("end")


# class OneTimeTokenResponse:
#     def __init__(self, data: Dict):
#         self.access_token = data.get("access_token")
#         self.procedures = [Procedure(p) for p in data.get("procedures", [])]
#         self.appointments = [AppointmentSlot(a) for a in data.get("appointments", [])]
#         self.working_hours = [WorkingHours(w) for w in data.get("working_hours", [])]


# class ScheduleMeetingRequest:
#     def __init__(self, name, email, phone, datetime_str, procedure_id=6170, health_operator_id=644):
#         if not name:
#             raise ValueError("Name is required")
#         if "@" not in email:
#             raise ValueError("Invalid email format")
#         if len(phone) < 8:
#             raise ValueError("Phone number too short")
#         try:
#             datetime.fromisoformat(datetime_str)
#         except ValueError:
#             raise ValueError("Invalid ISO datetime format")

#         self.name = name
#         self.email = email
#         self.phone = phone
#         self.datetime = datetime_str
#         self.procedure_id = procedure_id
#         self.health_operator_id = health_operator_id


# # --- API Client ---

# class OnlineClinicAPI:
#     def __init__(
#         self,
#         base_url=None,
#         api_key=None,
#         doctor_id=None,
#         clinic_id=None,
#         timeout=30
#     ):
#         self.base_url = base_url or os.getenv('ONLINE_CLINIC_BASE_URL', "https://hml.onlineclinic.com.br/api/v1")
#         self.api_key = api_key or os.getenv('ONLINE_CLINIC_API_KEY', "2422b02f-6139-4ee4-9a2a-fabe7eda2f08")
#         self.doctor_id = doctor_id or 1498
#         self.clinic_id = clinic_id or 297
#         self.timeout = timeout

#         self.session = requests.Session()
#         self.session.headers.update({
#             "X-API-KEY": self.api_key,
#             "Content-Type": "application/json"
#         })

#         retries = Retry(total=3, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
#         adapter = HTTPAdapter(max_retries=retries)
#         self.session.mount("http://", adapter)
#         self.session.mount("https://", adapter)

#     def _handle_response(self, response: requests.Response) -> Dict:
#         try:
#             response.raise_for_status()
#             return response.json()
#         except json.JSONDecodeError:
#             logger.exception("JSON decode error")
#             raise ValueError("Invalid JSON response")
#         except RequestException:
#             logger.exception("Request failed")
#             raise

#     def get_one_time_token(self) -> OneTimeTokenResponse:
#         url = f"{self.base_url}/auth/one-time-token/"
#         payload = {"doctor_id": self.doctor_id, "clinic_id": self.clinic_id}

#         logger.info(f"Requesting token with payload: {payload}")
#         response = self.session.post(url, json=payload, timeout=self.timeout)
#         data = self._handle_response(response)
#         return OneTimeTokenResponse(data)

#     def schedule_appointment(self, request: ScheduleMeetingRequest) -> Dict:
#         token_response = self.get_one_time_token()
#         logger.info(f"Received token: {token_response.access_token}")
#         url = f"https://hml.onlineclinic.com.br/api/v1/appointment/create/"

#         headers = {
#             "Authorization": f"Bearer {token_response.access_token}",
#             "Content-Type": "application/json"
#         }

#         payload = {
#             "patient_name": request.name,
#             "patient_email": request.email,
#             "patient_phone": request.phone,
#             "start": request.datetime,
#             "procedure_id": request.procedure_id,
#             "health_operator_id": request.health_operator_id,
#             "doctor_id": self.doctor_id,
#             "clinic_id": self.clinic_id
#         }
#         logger.info(f"POST {url}")
#         logger.info(f"Headers: {headers}")
#         logger.info(f"Payload: {json.dumps(payload, indent=2)}")

#         response = self.session.post(url, json=payload, headers=headers, timeout=self.timeout)
#         return self._handle_response(response)


# # --- Main Tool Call ---

# def schedule_meeting_with_dr_inae(name, email, phone, datetime, procedure_id=6170, health_operator_id=644):
#     try:
#         request = ScheduleMeetingRequest(name, email, phone, datetime, procedure_id, health_operator_id)
#         logger.info(f"Scheduling appointment with Dr. Inae: {request}, name={name}, email={email}, phone={phone}, datetime={datetime}, procedure_id={procedure_id}, health_operator_id={health_operator_id}")
#         api = OnlineClinicAPI()
#         result = api.schedule_appointment(request)
#         return {
#             "status": "success",
#             "data": result,
#             "message": "Appointment scheduled successfully"
#         }
#     except Exception as e:
#         logger.error(f"Error scheduling appointment: {e}", exc_info=True)
#         return {
#             "status": "error",
#             "message": str(e),
#             "error_type": e.__class__.__name__
#         }


# # --- CLI Testing ---

# if __name__ == "__main__":
#     result = schedule_meeting_with_dr_inae(
#         name="John Doe",
#         email="john.doe@example.com",
#         phone="+5511999999999",
#         datetime="2025-07-18T14:00:00"
#     )
#     print(json.dumps(result, indent=2, ensure_ascii=False))

















import os
import json
import logging
import requests
from datetime import datetime
from typing import List, Dict
from requests.exceptions import RequestException
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from zoneinfo import ZoneInfo  # Requires Python 3.9+

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


# --- Data Models (Simple) ---

class HealthOperator:
    def __init__(self, data: Dict):
        self.id = data.get("id")
        self.name = data.get("name")


class Procedure:
    def __init__(self, data: Dict):
        self.id = data.get("id")
        self.name = data.get("name")
        self.time = data.get("time")
        self.price = data.get("price")
        self.health_operators = [HealthOperator(op) for op in data.get("health_operators", [])]


class AppointmentSlot:
    def __init__(self, data: Dict):
        self.start = datetime.fromisoformat(data["start"])
        self.end = datetime.fromisoformat(data["end"])
        if self.end <= self.start:
            raise ValueError("End time must be after start time")


class WorkingHours:
    def __init__(self, data: Dict):
        self.weekday = data.get("weekday")
        self.start = data.get("start")
        self.end = data.get("end")


class OneTimeTokenResponse:
    def __init__(self, data: Dict):
        self.access_token = data.get("access_token")
        self.procedures = [Procedure(p) for p in data.get("procedures", [])]
        self.appointments = [AppointmentSlot(a) for a in data.get("appointments", [])]
        self.working_hours = [WorkingHours(w) for w in data.get("working_hours", [])]


class ScheduleMeetingRequest:
    def __init__(self, name, email, phone, datetime_str, procedure_id=6170, health_operator_id=644):
        if not name:
            raise ValueError("Name is required")
        if "@" not in email:
            raise ValueError("Invalid email format")
        if len(phone) < 8:
            raise ValueError("Phone number too short")

        try:
            # Parse and set timezone to Brazil if naive
            dt = datetime.fromisoformat(datetime_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=ZoneInfo("America/Sao_Paulo"))
            self.datetime_obj = dt
            self.datetime = dt.isoformat()
        except Exception as e:
            raise ValueError(f"Invalid datetime format or timezone issue: {e}")

        self.name = name
        self.email = email
        self.phone = phone
        self.procedure_id = procedure_id
        self.health_operator_id = health_operator_id


# --- API Client ---

class OnlineClinicAPI:
    def __init__(
        self,
        base_url=None,
        api_key=None,
        doctor_id=None,
        clinic_id=None,
        timeout=30
    ):
        self.base_url = base_url or os.getenv('ONLINE_CLINIC_BASE_URL', "https://hml.onlineclinic.com.br/api/v1")
        self.api_key = api_key or os.getenv('ONLINE_CLINIC_API_KEY', "2422b02f-6139-4ee4-9a2a-fabe7eda2f08")
        self.doctor_id = doctor_id or 1498
        self.clinic_id = clinic_id or 297
        self.timeout = timeout

        self.session = requests.Session()
        self.session.headers.update({
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        })

        retries = Retry(total=3, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _handle_response(self, response: requests.Response) -> Dict:
        try:
            #response.raise_for_status()
            return response.json()
        except json.JSONDecodeError:
            logger.exception("JSON decode error")
            raise ValueError("Invalid JSON response")
        except RequestException:
            logger.exception("Request failed")
            raise

    def get_one_time_token(self) -> OneTimeTokenResponse:
        url = f"{self.base_url}/auth/one-time-token/"
        payload = {"doctor_id": self.doctor_id, "clinic_id": self.clinic_id}

        logger.info(f"Requesting token with payload: {payload}")
        response = self.session.post(url, json=payload, timeout=self.timeout)
        data = self._handle_response(response)
        return OneTimeTokenResponse(data)

    def schedule_appointment(self, request: ScheduleMeetingRequest) -> Dict:
        token_response = self.get_one_time_token()
        logger.info(f"Received token: {token_response.access_token}")
        url = f"https://hml.onlineclinic.com.br/api/v1/appointment/create/"

        headers = {
            "Authorization": f"Bearer {token_response.access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "patient_name": request.name,
            "patient_email": request.email,
            "patient_phone": request.phone,
            "start": request.datetime,  # timezone-aware ISO string
            "procedure_id": request.procedure_id,
            "health_operator_id": request.health_operator_id,
            "doctor_id": self.doctor_id,
            "clinic_id": self.clinic_id
        }
        logger.info(f"POST {url}")
        logger.info(f"Headers: {headers}")
        logger.info(f"Payload: {json.dumps(payload, indent=2)}")

        response = self.session.post(url, json=payload, headers=headers, timeout=self.timeout)
        
        return self._handle_response(response)


# --- Main Tool Call ---

def schedule_meeting_with_dr_inae(name, email, phone, datetime, procedure_id=6170, health_operator_id=644):
    try:
        request = ScheduleMeetingRequest(name, email, phone, datetime, procedure_id, health_operator_id)
        logger.info(f"Scheduling appointment with Dr. Inae: {request}, name={name}, email={email}, phone={phone}, datetime={datetime}, procedure_id={procedure_id}, health_operator_id={health_operator_id}")
        api = OnlineClinicAPI()
        result = api.schedule_appointment(request)
        return {
            "status": "success",
            "data": result,
            "message": "Appointment scheduled successfully"
        }
    except Exception as e:
        logger.error(f"Error scheduling appointment: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "error_type": e.__class__.__name__
        }


# --- CLI Testing ---

if __name__ == "__main__":
    result = schedule_meeting_with_dr_inae(
        name="John Doe",
        email="john.doe@example.com",
        phone="+5511999999999",
        datetime="2025-07-18T14:00:00"  # assumed to be Brazil time if no timezone
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
