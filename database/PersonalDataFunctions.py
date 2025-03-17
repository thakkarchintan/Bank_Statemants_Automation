from .database_init import *

def create_dependents_table(username):
    """Creates the Dependents table if it does not already exist."""
    try:
        with mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name) as conn:
            with conn.cursor() as cursor:
                create_table_query = f"""
                    CREATE TABLE IF NOT EXISTS `{username}_Dependents` (
                        Dependent_ID INT AUTO_INCREMENT PRIMARY KEY,
                        Name VARCHAR(255) NOT NULL,
                        Date_of_Birth DATE NOT NULL,
                        Gender ENUM('Male', 'Female', 'Other') NOT NULL,
                        Relationship ENUM('Spouse', 'Children', 'Mother', 'Father', 'Other', 'Self') NOT NULL
                    );
                """
                cursor.execute(create_table_query)
                conn.commit()
                logging.info("Dependents table created successfully.")
    except mysql.connector.Error as err:
        logging.error(f"Error creating Dependents table: {err}")



def get_self_details(username):
    """Fetch personal details stored as 'Self' in the dependents table."""
    create_dependents_table(username)  # Ensure table exists
    try:
        with mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name) as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(f"""
                    SELECT Name, Date_of_Birth, Gender 
                    FROM `{username}_Dependents`
                    WHERE Relationship = 'Self'
                """)  # ✅ Fixed WHERE clause
                return cursor.fetchone()  # Returns details if exists, else None
    except mysql.connector.Error as err:
        logging.error(f"Error fetching personal details for `{username}`: {err}")
        return None



def upsert_self_details(username, name, dob, gender):
    """Insert or update the 'Self' entry in the dependents table."""
    try:
        with mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name) as conn:
            with conn.cursor() as cursor:
                # Step 1: Check if 'Self' relation already exists
                cursor.execute(f"SELECT Dependent_ID FROM `{username}_Dependents` WHERE Relationship = 'Self' LIMIT 1")
                existing_record = cursor.fetchone()

                if existing_record:
                    # Step 2: If exists, update it
                    query = f"""
                        UPDATE `{username}_Dependents`
                        SET Name = %s, Date_of_Birth = %s, Gender = %s
                        WHERE Relationship = 'Self'
                    """
                    cursor.execute(query, (name, dob, gender))
                else:
                    # Step 3: If doesn't exist, insert new record
                    query = f"""
                        INSERT INTO `{username}_Dependents` (Name, Date_of_Birth, Gender, Relationship)
                        VALUES (%s, %s, %s, 'Self')
                    """
                    cursor.execute(query, (name, dob, gender))
                
                conn.commit()
                return True

    except mysql.connector.Error as err:
        logging.error(f"Error updating personal details for `{username}`: {err}")
        return False



def add_dependent(username, name, dob, gender, relationship):
    """Insert a dependent into the database."""
    try:
        conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
        cursor = conn.cursor()

        query = f"INSERT INTO `{username}_Dependents` (Name, Date_of_Birth, Gender, Relationship) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (name, dob, gender, relationship))

        conn.commit()
        logging.info(f"Dependent `{name}` added successfully for user `{username}`.")

    except mysql.connector.Error as err:
        logging.error(f"Error adding dependent `{name}`: {err}")

    finally:
        cursor.close()
        conn.close()


def get_dependents(username):
    """Retrieve dependents for a user."""
    try:
        conn = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_name)
        cursor = conn.cursor()

        query = f"""SELECT Dependent_ID, Name, Date_of_Birth, Gender, Relationship 
                    FROM `{username}_Dependents`;"""
        cursor.execute(query)

        columns = [col[0] for col in cursor.description]  # Get column names
        dependents = [dict(zip(columns, row)) for row in cursor.fetchall()]  # Convert to list of dicts

        return dependents

    except mysql.connector.Error as err:
        logging.error(f"Error retrieving dependents for `{username}`: {err}")
        return []

    finally:
        cursor.close()
        conn.close()


def delete_dependents(df, username):
    """Delete all dependents in the given DataFrame from the database using SQLAlchemy."""
    if df.empty:
        logging.info("No dependents to delete.")
        return df  # Return unchanged DataFrame

    try:
        engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")

        with engine.connect() as conn:
            for _, row in df.iterrows():
                query = text(f"""
                    DELETE FROM `{username}_Dependents`
                    WHERE Dependent_ID = :id
                    AND Name = :name
                    AND Date_of_Birth = :dob
                    AND Gender = :gender
                    AND Relationship = :relationship
                """)

                conn.execute(query, {
                    "id":row["ID"],
                    "name": row["Name"],
                    "dob": row["Date of Birth"],
                    "gender": row["Gender"],
                    "relationship": row["Relationship"]
                })
                conn.commit()

        logging.info(f"Deleted {len(df)} dependents from the database.")

        return df.iloc[0:0]  # Return empty DataFrame after deletion

    except Exception as e:
        logging.error(f"Error deleting dependents: {e}")
        return df  # Return original DataFrame if error occurs
               


