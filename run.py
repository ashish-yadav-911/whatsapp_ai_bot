from app import create_app
from app.config import Config
from app.log import setup_logging

setup_logging()

import logging
logger = logging.getLogger(__name__)
logger.info("Application starting...")

app = create_app()

if __name__ == '__main__':
    app.run(debug=Config.LOG_LEVEL, port=Config.PORT)