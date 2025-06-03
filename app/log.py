# import logging
# from logging.handlers import TimedRotatingFileHandler
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from datetime import datetime

# # Configure logging
# logger = logging.getLogger("RotatingLog")
# logger.setLevel(logging.ERROR)

# # Log rotation handler
# handler = TimedRotatingFileHandler("app.log", when="midnight", interval=1, backupCount=30)
# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
# logger.addHandler(handler)

# # Email notification function
# def send_error_email(subject, message):
#     sender_email = "your_email@example.com"
#     receiver_email = "receiver_email@example.com"
#     password = "your_email_password"

#     msg = MIMEMultipart()
#     msg['From'] = sender_email
#     msg['To'] = receiver_email
#     msg['Subject'] = subject

#     msg.attach(MIMEText(message, 'plain'))

#     try:
#         with smtplib.SMTP('smtp.example.com', 587) as server:
#             server.starttls()
#             server.login(sender_email, password)
#             server.sendmail(sender_email, receiver_email, msg.as_string())
#     except Exception as e:
#         logger.error(f"Failed to send email: {e}")

# # Example usage
# try:
#     # Simulate an error
#     1 / 0
# except Exception as e:
#     error_message = f"An error occurred: {e}"
#     logger.error(error_message)
#     send_error_email("Application Error", error_message)




import logging
from logging.handlers import TimedRotatingFileHandler, SMTPHandler
import os
from app.config import Config # Assuming Config is structured to be importable

# Ensure Config loads environment variables *before* we try to access them
# This is already handled by the structure we put in place in config.py
# Config.load_env() # No longer need this call here if config.py handles it on import

def setup_logging():
    """
    Configures the application's logging.
    Sets up console output, date-based file rotation with cleanup,
    and optional email notification for errors.
    """
    # Define the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(Config.LOG_LEVEL or logging.INFO) # Set overall minimum level

    # Clear existing handlers to prevent duplicate logs if called multiple times
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # --- Console Handler (for development/immediate visibility) ---
    console_handler = logging.StreamHandler()
    console_handler.setLevel(Config.LOG_LEVEL or logging.INFO) # Console logs at the overall level
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    # Log a message to confirm console handler is set up
    logger = logging.getLogger(__name__) # Get a logger for this module
    logger.info("Console logging configured.")


    # --- File Handler (Timed Rotating with Cleanup) ---
    log_file_path = Config.LOG_FILE_PATH
    if log_file_path:
        log_directory = os.path.dirname(log_file_path)
        # Create the log directory if it doesn't exist
        if log_directory and not os.path.exists(log_directory):
            try:
                os.makedirs(log_directory)
                logger.info(f"Created log directory: {log_directory}")
            except OSError as e:
                logger.error(f"Failed to create log directory {log_directory}: {e}. File logging may fail.")
                log_file_path = None # Disable file logging if dir creation fails

    if log_file_path:
        # Use 'midnight' to rotate daily
        # backupCount is the number of files to keep (plus the current one)
        # So backupCount=29 + current file = 30 days worth
        # Set backupCount based on LOG_RETENTION_DAYS - 1
        retention_days = Config.LOG_RETENTION_DAYS or 30
        backup_count = max(0, retention_days - 1) # Ensure it's not negative

        try:
            # when='midnight', interval=1 means rotate every day at midnight
            file_handler = TimedRotatingFileHandler(
                log_file_path,
                when='midnight',
                interval=1,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(Config.LOG_LEVEL or logging.INFO) # File logs at the overall level
            file_handler.setFormatter(formatter) # Use the same formatter
            root_logger.addHandler(file_handler)
            logger.info(f"File logging configured: {log_file_path} with {retention_days} days retention.")
        except Exception as e:
            logger.error(f"Failed to configure file logging to {log_file_path}: {e}")


    # --- Email Handler (for Errors) ---
    if Config.ENABLE_ERROR_EMAIL:
        # Basic validation for email config
        if not all([Config.EMAIL_HOST, Config.EMAIL_PORT, Config.EMAIL_HOST_USER, Config.EMAIL_HOST_PASSWORD, Config.EMAIL_RECIPIENTS]):
             logger.warning("Email notification is enabled but missing required configuration values in .env.")
        else:
            try:
                # Convert recipient string to a list
                recipients = [r.strip() for r in (Config.EMAIL_RECIPIENTS or "").split(',') if r.strip()]
                if not recipients:
                    logger.warning("Email notification enabled but no valid recipients specified in EMAIL_RECIPIENTS.")
                else:
                    # The SMTPHandler requires hostname, port, fromaddr, toaddrs, subject
                    # It also supports secure connections via secure=() or use_tls=True
                    # The subject includes the record's level name and the subject prefix
                    email_subject = f"{Config.EMAIL_SUBJECT_PREFIX or ''} %(levelname)s from Bot"

                    # The SMTPHandler message body is just the formatted log message by default
                    email_handler = SMTPHandler(
                        mailhost=(Config.EMAIL_HOST, Config.EMAIL_PORT), # mailhost can be a tuple for host and port
                        fromaddr=Config.EMAIL_HOST_USER,
                        toaddrs=recipients, # toaddrs must be a list or tuple
                        subject=email_subject,
                        credentials=(Config.EMAIL_HOST_USER, Config.EMAIL_HOST_PASSWORD), # for authentication
                        secure=() if Config.EMAIL_USE_TLS else None, # Use secure=() for TLS
                        # If using SSL (port 465), secure should be None and you might use SMTP_SSL instead of SMTP in handler
                        # Python's SMTPHandler doesn't directly support starttls=True like this,
                        # secure=() is the standard way for TLS.
                        # For SSL (port 465), you might need a custom handler or a different approach if SMTPHandler doesn't work.
                        # Standard practice is TLS on 587.
                    )
                    # Set the level for emails - only send ERROR and CRITICAL logs
                    email_handler.setLevel(logging.ERROR)
                    # Use a simple formatter for emails or the same one
                    email_handler.setFormatter(formatter) # Using the same formatter as files/console
                    root_logger.addHandler(email_handler)
                    logger.info(f"Email logging configured for ERROR level to {', '.join(recipients)}.")

            except Exception as e:
                 logger.error(f"Failed to configure email logging: {e}")


# Get a module-level logger here to use within log.py itself
logger = logging.getLogger(__name__)

# Example of how to use the logger elsewhere:
# import logging
# logger = logging.getLogger(__name__) # __name__ gets the current module name
# logger.info("This is an info message.")
# logger.error("This is an error message.")