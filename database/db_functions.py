import pandas as pd
import pymysql
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import datetime as dt
import pytz

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
        conn.select_db(database_name)  
        cursor.execute(create_table_query)
        print(f"Table created successfully in database '{database_name}'.")
        cursor.close()
    except Exception as e:
        print("Error creating table:", e)

# 3. Insert data into the table
def insert_data(database_name, table_name, data, conn, cursor, col_names=""):
    try:
        no_of_values=len(data)
        no_of_values-=1
        s='( %s'
        for i in range(no_of_values):
            s+=", %s"
        s+=' )'
        conn.select_db(database_name)
        insert_query = f"INSERT IGNORE INTO {table_name} {col_names} VALUES {s};"
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
def delete_data(database_name, table_name, condition):
    try:
        conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, port=PORT)
        cursor = conn.cursor()
        conn.select_db(database_name)
        delete_query = f"DELETE FROM {table_name} WHERE {condition}"
        cursor.execute(delete_query)
        conn.commit()
        print(f"Data deleted successfully from table '{table_name}'.")
        # Close the connection
        cursor.close()
        conn.close()
    except Exception as e:
        print("Error deleting data:", e)

def add_data(df,override,database_name, table_name):
    conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, port=PORT)
    cursor = conn.cursor()
    # create_database(database_name,cursor)

    create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            Name VARCHAR(50), 
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

        delete_data(database_name, table_name,condition)

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

def get_transaction_data(database_name,table_name):
    conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, port=PORT)
    cursor = conn.cursor()
    # create_database(database_name,cursor)

    create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            Name VARCHAR(50),
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


def add_user(database_name,table_name,data):
    conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, port=PORT)
    cursor = conn.cursor()

    # create_database(database_name,cursor)

    create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            user_name VARCHAR(50) primary key,
            name VARCHAR(50),
            email VARCHAR(50) UNIQUE
        )
    """
    create_table(database_name,create_table_query,conn)
    insert_data(database_name,table_name,data,conn,cursor)
    # Close the connection
    cursor.close()
    conn.close()

def update_summary(database_name,table_name,ac_name,bank,From,Till,no_of_transactions):
    conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, port=PORT)
    create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            Name VARCHAR(50), 
            Bank VARCHAR(50), 
            Start_Date DATE,
            End_Date DATE,
            Pending_days INT,
            Transactions INT
        );
    """
    create_table(database_name,create_table_query,conn)
    
    cursor = conn.cursor()

    query = f"SELECT Start_Date,End_Date,Transactions FROM {table_name} WHERE Name = %s and Bank = %s"
    cursor.execute(query, (ac_name,bank,))

    # Fetch result
    dates_and_transactions = cursor.fetchone()

    # Close connection
    cursor.close()
    cursor = conn.cursor()
    # Store in Python variable
    # Till=dt.datetime.strptime(Till,'%Y-%m-%d')
    # From=dt.datetime.strptime(From,'%Y-%m-%d')
    ist = pytz.timezone('Asia/Kolkata')
    # print(dt.datetime.now(ist))
    pending_days=dt.datetime.now(ist) - ist.localize(Till)
    if dates_and_transactions:
        # dates[0]=dt.datetime.strptime(str(dates[0]),'%Y-%m-%d')
        # dates[1]=dt.datetime.strptime(str(dates[1]),'%Y-%m-%d')
        From=min(dt.datetime.strptime(str(dates_and_transactions[0]),'%Y-%m-%d'),From)
        Till=max(dt.datetime.strptime(str(dates_and_transactions[1]),'%Y-%m-%d'),Till)
        no_of_transactions+=dates_and_transactions[2]
        pending_days=dt.datetime.now(ist) - ist.localize(Till)
        # print(type(pending_days.days))

        condition=f"""
        Bank="{bank}"
        """
        update_data(database_name,table_name,'Start_Date',From,condition,conn,cursor)
        update_data(database_name,table_name,'End_Date',Till,condition,conn,cursor)
        update_data(database_name,table_name,'Pending_days',pending_days.days,condition,conn,cursor)
        update_data(database_name,table_name,'Transactions',no_of_transactions,condition,conn,cursor)
    
    else:
        data=(ac_name,bank,From,Till,pending_days.days,no_of_transactions)
        insert_data(database_name,table_name,data,conn,cursor)
    
    cursor.close()
    conn.close()

def get_summary_data(database_name,table_name):
    conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, port=PORT)
    cursor = conn.cursor()
    # create_database(database_name,cursor)

    create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            Name VARCHAR(50), 
            Bank VARCHAR(50), 
            Start_Date DATE,
            End_Date DATE,
            Pending_days INT,
            Transactions INT
        );
    """
    create_table(database_name,create_table_query,conn)

    # Close the connection
    cursor.close()
    conn.close()

    # Create database connection
    engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")

    with engine.connect() as Conn:
        # Read existing data from the table
        all_data = pd.read_sql(text(f"SELECT * FROM {table_name} order by Bank;"), Conn)

        return all_data
    
    return pd.DataFrame()

def add_feedback(database_name,table_name,data):
    conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, port=PORT)
    cursor = conn.cursor()

    # create_database(database_name,cursor)

    create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id varchar(50) ,
            feedback VARCHAR(255)
        )
    """
    create_table(database_name,create_table_query,conn)
    insert_data(database_name,table_name,data,conn,cursor)
    # Close the connection
    cursor.close()
    conn.close()

def get_name(database_name,table_name,user_name):
    conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, port=PORT)
    conn.select_db(database_name)
    create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            user_name VARCHAR(50) primary key,
            name VARCHAR(50),
            email VARCHAR(50) UNIQUE
        )
    """
    create_table(database_name,create_table_query,conn)
    cursor = conn.cursor()
    query = f"SELECT name FROM {table_name} WHERE user_name = %s;"
    cursor.execute(query, (user_name,))

    # Fetch result
    name = cursor.fetchone()

    # Close connection
    cursor.close()
    cursor = conn.cursor()

    return name[0] if name else ""