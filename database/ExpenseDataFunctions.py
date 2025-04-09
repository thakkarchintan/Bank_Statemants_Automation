from .database_init import *
from sqlalchemy import create_engine, text
import logging 
# Function to create Expenses table
def create_expense_table(username):
    try:
        with mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name) as conn:
            with conn.cursor() as cursor:
                query = f'''CREATE TABLE IF NOT EXISTS `{username}_Expenses`(
                        Expense_ID INT AUTO_INCREMENT PRIMARY KEY,
                        Profile_Name VARCHAR(100) NOT NULL,
                        Expense_Type ENUM('Rent', 'Household expenses', 'Home Maintenance & Utilities', 'Groceries', 'Housekeeping Services', 
                                        'School Tuition Fees', 'College Tuition Fees', 'Vacation - Domestic', 'Vacation - International',
                                        'EMI - Home Loan', 'EMI - Auto Loan', 'EMI - Education Loan', 'EMI - Personal Loan', 'EMI - Other Loan',
                                        'Health Insurance', 'Life Insurance', 'Auto Insurance', 'Medical Expenses', 'Marriage Expenses',
                                        'Fuel / Transportation', 'Entertainment', 'Dining Out', 'Subscriptions', 'Personal Care', 'Clothing', 'Gifts',
                                        'Pet Care', 'Childcare', 'Fitness & Gym', 'Education (Courses, Books)', 'Charity & Donations',
                                        'Professional Services', 'Hobbies & Leisure', 'Other'),
                        Value DECIMAL(10,2),
                        Frequency ENUM('Daily', 'Weekly', 'bi-Weekly', 'Monthly', 'Quarterly', 'Half-Yearly', 'Annual'),
                        Start_Date DATE,
                        End_Date DATE,
                        Inflation_Rate DECIMAL(5,2)
                        );'''
                cursor.execute(query)
                conn.commit()
                logging.info(f"✅ Table `{username}_Expenses` created successfully.")
                ensure_profile_name_column(username)  # Add this call
    except mysql.connector.Error as err:
        logging.error(f"❌ Error creating expenses table: {err}")

            
def add_expense(username, profile_name, exp_type, exp_value, exp_frequency, exp_start_date, exp_end_date, inflation_rate):
    """Insert expense details into the expenses table for a specific profile."""
    create_expense_table(username)  # Ensure table exists

    VALID_EXPENSE_TYPES = {'Rent', 'Household expenses', 'Home Maintenance & Utilities', 'Groceries', 'Housekeeping Services',
                            'School Tuition Fees', 'College Tuition Fees', 'Vacation - Domestic', 'Vacation - International',
                            'EMI - Home Loan', 'EMI - Auto Loan', 'EMI - Education Loan', 'EMI - Personal Loan', 'EMI - Other Loan',
                            'Health Insurance', 'Life Insurance', 'Auto Insurance', 'Medical Expenses', 'Marriage Expenses',
                            'Fuel / Transportation', 'Entertainment', 'Dining Out', 'Subscriptions', 'Personal Care', 'Clothing', 'Gifts',
                            'Pet Care', 'Childcare', 'Fitness & Gym', 'Education (Courses, Books)', 'Charity & Donations',
                            'Professional Services', 'Hobbies & Leisure', 'Other'}

    VALID_FREQUENCIES = {'Daily', 'Weekly', 'bi-Weekly', 'Monthly', 'Quarterly', 'Half-Yearly', 'Annual'}

    if exp_type not in VALID_EXPENSE_TYPES or exp_frequency not in VALID_FREQUENCIES:
        logging.error(f"❌ Invalid ENUM value: Expense_Type={exp_type}, Frequency={exp_frequency}")
        return

    try:
        with mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name) as conn:
            with conn.cursor() as cursor:
                insert_query = f"""
                    INSERT INTO `{username}_Expenses` (Profile_Name, Expense_Type, Value, Frequency, Start_Date, End_Date, Inflation_Rate)
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                """
                cursor.execute(insert_query, (profile_name, exp_type, exp_value, exp_frequency, exp_start_date, exp_end_date, inflation_rate))
                conn.commit()
                logging.info(f"✅ Expense added successfully for `{username}` under profile `{profile_name}`.")

    except mysql.connector.Error as err:
        logging.error(f"❌ Error inserting expense: {err}")


def get_expenses(username, profile_name):
    """Retrieve all expenses for a specific user and profile."""
    try:
        with mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name) as conn:
            with conn.cursor() as cursor:
                query = f"SELECT Expense_ID, Expense_Type, Value, Frequency, Start_Date, End_Date, Inflation_Rate FROM `{username}_Expenses` WHERE Profile_Name = %s"
                cursor.execute(query, (profile_name,))
                return cursor.fetchall()
    except mysql.connector.Error as err:
        logging.error(f"❌ Error retrieving expenses: {err}")
        return []


def delete_expense(df, username, profile_name):
    """Delete all expense records in the given DataFrame for a specific profile."""
    if df.empty:
        logging.info("⚠️ No Expenses to delete.")
        return df

    try:
        engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")

        with engine.connect() as conn:
            for _, row in df.iterrows():
                query = text(f"""
                    DELETE FROM `{username}_Expenses`
                    WHERE Expense_ID = :id AND Profile_Name = :profile_name
                """)
                conn.execute(query, {"id": row["ID"], "profile_name": profile_name})
            conn.commit()

        logging.info(f"✅ Deleted {len(df)} expenses for profile `{profile_name}`.")
        return df.iloc[0:0]

    except Exception as e:
        logging.error(f"❌ Error deleting expenses: {e}")
        return df


#################################################### Add savings ########################################### 
def create_savings_table(username):
    try:
        with mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name) as conn:
            with conn.cursor() as cursor:
                create_table_query = f"""
                CREATE TABLE IF NOT EXISTS `{username}_Savings`(
                    Saving_ID INT AUTO_INCREMENT PRIMARY KEY,
                    Profile_Name VARCHAR(100) NOT NULL,
                    Saving_Rate DECIMAL(5,2)
                );
                """
                cursor.execute(create_table_query)
                conn.commit()
                logging.info(f"✅ Savings table created for `{username}`.")
                ensure_profile_name_column(username)  # Add this call
    except mysql.connector.Error as err:
        logging.error(f"❌ Error creating savings table: {err}")


def add_savings(username, profile_name, rate):
    """Insert saving details into the savings table for a specific profile."""
    create_savings_table(username)

    try:
        with mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name) as conn:
            with conn.cursor() as cursor:
                insert_query = f"""
                    INSERT INTO `{username}_Savings` (Profile_Name, Saving_Rate)
                    VALUES (%s, %s);
                """
                cursor.execute(insert_query, (profile_name, rate))
                conn.commit()
                logging.info(f"✅ Saving added successfully for `{username}` under profile `{profile_name}`.")
    except mysql.connector.Error as err:
        logging.error(f"❌ Error inserting saving: {err}")


def get_savings(username, profile_name):
    """Retrieve all savings for a specific user and profile."""
    try:
        with mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name) as conn:
            with conn.cursor() as cursor:
                query = f"SELECT Saving_ID, Saving_Rate FROM `{username}_Savings` WHERE Profile_Name = %s"
                cursor.execute(query, (profile_name,))
                return cursor.fetchall()
    except mysql.connector.Error as err:
        logging.error(f"❌ Error retrieving savings: {err}")
        return []


def delete_savings(username, profile_name, savings_id):
    """Delete a saving record by ID and profile name."""
    try:
        with mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name) as conn:
            with conn.cursor() as cursor:
                query = f"DELETE FROM `{username}_Savings` WHERE Saving_ID = %s AND Profile_Name = %s"
                cursor.execute(query, (savings_id, profile_name))
                conn.commit()
                logging.info(f"✅ Saving `{savings_id}` deleted for profile `{profile_name}`.")
    except mysql.connector.Error as err:
        logging.error(f"❌ Error deleting saving: {err}")
