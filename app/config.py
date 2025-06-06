import os
from dotenv import load_dotenv
import logging

# --- Step 1: Load environment variables FIRST ---
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_success = load_dotenv(dotenv_path=dotenv_path)

# --- Step 2: Define the Config class, reading from os.environ ---
class Config:
    DEBUG = os.environ.get('FLASK_DEBUG') or True
    PORT = os.environ.get('PORT') or 4000

    LOG_LEVEL_STR = os.environ.get('LOG_LEVEL', 'INFO').upper()

    # OpenAI Config
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_ASSISTANT_ID = os.environ.get('OPENAI_ASSISTANT_ID')

    # WhatsApp Config
    WHATSAPP_TOKEN = os.environ.get('WHATSAPP_TOKEN')
    WHATSAPP_VERIFY_TOKEN = os.environ.get('WHATSAPP_VERIFY_TOKEN')
    WHATSAPP_PHONE_NUMBER_ID = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')

    # CRM/Scheduling API Config
    CRM_API_BASE_URL = os.environ.get('CRM_API_URL')
    CRM_API_KEY = os.environ.get('CRM_API_KEY')
    DOCTOR_ID_STR = os.environ.get('DOCTOR_ID')
    CLINIC_ID_STR = os.environ.get('CLINIC_ID')
    PROCEDURE_ID_STR = os.environ.get('PROCEDURE_ID') # New
    HEALTH_OPERATOR_ID_STR = os.environ.get('HEALTH_OPERATOR_ID') # New


    # Chat Transfer Config
    WHATSAPP_TRANSFER_NUMBER = os.environ.get('WHATSAPP_TRANSFER_NUMBER')

    # Logging & Error Notification Config
    LOG_FILE_PATH = os.environ.get('LOG_FILE_PATH', 'logs/app.log')
    LOG_RETENTION_DAYS_STR = os.environ.get('LOG_RETENTION_DAYS', '30')

    # Email Notification for Errors Config
    ENABLE_ERROR_EMAIL_STR = os.environ.get('ENABLE_ERROR_EMAIL', 'False').lower()
    EMAIL_HOST = os.environ.get('EMAIL_HOST')
    EMAIL_PORT_STR = os.environ.get('EMAIL_PORT')
    EMAIL_USE_TLS_STR = os.environ.get('EMAIL_USE_TLS', 'True').lower()
    EMAIL_USE_SSL_STR = os.environ.get('EMAIL_USE_SSL', 'False').lower()
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
    EMAIL_RECIPIENTS = os.environ.get('EMAIL_RECIPIENTS')
    EMAIL_SUBJECT_PREFIX = os.environ.get('EMAIL_SUBJECT_PREFIX', "[WhatsApp Bot Error]")


    # Attributes to hold converted types (int, bool, logging level constant)
    DOCTOR_ID = None
    CLINIC_ID = None
    PROCEDURE_ID = None # Converted
    HEALTH_OPERATOR_ID = None # Converted
    LOG_LEVEL = logging.INFO
    LOG_RETENTION_DAYS = 30
    ENABLE_ERROR_EMAIL = False
    EMAIL_PORT = None
    EMAIL_USE_TLS = True
    EMAIL_USE_SSL = False


    # --- Step 3: Add validation checks ---
    @staticmethod
    def validate_config():
         # Convert string IDs to integers
         try:
             Config.DOCTOR_ID = int(Config.DOCTOR_ID_STR) if Config.DOCTOR_ID_STR else None
         except ValueError:
             print("Warning: DOCTOR_ID in .env is not a valid integer. Scheduling may fail.")
             Config.DOCTOR_ID = None

         try:
             Config.CLINIC_ID = int(Config.CLINIC_ID_STR) if Config.CLINIC_ID_STR else None
         except ValueError:
             print("Warning: CLINIC_ID in .env is not a valid integer. Scheduling may fail.")
             Config.CLINIC_ID = None

         try: # New ID conversion
             Config.PROCEDURE_ID = int(Config.PROCEDURE_ID_STR) if Config.PROCEDURE_ID_STR else None
         except ValueError:
             print("Warning: PROCEDURE_ID in .env is not a valid integer. Scheduling may fail.")
             Config.PROCEDURE_ID = None

         try: # New ID conversion
             Config.HEALTH_OPERATOR_ID = int(Config.HEALTH_OPERATOR_ID_STR) if Config.HEALTH_OPERATOR_ID_STR else None
         except ValueError:
             print("Warning: HEALTH_OPERATOR_ID in .env is not a valid integer. Scheduling may fail.")
             Config.HEALTH_OPERATOR_ID = None


         # Convert LOG_LEVEL string to logging constant
         log_levels = { 'DEBUG': logging.DEBUG, 'INFO': logging.INFO, 'WARNING': logging.WARNING, 'ERROR': logging.ERROR, 'CRITICAL': logging.CRITICAL }
         Config.LOG_LEVEL = log_levels.get(Config.LOG_LEVEL_STR, logging.INFO)
         if Config.LOG_LEVEL_STR not in log_levels:
             print(f"Warning: Invalid LOG_LEVEL '{Config.LOG_LEVEL_STR}' in .env. Defaulting to INFO.")

         # Convert LOG_RETENTION_DAYS string to integer
         try:
             Config.LOG_RETENTION_DAYS = int(Config.LOG_RETENTION_DAYS_STR)
             if Config.LOG_RETENTION_DAYS <= 0:
                 print(f"Warning: LOG_RETENTION_DAYS '{Config.LOG_RETENTION_DAYS_STR}' must be positive. Defaulting to 30.")
                 Config.LOG_RETENTION_DAYS = 30
         except ValueError:
             print(f"Warning: Invalid LOG_RETENTION_DAYS '{Config.LOG_RETENTION_DAYS_STR}' in .env. Defaulting to 30.")
             Config.LOG_RETENTION_DAYS = 30

         # Convert boolean strings to booleans
         Config.ENABLE_ERROR_EMAIL = Config.ENABLE_ERROR_EMAIL_STR == 'true'
         Config.EMAIL_USE_TLS = Config.EMAIL_USE_TLS_STR == 'true'
         Config.EMAIL_USE_SSL = Config.EMAIL_USE_SSL_STR == 'true'

         # Convert EMAIL_PORT string to integer
         try:
             Config.EMAIL_PORT = int(Config.EMAIL_PORT_STR) if Config.EMAIL_PORT_STR else None
         except ValueError:
             print(f"Warning: EMAIL_PORT '{Config.EMAIL_PORT_STR}' in .env is not a valid integer. Email logging may fail.")
             Config.EMAIL_PORT = None


         # --- Perform Core Validation ---
         if not Config.OPENAI_API_KEY:
             raise ValueError("OPENAI_API_KEY not set in .env")

         if not Config.WHATSAPP_TOKEN or not Config.WHATSAPP_VERIFY_TOKEN or not Config.WHATSAPP_PHONE_NUMBER_ID:
              print("Warning: WhatsApp API keys/tokens not fully set. Sending responses might fail.")

         if not Config.OPENAI_ASSISTANT_ID:
              print("Warning: OPENAI_ASSISTANT_ID not set. Run setup_assistant.py first.")

         # Validate scheduling config - now includes procedure and health_operator IDs
         if not Config.CRM_API_BASE_URL or not Config.CRM_API_KEY or Config.DOCTOR_ID is None or Config.CLINIC_ID is None or Config.PROCEDURE_ID is None or Config.HEALTH_OPERATOR_ID is None:
              print("Warning: CRM/Scheduling API details (URL, Key, Doctor/Clinic/Procedure/Operator IDs) not fully set or are invalid integers. Meeting scheduling will not work.")

         if not Config.WHATSAPP_TRANSFER_NUMBER:
              print("Warning: WhatsApp transfer number not set. Chat transfer will not work.")

         # Validate email config if enabled
         if Config.ENABLE_ERROR_EMAIL:
              recipients = [r.strip() for r in (Config.EMAIL_RECIPIENTS or "").split(',') if r.strip()]
              if not all([Config.EMAIL_HOST, Config.EMAIL_PORT, Config.EMAIL_HOST_USER, Config.EMAIL_HOST_PASSWORD, recipients]):
                   print("Warning: Email notification is enabled but missing required configuration values (.env: EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_RECIPIENTS) or recipients list is empty.")
                   # Decide if invalid email config should disable email notifications
                   # Config.ENABLE_ERROR_EMAIL = False # Option to disable

# --- Step 4: Perform validation after the Config class is defined ---
Config.validate_config()

logger = logging.getLogger(__name__)
logger.info(f"Configuration loaded. Log level: {Config.LOG_LEVEL_STR} ({Config.LOG_LEVEL}), Email enabled: {Config.ENABLE_ERROR_EMAIL}")


