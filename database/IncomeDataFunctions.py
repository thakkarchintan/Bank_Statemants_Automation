from .database_init import *

def create_incomes_table(username):
    try:
        with mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name) as conn:
            with conn.cursor() as cursor:
                create_table_query = f"""
                CREATE TABLE IF NOT EXISTS `{username}_Incomes`(
                    Income_ID INT AUTO_INCREMENT PRIMARY KEY,
                    Source ENUM('Salary', 'Bonuses & Commissions', 'Business Income', 'Freelancing', 'Consulting', 'Dividends', 'Royalties', 'Other'),
                    Value DECIMAL(10,2),
                    Frequency ENUM('Daily', 'Weekly', 'bi-Weekly', 'Monthly', 'Quarterly', 'Half-Yearly', 'Annual'),
                    Start_Date DATE,
                    End_Date DATE,
                    Growth_Rate DECIMAL(5,2)
                );
                """

                # Execute the query
                cursor.execute(create_table_query)
                conn.commit()
                print("✅ Incomes table created successfully!")

    except mysql.connector.Error as err:
        print(f"❌ Error creating table: {err}")
    


def add_income(username, source, value, frequency, start_date, end_date, growth_rate):
    """Insert income details into the Incomes table."""
    create_incomes_table(username)
    try:
        with mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name) as conn:
            with conn.cursor() as cursor:
                query = f"""
                INSERT INTO `{username}_Incomes`(Source, Value, Frequency, Start_Date, End_Date, Growth_Rate)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (source, value, frequency, start_date, end_date, growth_rate))
                conn.commit()
                logging.info(f"Income added successfully for user {username}.")
    except mysql.connector.Error as err:
        logging.error(f"Error inserting income: {err}")


# Function to fetch all income records for a user
def get_incomes(username):
    """Retrieve all income details for a specific user."""
    try:
        with mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name) as conn:
            with conn.cursor() as cursor:
                query = f"SELECT Income_ID, Source, Value, Frequency, Start_Date, End_Date, Growth_Rate FROM `{username}_Incomes`"
                cursor.execute(query)
                return cursor.fetchall()
    except mysql.connector.Error as err:
        logging.error(f"Error retrieving incomes: {err}")
        return []


# Function to delete an income record
def delete_income(df, username):
    """Delete all investment in the given DataFrame from the database using SQLAlchemy."""
    if df.empty:
        logging.info("No Income to delete.")
        return df  # Return unchanged DataFrame

    try:
        engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")

        with engine.connect() as conn:
            for _, row in df.iterrows():
                query = text(f"""
                    DELETE FROM `{username}_Incomes`
                    WHERE Income_ID = :Ii
                    AND Source = :sr
                    AND Value = :val
                    AND Frequency = :fq
                    AND Start_Date = :sd
                    AND End_Date = :ed
                    AND Growth_Rate = :gr
                """)

                conn.execute(query, {
                    "Ii": row["Income_ID"],
                    "sr": row["Source"],
                    "val": row["Value"],
                    "fq":row["Frequency"],
                    "sd": row["Start_Date"],
                    "ed": row["End_Date"],
                    "gr":row["Growth_Rate"]
                })
                conn.commit()

        logging.info(f"Deleted {len(df)} Income from the database.")

        return df.iloc[0:0]  # Return empty DataFrame after deletion

    except Exception as e:
        logging.error(f"Error deleting Income: {e}")
        return df  # Return original DataFrame if error occurs


