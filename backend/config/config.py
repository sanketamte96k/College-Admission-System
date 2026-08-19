import os
import sys
from urllib.parse import quote_plus
from datetime import timedelta

try:
    from dotenv import load_dotenv
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(backend_dir, ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)
    else:
        load_dotenv()
except Exception:
    pass


def get_database_uri():
    """
    Resolve and validate the database connection URI.
    Supports DATABASE_URL or individual DB_USER, DB_PASSWORD, DB_HOST, DB_NAME variables.
    Fails with a clear configuration error if required credentials are missing.
    """
    # 1. If DATABASE_URL is provided, use it directly
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        if database_url.startswith("mysql://"):
            return database_url.replace("mysql://", "mysql+pymysql://", 1)
        elif database_url.startswith("postgres://"):
            return database_url.replace("postgres://", "postgresql://", 1)
        return database_url

    # SQLite fallback for Render demo environments
    if os.getenv("RENDER"):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return f"sqlite:///{os.path.join(base_dir, 'college_admission.db')}"

    # Test environment fallback
    if os.getenv("FLASK_ENV") == "test" or os.getenv("TESTING") == "True" or (len(sys.argv) > 0 and "test" in os.path.basename(sys.argv[0])):
        return "sqlite:///:memory:"

    # 2. Build MySQL connection from environment variables
    db_user = os.environ.get("DB_USER", "root")
    db_password_raw = os.environ.get("DB_PASSWORD")
    if not db_password_raw:
        raise RuntimeError("Database configuration error: DB_PASSWORD must be configured. Please set the DB_PASSWORD environment variable or provide DATABASE_URL.")
    db_password = quote_plus(db_password_raw)
    db_host = os.environ.get("DB_HOST", "localhost")
    db_name = os.environ.get("DB_NAME", "college_admission_db")
    db_port = os.environ.get("DB_PORT", "3306")

    # 3. Safely encode the password with quote_plus
    return f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


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

    # Attendance Configuration
    ATTENDANCE_MIN_PERCENTAGE = float(os.getenv("ATTENDANCE_MIN_PERCENTAGE", 75.0))

    # ==========================
    # Database Configuration
    # ==========================

    DATABASE_URL = os.getenv("DATABASE_URL")
    DB_USER = os.getenv("DB_USER") or os.getenv("MYSQL_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD") or os.getenv("MYSQL_PASSWORD")
    DB_HOST = os.getenv("DB_HOST") or os.getenv("MYSQL_HOST")
    DB_NAME = os.getenv("DB_NAME") or os.getenv("MYSQL_DB")
    DB_PORT = os.getenv("DB_PORT") or os.getenv("MYSQL_PORT", "3306")

    SQLITE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'college_admission.db')}"
    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    if SQLALCHEMY_DATABASE_URI.startswith("sqlite"):
        SQLALCHEMY_ENGINE_OPTIONS = {}
    else:
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
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "False").lower() == "true" or int(os.getenv("MAIL_PORT", 587)) == 465

    MAIL_USERNAME = os.getenv(
        "MAIL_USERNAME",
        "admin@zeal.edu.in"
    )

    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")

    MAIL_DEFAULT_SENDER = (
        "Zeal College Admission System",
        os.getenv("MAIL_USERNAME", "admin@zeal.edu.in")
    )

    MAIL_SUPPRESS_SEND = (
        os.getenv("MAIL_SUPPRESS_SEND", "False").lower() == "true"
    )
    MAIL_TIMEOUT = int(os.getenv("MAIL_TIMEOUT", 10))


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