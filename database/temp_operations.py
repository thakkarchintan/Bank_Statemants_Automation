import mysql.connector
from constant_variables import *

DB_CONFIG = {
    'host': HOST,
    'user': USER,
    'password': PASSWORD,
    'database': DATABASE
}

def create_connection():
    return mysql.connector.connect(**DB_CONFIG)

def insert_user(name, email):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO temp_users (name, email) VALUES (%s, %s)", (name, email))
        conn.commit()
    except mysql.connector.Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

def fetch_pending_users():
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, email FROM temp_users WHERE is_approved = FALSE")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users

def update_user_approval(user_id, approve=True):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE temp_users SET is_approved = %s WHERE id = %s",
        (approve, user_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

def delete_user(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM temp_users WHERE id = %s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()

def check_user_status(email):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT is_approved FROM temp_users WHERE email = %s", (email,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result  # Returns {'is_approved': True/False} if user exists, else None