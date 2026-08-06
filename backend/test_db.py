import pymysql

try:
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="Sanket@123",
        database="college_admission_db",
        port=3306
    )

    print("✅ Connected Successfully!")

    conn.close()

except Exception as e:
    print("❌ Error:")
    print(e)