import mysql.connector
import logging
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# Database credentials
db_host = os.getenv("HOST")
db_user = os.getenv("USER")
db_password = os.getenv("PASSWORD")
db_name = os.getenv("DATABASE_NAME")

# Connect to the database
conn = mysql.connector.connect(
    host=db_host,
    user=db_user,
    password=db_password,
    database=db_name
)
cursor = conn.cursor()

# List of tables to check
tables = ["Incomes", "Expenses", "Savings", "Investments"]

# Function to check if column exists
def column_exists(table, column_name):
    try:
        cursor.execute(f"SHOW COLUMNS FROM {table} LIKE '{column_name}';")
        result = cursor.fetchone() is not None
        logging.debug(f"Checked if '{column_name}' exists in '{table}': {result}")
        return result
    except mysql.connector.Error as e:
        logging.error(f"Error checking column '{column_name}' in '{table}': {e}")
        return False

# Add Profile_Name column only if it doesn’t exist
for table in tables:
    if not column_exists(table, "Profile_Name"):
        try:
            command = f"ALTER TABLE {table} ADD COLUMN Profile_Name VARCHAR(255) NOT NULL;"
            cursor.execute(command)
            conn.commit()
            logging.info(f"Successfully executed: {command}")
        except mysql.connector.Error as e:
            logging.error(f"Error executing {command}: {e}")
    else:
        logging.info(f"Column 'Profile_Name' already exists in {table}, skipping...")

# Close connection
cursor.close()
conn.close()