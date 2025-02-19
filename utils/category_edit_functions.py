import streamlit as st
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

# MySQL database credentials
HOST = os.getenv("HOST")
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
DATABASE = os.getenv("DATABASE")

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
            id INT AUTO_INCREMENT PRIMARY KEY,
            keyword VARCHAR(255) NOT NULL,
            category VARCHAR(255) NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Function to add category
def add_category(keyword, category, table_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO {table_name} (keyword, category) VALUES (%s, %s)", (keyword, category))
    conn.commit()
    conn.close()

# Function to get all categories
def get_categories(table_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    categories = cursor.fetchall()
    conn.close()
    return categories

# Function to delete a category
def delete_category(category_id,table_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {table_name} WHERE id = %s", (category_id,))
    conn.commit()
    conn.close()

