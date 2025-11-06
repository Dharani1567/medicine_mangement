# db_connection.py
import psycopg2

def get_db_connection():
    try:
        connection = psycopg2.connect(
            host="127.0.0.1",
            database="medical_db",
            user="postgres",
            password='Dharani@1567',
            port=5432
        )
        return connection
    except Exception as e:
        print("Database connection failed:", e)
        return None
