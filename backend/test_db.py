import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

db_user = os.getenv("DB_USER") or os.getenv("MYSQL_USER", "root")
db_password = os.getenv("DB_PASSWORD") or os.getenv("MYSQL_PASSWORD")
db_host = os.getenv("DB_HOST") or os.getenv("MYSQL_HOST", "localhost")
db_name = os.getenv("DB_NAME") or os.getenv("MYSQL_DB", "college_admission_db")
db_port = int(os.getenv("DB_PORT") or os.getenv("MYSQL_PORT", "3306"))

if not db_password:
    print("❌ Error: DB_PASSWORD environment variable is not set.")
else:
    try:
        conn = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name,
            port=db_port
        )

        print("✅ Connected Successfully!")
        conn.close()

    except Exception as e:
        print("❌ Error:")
        print(e)