import mysql.connector
import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join("home","ec2-user","app",".env"))

# MySQL database credentials
DATABASE_TYPE = os.getenv("DATABASE_TYPE")
DBAPI = os.getenv("DBAPI")
HOST = os.getenv("HOST")
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
DATABASE = os.getenv("DATABASE")
PORT = 3306

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD, 
        database=DATABASE
    )

# Initialize database and table if not exists
def initialize_db(table_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE}")
    cursor.execute(f"USE {DATABASE}")
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            Keyword VARCHAR(255) NOT NULL,
            Category VARCHAR(255) NOT NULL,
            Type VARCHAR(255) NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Function to add category
def add_category(keyword, category,type, table_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO {table_name} VALUES (%s, %s)", (keyword, category,type))
    conn.commit()
    conn.close()

# Function to delete a category
def delete_all(table_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {table_name};")
    conn.commit()
    conn.close()

def add_category_df(df,table_name):
    # Create database connection
    engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")

    try:
        if not df.empty:
            df.to_sql(table_name, con=engine, if_exists='append', index=False)
            print(f"{len(df)} new rows inserted.")
        else:
            print("No new rows to insert.")
    except Exception as e:
        print(f"Error occurred: {e}")

