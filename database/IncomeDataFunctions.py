from .database_init import *
from sqlalchemy import create_engine, text
import logging 

def create_incomes_table(username):
    try:
        with mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name) as conn:
            with conn.cursor() as cursor:
                create_table_query = f"""
                CREATE TABLE IF NOT EXISTS `{username}_Incomes`(
                    Income_ID INT AUTO_INCREMENT PRIMARY KEY,
                    Profile_Name VARCHAR(100) NOT NULL,
                    Source ENUM('Salary', 'Bonuses & Commissions', 'Business Income', 'Freelancing', 'Consulting', 'Dividends', 'Royalties', 'Other'),
                    Value DECIMAL(10,2),
                    Frequency ENUM('Daily', 'Weekly', 'bi-Weekly', 'Monthly', 'Quarterly', 'Half-Yearly', 'Annual'),
                    Start_Date DATE,
                    End_Date DATE,
                    Growth_Rate DECIMAL(5,2)
                );
                """
                cursor.execute(create_table_query)
                conn.commit()
                print("✅ Incomes table created successfully!")
                # Ensure Profile_Name column exists (even though it's in the query, call this for consistency)
                ensure_profile_name_column(username)
    except mysql.connector.Error as err:
        print(f"❌ Error creating table: {err}")
    

def add_income(username, profile_name, source, value, frequency, start_date, end_date, growth_rate):
    create_incomes_table(username)  # This will now ensure Profile_Name exists
    try:
        with mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name) as conn:
            with conn.cursor() as cursor:
                query = f"""
                INSERT INTO `{username}_Incomes`(Profile_Name, Source, Value, Frequency, Start_Date, End_Date, Growth_Rate)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (profile_name, source, value, frequency, start_date, end_date, growth_rate))
                conn.commit()
                logging.info(f"Income added successfully for user {username} under profile '{profile_name}'.")
    except mysql.connector.Error as err:
        logging.error(f"Error inserting income: {err}")


def get_incomes(username, profile_name):
    """Retrieve all income details for a specific user and profile."""
    try:
        with mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name) as conn:
            with conn.cursor() as cursor:
                query = f"""
                SELECT Income_ID, Source, Value, Frequency, Start_Date, End_Date, Growth_Rate 
                FROM `{username}_Incomes` 
                WHERE Profile_Name = %s
                """
                cursor.execute(query, (profile_name,))
                return cursor.fetchall()
    except mysql.connector.Error as err:
        logging.error(f"Error retrieving incomes: {err}")
        return []


def delete_income(df, username, profile_name):
    """Delete all income records in the given DataFrame for a specific profile."""
    if df.empty:
        logging.info("No Income to delete.")
        return df

    try:
        engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")

        with engine.connect() as conn:
            for _, row in df.iterrows():
                query = text(f"""
                    DELETE FROM `{username}_Incomes`
                    WHERE Income_ID = :id AND Profile_Name = :profile_name
                """)
                conn.execute(query, {"id": row["ID"], "profile_name": profile_name})
            conn.commit()

        logging.info(f"Deleted {len(df)} income records for profile '{profile_name}' from the database.")
        return df.iloc[0:0]

    except Exception as e:
        logging.error(f"Error deleting income: {e}")
        return df

