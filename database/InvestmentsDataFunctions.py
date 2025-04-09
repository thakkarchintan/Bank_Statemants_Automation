from .database_init import *
import logging
import mysql.connector
from sqlalchemy import create_engine, text

def create_investment_table(username):
    try:
        with mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name) as conn:
            with conn.cursor() as cursor:
                query = f"""
                CREATE TABLE IF NOT EXISTS `{username}_Investments` (
                    Investment_ID INT AUTO_INCREMENT PRIMARY KEY,
                    Profile_Name VARCHAR(100) NOT NULL,
                    Investment_Type ENUM('Savings Account', 'Fixed Deposits', 'Government Bonds', 'Corporate Bonds',
                                         'Mutual Funds', 'ETFs', 'Stocks', 'Real Estate', 'Gold', 'Collectibles',
                                         'Private Equity', 'Commodities', 'Art & Antiques', 'Hedge Funds',
                                         'Provident Fund (PF)', 'Precious Metals (Silver, Platinum)', 'Foreign Currency',
                                         'Annuities', 'Life Insurance Policies', 'Business Ownership', 'Cash',
                                         'Cryptocurrency', 'Other'),
                    Amount DECIMAL(15,2),
                    Start_Date DATE,
                    End_Date DATE,
                    Rate_of_Return DECIMAL(5,2)
                );
                """
                cursor.execute(query)
                conn.commit()
                logging.info(f"✅ Table `{username}_Investments` created successfully.")
                ensure_profile_name_column(username)  # Add this call
    except mysql.connector.Error as err:
        logging.error(f"❌ Error creating investment table: {err}")

def add_investment(username, profile_name, inv_type, inv_amount, inv_start_date, inv_end_date, inv_rate_of_return):
    """Insert investment details into the Investments table for a specific profile."""
    if not profile_name:
        logging.error("❌ Profile name is required but received None.")
        return

    create_investment_table(username)
    try:
        with mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name) as conn:
            with conn.cursor() as cursor:
                insert_query = f"""
                INSERT INTO `{username}_Investments` (Profile_Name, Investment_Type, Amount, Start_Date, End_Date, Rate_of_Return)
                VALUES (%s, %s, %s, %s, %s, %s);
                """
                cursor.execute(insert_query, (profile_name, inv_type, inv_amount, inv_start_date, inv_end_date, inv_rate_of_return))
                conn.commit()
                logging.info(f"✅ Investment added for user {username} under profile '{profile_name}'.")
    except mysql.connector.Error as err:
        logging.error(f"❌ Error inserting investment: {err}")

def get_investments(username, profile_name):
    """Retrieve all investment details for a specific user and profile."""
    if not profile_name:
        logging.error("❌ Profile name is required but received None.")
        return []

    try:
        with mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name) as conn:
            with conn.cursor() as cursor:
                query = f"""
                SELECT Investment_ID, Investment_Type, Amount, Start_Date, End_Date, Rate_of_Return 
                FROM `{username}_Investments` 
                WHERE Profile_Name = %s
                """
                cursor.execute(query, (profile_name,))
                return cursor.fetchall()
    except mysql.connector.Error as err:
        logging.error(f"❌ Error retrieving investments: {err}")
        return []

def delete_investments(df, username, profile_name):
    """Delete all investment records in the given DataFrame for a specific profile using SQLAlchemy."""
    if df.empty:
        logging.info("✅ No investment to delete.")
        return df  # Return unchanged DataFrame

    try:
        engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")

        with engine.connect() as conn:
            for _, row in df.iterrows():
                query = text(f"""
                    DELETE FROM `{username}_Investments`
                    WHERE Investment_ID = :id AND Profile_Name = :profile_name
                """)
                conn.execute(query, {"id": row["ID"], "profile_name": profile_name})
            conn.commit()

        logging.info(f"✅ Deleted {len(df)} investment records for profile '{profile_name}'.")
        return df.iloc[0:0]  # Return empty DataFrame after deletion

    except Exception as e:
        logging.error(f"❌ Error deleting investment: {e}")
        return df  # Return original DataFrame if error occurs


