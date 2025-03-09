from .database_init import *
import mysql.connector

def create_database():
    """Create the database if it does not exist."""
    logging.info("Attempting to create/check database...")
    try:
        with mysql.connector.connect(host=db_host, user=db_user, password=db_password) as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
                logging.info(f"Database `{db_name}` is ready.")
    except mysql.connector.Error as err:
        logging.error(f"Error creating database: {err}")


def create_user_table():
    """Create necessary tables inside the database."""
    logging.info("Checking/creating `User_Data` table...")
    try:
        with mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS User_Data (
                        Email VARCHAR(255) PRIMARY KEY,
                        User_Name VARCHAR(255) UNIQUE
                    )
                """)
                logging.info("Table `User_Data` is ready.")
    except mysql.connector.Error as err:
        logging.error(f"Error creating tables: {err}")

                

def insert_user(email, user_name):
    """Insert a new user into the User_Data table if not exists."""
    logging.info(f"Attempting to insert user `{email}` with table `{user_name}`...")
    try:
        with mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name) as conn:
            with conn.cursor() as cursor:
                cursor.execute("USE {}".format(db_name))

                cursor.execute(
                    "INSERT IGNORE INTO User_Data (Email, User_Name) VALUES (%s, %s)",
                    (email, user_name)
                )

                if cursor.rowcount > 0:
                    logging.info(f"User `{email}` inserted successfully.")
                    conn.commit()
                else:
                    logging.info(f"User `{email}` already exists, skipping insertion.")

    except mysql.connector.Error as err:
        logging.error(f"Error inserting user `{email}`: {err}")




def check_email_exists(email):
    """Check if a user email exists in the database."""
    logging.info(f"Checking if email `{email}` exists in database...")
    try:
        with mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(1) FROM User_Data WHERE Email = %s", (email,))  # ✅ FIXED
                result = cursor.fetchone()
                exists = result[0] > 0
                logging.info(f"Email `{email}` existence check: {exists}")
                return exists
    except mysql.connector.Error as err:
        logging.error(f"Error checking email `{email}` existence: {err}")
        return False

    
    

def get_username(email):
    """Retrieve the username for a given email from the User_Data table."""
    conn = None
    cursor = None  # ✅ Initialize cursor to None to avoid UnboundLocalError

    try:
        conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
        cursor = conn.cursor()

        cursor.execute("SELECT User_Name FROM User_Data WHERE Email = %s", (email,))
        result = cursor.fetchone()  # Fetch the first matching row

        if result:
            return result[0]  # Return the username
        else:
            logging.info(f"No username found for email `{email}`.")
            return None  # Return None if the email is not found

    except mysql.connector.Error as err:
        logging.error(f"Error retrieving username for `{email}`: {err}")
        return None  # Return None in case of an error

