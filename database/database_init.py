import mysql.connector
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# Database credentials
db_host = os.getenv("HOST")
db_user = os.getenv("USER")
db_password = os.getenv("PASSWORD")
db_name = os.getenv("DATABASE_NAME")

def ensure_profile_name_column(username):
    """Ensure the Profile_Name column exists in user-specific tables."""
    conn = mysql.connector.connect(
        host=db_host, user=db_user, password=db_password, database=db_name
    )
    cursor = conn.cursor()

    tables = [
        f"{username}_Incomes",
        f"{username}_Expenses",
        f"{username}_Savings",
        f"{username}_Investments"
    ]

    def column_exists(table, column_name):
        try:
            cursor.execute(f"SHOW COLUMNS FROM `{table}` LIKE '{column_name}';")
            result = cursor.fetchone() is not None
            logging.debug(f"Checked if '{column_name}' exists in '{table}': {result}")
            return result
        except mysql.connector.Error as e:
            logging.error(f"Error checking column '{column_name}' in '{table}': {e}")
            return False

    for table in tables:
        if not column_exists(table, "Profile_Name"):
            try:
                command = f"ALTER TABLE `{table}` ADD COLUMN Profile_Name VARCHAR(255) NOT NULL;"
                cursor.execute(command)
                conn.commit()
                logging.info(f"Successfully executed: {command}")
            except mysql.connector.Error as e:
                logging.error(f"Error executing {command}: {e}")
        else:
            logging.info(f"Column 'Profile_Name' already exists in '{table}', skipping...")

    cursor.close()
    conn.close()