import mysql.connector

def db_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="taskify_db"
        )
    except Exception as e:
        print(f"Error connecting to database: {e}")