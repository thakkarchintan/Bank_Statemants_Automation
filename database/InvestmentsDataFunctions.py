from .database_init import *


def create_investment_table(username):
    """Create a table for storing user investments."""
    try:
        with mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name) as conn:
            with conn.cursor() as cursor:
                query = f"""
                CREATE TABLE IF NOT EXISTS {username}_Investments (
                    Investment_ID INT AUTO_INCREMENT PRIMARY KEY,
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
                );"""
                cursor.execute(query)
                conn.commit()
                logging.info(f"Table created {username}_Investments")
    except mysql.connector.Error as err:
        logging.error(f"Error creating investment table: {err}")

def add_investment(username, inv_type, inv_amount, inv_start_date, inv_end_date, inv_rate_of_return):
    """Insert investment details into the Investments table."""
    create_investment_table(username)
    try:
        with mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name) as conn:
            with conn.cursor() as cursor:
                insert_query = f"""
                INSERT INTO {username}_Investments (Investment_Type, Amount, Start_Date, End_Date, Rate_of_Return)
                VALUES (%s, %s, %s, %s, %s);"""
                cursor.execute(insert_query, (inv_type, inv_amount, inv_start_date, inv_end_date, inv_rate_of_return))
                conn.commit()
                logging.info(f"Investment added successfully for user {username}.")
    except mysql.connector.Error as err:
        logging.error(f"Error inserting investment: {err}")

def get_investments(username):
    """Retrieve all investments details for a specific user."""
    try:
        with mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name) as conn:
            with conn.cursor() as cursor:
                query = f"SELECT * FROM {username}_Investments"
                cursor.execute(query)
                return cursor.fetchall()
    except mysql.connector.Error as err:
        logging.error(f"Error retrieving investments: {err}")
        return []

def delete_investments(df, username):
    """Delete all investment in the given DataFrame from the database using SQLAlchemy."""
    if df.empty:
        logging.info("No investment to delete.")
        return df  # Return unchanged DataFrame

    try:
        engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")

        with engine.connect() as conn:
            for _, row in df.iterrows():
                query = text(f"""
                    DELETE FROM `{username}_Investments`
                    WHERE Investment_ID = :id
                    AND Investment_Type = :it
                    AND Amount = :amt
                    AND Start_Date = :sd
                    AND End_Date = :ed
                    AND Rate_of_Return = :ror
                """)

                conn.execute(query, {
                    "id":row["ID"],
                    "it": row["Investment Type"],
                    "amt": row["Amount"],
                    "sd": row["Start Date"],
                    "ed": row["End Date"],
                    "ror":row["Rate of Return"]
                })
                conn.commit()

        logging.info(f"Deleted {len(df)} investment from the database.")

        return df.iloc[0:0]  # Return empty DataFrame after deletion

    except Exception as e:
        logging.error(f"Error deleting investment: {e}")
        return df  # Return original DataFrame if error occurs
