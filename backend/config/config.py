import os
from urllib.parse import quote_plus
from datetime import timedelta


class Config:
    """Base Configuration"""

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "zeal_college_production_erp_secret_2026"
    )

    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Uploads directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_FOLDER = os.getenv(
        "UPLOAD_FOLDER",
        os.path.join(BASE_DIR, "uploads")
    )
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    # ==========================
    # Database Configuration
    # ==========================

    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "Sanket@123")
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_DB = os.getenv("MYSQL_DB", "college_admission_db")
    MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")

    MYSQL_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{quote_plus(MYSQL_PASSWORD)}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    )

    SQLITE_URI = (
        f"sqlite:///{os.path.join(BASE_DIR, 'college_admission.db')}"
    )

    # Use SQLite on Render, MySQL locally
    if os.getenv("RENDER"):
        SQLALCHEMY_DATABASE_URI = SQLITE_URI
    else:
        SQLALCHEMY_DATABASE_URI = MYSQL_URI

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20
    }

    # ==========================
    # Mail Configuration
    # ==========================

    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").lower() == "true"

    MAIL_USERNAME = os.getenv(
        "MAIL_USERNAME",
        "admin@zeal.edu.in"
    )

    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")

    MAIL_DEFAULT_SENDER = (
        "Zeal College Admission System",
        "admin@zeal.edu.in"
    )

    MAIL_SUPPRESS_SEND = (
        os.getenv("MAIL_SUPPRESS_SEND", "False").lower() == "true"
    )


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {}
    MAIL_SUPPRESS_SEND = True


config_by_name = {
    "dev": DevelopmentConfig,
    "prod": ProductionConfig,
    "test": TestingConfig,
}