import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(app):
    """Configure application & error loggers with RotatingFileHandler"""
    log_dir = os.path.join(app.config["BASE_DIR"], "logs")
    os.makedirs(log_dir, exist_ok=True)

    app_log_path = os.path.join(log_dir, "app.log")
    error_log_path = os.path.join(log_dir, "error.log")

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )

    # General App Log Handler
    app_handler = RotatingFileHandler(app_log_path, maxBytes=10*1024*1024, backupCount=5)
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(formatter)

    # Error Log Handler
    error_handler = RotatingFileHandler(error_log_path, maxBytes=10*1024*1024, backupCount=5)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(app_handler)
    app.logger.addHandler(error_handler)

    app.logger.info("Zeal ERP System Logger initialized successfully.")
