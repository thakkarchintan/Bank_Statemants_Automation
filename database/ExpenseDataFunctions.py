from .database_init import *
# Function to insert Expense records

def create_expense_table(username):
    """Delete an income record by ID."""
    try:
        with mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name) as conn:
            with conn.cursor() as cursor:
                query = f'''CREATE TABLE IF NOT EXISTS `{username}_Expenses`(
                        Expense_ID INT AUTO_INCREMENT PRIMARY KEY,
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
                logging.info(f"Table created {username}-Expenses")
    except mysql.connector.Error as err:
        logging.error(f"Error deleting income: {err}")

            
def add_expense(username, exp_type, exp_value, exp_frequency, exp_start_date, exp_end_date, inflation_rate):
    """Insert expense details into the expenses table."""
    create_expense_table(username)  # Ensure table exists

    # Validate ENUM values
    VALID_EXPENSE_TYPES = {'Rent', 'Household expenses', 'Home Maintenance & Utilities', 'Groceries', 'Housekeeping Services',
                            'School Tuition Fees', 'College Tuition Fees', 'Vacation - Domestic', 'Vacation - International',
                            'EMI - Home Loan', 'EMI - Auto Loan', 'EMI - Education Loan', 'EMI - Personal Loan', 'EMI - Other Loan',
                            'Health Insurance', 'Life Insurance', 'Auto Insurance', 'Medical Expenses', 'Marriage Expenses',
                            'Fuel / Transportation', 'Entertainment', 'Dining Out', 'Subscriptions', 'Personal Care', 'Clothing', 'Gifts',
                            'Pet Care', 'Childcare', 'Fitness & Gym', 'Education (Courses, Books)', 'Charity & Donations',
                            'Professional Services', 'Hobbies & Leisure', 'Other'}

    VALID_FREQUENCIES = {'Daily', 'Weekly', 'bi-Weekly', 'Monthly', 'Quarterly', 'Half-Yearly', 'Annual'}

    if exp_type not in VALID_EXPENSE_TYPES or exp_frequency not in VALID_FREQUENCIES:
        logging.error(f"Invalid ENUM value: Expense_Type={exp_type}, Frequency={exp_frequency}")
        return

    try:
        with mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name) as conn:
            with conn.cursor() as cursor:
                insert_query = f"""
                    INSERT INTO `{username}_Expenses` (Expense_Type, Value, Frequency, Start_Date, End_Date, Inflation_Rate)
                    VALUES (%s, %s, %s, %s, %s, %s);
                """
                cursor.execute(insert_query, (exp_type, exp_value, exp_frequency, exp_start_date, exp_end_date, inflation_rate))
                conn.commit()
                logging.info(f"Expense added successfully for user {username}.")

                # Debugging: Check if the expense is added
                expenses = get_expenses(username)
                print(f"DEBUG: Expenses after adding = {expenses}")
                

    except mysql.connector.Error as err:
        logging.error(f"Error inserting Expense: {err}")



def get_expenses(username):
    try:
        with mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name) as conn:
            with conn.cursor() as cursor:
                query = f"SELECT * FROM `{username}_Expenses`"
                cursor.execute(query)
                data = cursor.fetchall()
                print(f"DEBUG: Expenses fetched -> {data}")
                return data
    except mysql.connector.Error as err:
        print(f"ERROR: {err}")
        return []


def delete_expense(df,username):
    """Delete all investment in the given DataFrame from the database using SQLAlchemy."""
    if df.empty:
        logging.info("No Expenses to delete.")
        return df  # Return unchanged DataFrame

    try:
        engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")

        with engine.connect() as conn:
            for _, row in df.iterrows():
                query = text(f"""
                    DELETE FROM `{username}_Expenses`
                    WHERE Expense_ID = :Ei
                    AND Expense_Type = :et
                    AND Value = :val
                    AND Frequency = :fq
                    AND Start_Date = :sd
                    AND End_Date = :ed
                    AND Inflation_Rate = :ir
                """)

                conn.execute(query, {
                    "Ei": row["Expense_ID"],
                    "et": row["Expense_Type"],
                    "val": row["Value"],
                    "fq":row["Frequency"],
                    "sd": row["Start_Date"],
                    "ed": row["End_Date"],
                    "ir":row["Inflation_Rate"]
                })
                conn.commit()

        logging.info(f"Deleted {len(df)} Expenses from the database.")

        return df.iloc[0:0]  # Return empty DataFrame after deletion

    except Exception as e:
        logging.error(f"Error deleting Expenses: {e}")
        return df  # Return original DataFrame if error occurs)

            
#################################################### Add savings ########################################### 
def create_savings_table(username):
    try:
        with mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name) as conn:
            with conn.cursor() as cursor:
                create_table_query = f"""
                CREATE TABLE IF NOT EXISTS `{username}_Savings`(
                    Saving_ID INT AUTO_INCREMENT PRIMARY KEY,
                    Saving_Rate DECIMAL(5,2)
                );
                """

                # Execute the query
                cursor.execute(create_table_query)
                conn.commit()
                print("✅ Savings table created successfully!")

    except mysql.connector.Error as err:
        print(f"❌ Error creating table: {err}")
 

def add_savings(username,rate):
    """Insert income details into the Incomes table."""
    create_savings_table(username)
    try:
        with mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name) as conn:
            with conn.cursor() as cursor:
                insert_query = f"""
                                INSERT INTO `{username}_Savings`(Saving_Rate)
                                VALUES (%s);
                                """
                cursor.execute(insert_query, (rate,))
                conn.commit()
                logging.info(f"Saving added successfully for user {username}.")
    except mysql.connector.Error as err:
        logging.error(f"Error inserting Saving: {err}")

            
def get_savings(username):
    """Retrieve all expenses details for a specific user."""
    try:
        with mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name) as conn:
            with conn.cursor() as cursor:
                query = f"SELECT * FROM `{username}_Savings`"
                cursor.execute(query)
                return cursor.fetchall()
    except mysql.connector.Error as err:
        logging.error(f"Error retrieving savings: {err}")
        return []

            
def delete_savings(username,savings_id):
    """Delete an income record by ID."""
    try:
        with mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name) as conn:
            with conn.cursor() as cursor:
                query = f"DELETE FROM `{username}_Savings` WHERE Saving_ID = %s"
                cursor.execute(query, (savings_id,))
                conn.commit()
                logging.info(f"Income {savings_id} deleted successfully.")
    except mysql.connector.Error as err:
        logging.error(f"Error deleting income: {err}")
 