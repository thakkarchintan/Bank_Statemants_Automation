import pandas as pd
import pymysql
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

# MySQL database credentials
DATABASE_TYPE = os.getenv("DATABASE_TYPE")
DBAPI = os.getenv("DBAPI")
HOST = os.getenv("HOST")
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
DATABASE = os.getenv("DATABASE")
PORT = 3306
# int(os.getenv("PORT"))

# Table name
# user_name='user1'
# table_name = user_name+'_table'

# 1. Create a new database
def create_database(database_name,cursor):
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
        print(f"Database '{database_name}' created successfully.")
    except Exception as e:
        print("Error creating database:", e)

# 2. Create a new table
def create_table(database_name, create_table_query,conn):
    try:
        cursor=conn.cursor()
        conn.select_db(database_name)  # Use the database
        # create_table_query = f"""
        # CREATE TABLE IF NOT EXISTS {table_name} (
        #     id INT PRIMARY KEY,
        #     name VARCHAR(50),
        #     age INT
        # )
        # """
        cursor.execute(create_table_query)
        print(f"Table created successfully in database '{database_name}'.")
    except Exception as e:
        print("Error creating table:", e)

# 3. Insert data into the table
def insert_data(database_name, table_name, data,conn,cursor):
    try:
        conn.select_db(database_name)
        insert_query = f"INSERT IGNORE INTO {table_name} (id,user_name, name, email) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, data)  
        conn.commit()
        print(f"Data inserted successfully into table '{table_name}'.")
    except Exception as e:
        print("Error inserting data:", e)

# 4. Update data in the table
def update_data(database_name, table_name, column, value, condition,conn,cursor):
    try:
        conn.select_db(database_name)
        update_query = f"UPDATE {table_name} SET {column} = %s WHERE {condition}"
        cursor.execute(update_query, (value,))
        conn.commit()
        print(f"Data updated successfully in table '{table_name}'.")
    except Exception as e:
        print("Error updating data:", e)

# 5. Delete data from the table
def delete_data(database_name, table_name, condition,conn,cursor):
    try:
        conn.select_db(database_name)
        delete_query = f"DELETE FROM {table_name} WHERE {condition}"
        cursor.execute(delete_query)
        conn.commit()
        print(f"Data deleted successfully from table '{table_name}'.")
    except Exception as e:
        print("Error deleting data:", e)

def add_data(df,override,database_name, table_name):
    conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, port=PORT)
    cursor = conn.cursor()
    create_database(database_name,cursor)

    create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            Bank VARCHAR(50), 
            Date DATE, 
            Narration VARCHAR(255), 
            Debit FLOAT, 
            Credit FLOAT, 
            Category VARCHAR(50)
        )
    """
    create_table(database_name,create_table_query,conn)

    if override :
        min_date=min(df['Date'])
        max_date=max(df['Date'])
        bank=df['Bank'][0]
        
        condition=f"Bank='{bank}' and Date between '{min_date}' and '{max_date}'"
        print(condition)

        delete_data(database_name, table_name,condition,conn,cursor)

    # Close the connection
    cursor.close()
    conn.close()

    # Create database connection
    engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")

    try:
        if not df.empty:
            # Insert the new rows into the database
            # df.to_sql(table_name, con=Conn, if_exists='append', index=False)
            df.to_sql(table_name, con=engine, if_exists='append', index=False)

            print(f"{len(df)} new rows inserted.")
        else:
            print("No new rows to insert.")
    except Exception as e:
        print(f"Error occurred: {e}")


def get_data(database_name,table_name):
    conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, port=PORT)
    cursor = conn.cursor()
    create_database(database_name,cursor)

    create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            Bank VARCHAR(50), 
            Date DATE, 
            Narration VARCHAR(255), 
            Debit FLOAT, 
            Credit FLOAT, 
            Category VARCHAR(50)
        )
    """
    create_table(database_name,create_table_query,conn)

    # Close the connection
    cursor.close()
    conn.close()

    # Create database connection
    engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")

    with engine.connect() as Conn:
        # Read existing data from the table
        all_data = pd.read_sql(text(f"SELECT * FROM {table_name} order by Date;"), Conn)

        return all_data
    
    return pd.DataFrame()

        # # Find new rows that are not in the existing data
        # merged_data = pd.concat([df_new, existing_data],ignore_index=True)

        # print(merged_data)

def add_user(database_name,table_name,data):
    conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, port=PORT)
    cursor = conn.cursor()

    create_database(database_name,cursor)

    create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INT PRIMARY KEY,
            user_name VARCHAR(50),
            name VARCHAR(50),
            email VARCHAR(50)
        )
    """
    create_table(database_name,create_table_query,conn)
    insert_data(database_name,table_name,data,conn,cursor)
    # Close the connection
    cursor.close()
    conn.close()

# Check for duplicate rows and append only new ones
# try:
    # sample_data = [
    #     (1, 'Alice', 25),
    #     (2, 'Bob', 30),
    #     (3, 'Charlie', 35)
    # ]
    # conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, port=PORT)
    # cursor = conn.cursor()

    # create_database(DATABASE,cursor)
    # create_table(DATABASE,table_name,conn)
    # insert_data(DATABASE,table_name,sample_data,conn,cursor)
    # update_data(DATABASE,table_name,'age', 69, 'id = 1',conn,cursor)
    # delete_data(DATABASE,table_name,'id = 2',conn,cursor)

    # # Close the connection
    # cursor.close()
    # conn.close()
    
# except Exception as e:
#     print("An error occurred:", e)
