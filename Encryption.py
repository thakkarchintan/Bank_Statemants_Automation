import base64
import boto3
from dotenv import load_dotenv
from botocore.exceptions import NoCredentialsError
import botocore.exceptions
import os 
import logging
import pandas as pd
from joblib import Parallel, delayed
from Crypto.Cipher import AES

load_dotenv()

def aws_config():
    # Replace with your actual credentials
    aws_access_key = os.getenv("AWS_ACCESS_KEY")
    aws_secret_key = os.getenv("AWS_SECRET_KEY")  # Fixed typo here
    aws_region = "ap-south-1"  # Change to your AWS region

    # Configure Boto3 session
    session = boto3.Session(
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=aws_region
    )

    # Create an AWS client (Example: KMS client)
    try:
        logging.info("AWS Configuration Successful! ✅")
        return session.client("kms")
    except NoCredentialsError:
        logging.error("Error: AWS credentials not found or incorrect.")
        return None

def get_encrypt_key():
    try:
        kms_client = aws_config()
        if not kms_client:
            raise Exception("Failed to initialize AWS KMS client.")

        response = kms_client.generate_data_key(
            KeyId="alias/Fintellect_Key",  # Use alias or actual Key ID
            KeySpec="AES_256"
        )
        
        # Use raw plaintext key for encryption and base64 encode only the ciphertext blob for storage.
        plaintext_key = response['Plaintext']  # raw bytes for encryption
        encrypted_key = base64.b64encode(response['CiphertextBlob']).decode()  # store securely
        
        return plaintext_key, encrypted_key
    
    except botocore.exceptions.ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == "NotFoundException":
            logging.error("Error: The specified KMS key was not found.")
        elif error_code == "AccessDeniedException":
            logging.error("Error: Access denied. Check IAM permissions for the KMS key.")
        elif error_code == "ValidationException":
            logging.error("Error: Invalid parameters passed to AWS KMS.")
        else:
            logging.error(f"An AWS ClientError occurred: {e}")
    
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

    return None, None  # Return None in case of failure

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def encrypt_aes_gcm(data, aes_key):
    """
    Encrypts a given string using AES-GCM.
    
    Args:
        data (str): Data to encrypt.
        aes_key (bytes): AES encryption key.
    
    Returns:
        str: Encrypted data (base64 encoded IV + ciphertext + tag) or None on failure.
    """
    try:
        cipher = AES.new(aes_key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(data.encode())
        return base64.b64encode(cipher.nonce + ciphertext + tag).decode()
    except Exception as e:
        logging.error(f"Encryption failed for data: {data}. Error: {e}")
        return None  # Return None to handle failures gracefully

def encrypt_column(data, plain_key, column_name):
    """
    Encrypts a Pandas Series using AES-GCM in parallel.
    
    Args:
        data (pd.Series): Column to encrypt.
        plain_key (bytes): AES encryption key.
        column_name (str): Name of the column being encrypted.
    
    Returns:
        pd.Series: Encrypted column.
    """
    logging.info(f"Encrypting column: {column_name}")
    return data.apply(lambda x: encrypt_aes_gcm(str(x), plain_key) if pd.notna(x) else x)

def encrypt_dataframe(df, encrypt_columns):
    """
    Encrypts specified columns in a dataframe using AES and adds an encryption key column.
    
    Args:
        df (pd.DataFrame): The dataframe to encrypt.
        encrypt_columns (list): List of column names to encrypt.
        get_plain_and_encrypted_key (function): Function that returns (plain AES key, encrypted AES key).
    
    Returns:
        pd.DataFrame: Encrypted dataframe.
    """
    if df.empty:
        logging.warning("Received an empty DataFrame. Skipping encryption.")
        return df

    encrypted_df = df.copy()

    # Check if all encrypt_columns exist
    missing_cols = [col for col in encrypt_columns if col not in encrypted_df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns in DataFrame: {missing_cols}")

    try:
        # Generate key once for all rows using the passed function
        plain_key, encrypted_key = get_encrypt_key()
        if plain_key is None:
            logging.error("Encryption key generation failed. Returning unmodified DataFrame.")
            return df

        logging.info("Generated AES key successfully.")

        # Encrypt the specified columns in parallel
        encrypted_df[encrypt_columns] = Parallel(n_jobs=-1)(
            delayed(encrypt_column)(encrypted_df[col], plain_key, col) for col in encrypt_columns
        )

        # Assign encryption key to all rows
        encrypted_df["key"] = encrypted_key

        logging.info("Data encryption completed successfully.")
        return encrypted_df

    except Exception as e:
        logging.error(f"Error occurred during encryption: {e}")
        return df  # Return unmodified DataFrame on failure
    
    
def decrypt_aes_gcm(encrypted_data, aes_key):
    """
    Decrypts a given string using AES-GCM.

    Args:
        encrypted_data (str): Base64 encoded (IV + ciphertext + tag).
        aes_key (bytes): AES decryption key.

    Returns:
        str: Decrypted data or None on failure.
    """
    try:
        encrypted_bytes = base64.b64decode(encrypted_data)
        nonce = encrypted_bytes[:16]  # First 16 bytes = nonce
        ciphertext = encrypted_bytes[16:-16]  # Middle part = encrypted text
        tag = encrypted_bytes[-16:]  # Last 16 bytes = authentication tag

        cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
        decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)

        return decrypted_data.decode()
    except Exception as e:
        logging.error(f"Decryption failed for data: {encrypted_data}. Error: {e}")
        return None  # Return None to handle failures gracefully
    
    

def decrypt_column(data, plain_key, column_name):
    """
    Decrypts a Pandas Series using AES-GCM in parallel.

    Args:
        data (pd.Series): Column to decrypt.
        plain_key (bytes): AES decryption key.
        column_name (str): Name of the column being decrypted.

    Returns:
        pd.Series: Decrypted column.
    """
    logging.info(f"Decrypting column: {column_name}")
    return data.apply(lambda x: decrypt_aes_gcm(x, plain_key) if pd.notna(x) else x)



def decrypt_dataframe(df, decrypt_columns):
    """
    Decrypts specified columns in a dataframe using AES.

    Args:
        df (pd.DataFrame): The encrypted dataframe.
        decrypt_columns (list): List of column names to decrypt.

    Returns:
        pd.DataFrame: Decrypted dataframe.
    """
    if df.empty:
        logging.warning("Received an empty DataFrame. Skipping decryption.")
        return df

    decrypted_df = df.copy()

    # Check if key column exists
    if "key" not in decrypted_df.columns:
        raise ValueError("Missing 'key' column. Cannot decrypt without encryption key.")

    try:
        # Get encrypted AES key from the DataFrame
        encrypted_key = decrypted_df["key"].iloc[0]  # Assuming one key for all rows

        # Decrypt AES key using AWS KMS
        kms_client = aws_config()
        if not kms_client:
            logging.error("Failed to initialize AWS KMS client. Returning unmodified DataFrame.")
            return df

        response = kms_client.decrypt(CiphertextBlob=base64.b64decode(encrypted_key))
        plain_key = response["Plaintext"]

        logging.info("Decrypted AES key successfully.")

        # Decrypt the specified columns in parallel
        decrypted_df[decrypt_columns] = Parallel(n_jobs=-1)(
            delayed(decrypt_column)(decrypted_df[col], plain_key, col) for col in decrypt_columns
        )

        # Remove the encryption key column for security
        decrypted_df.drop(columns=["key"], inplace=True)

        logging.info("Data decryption completed successfully.")
        return decrypted_df

    except Exception as e:
        logging.error(f"Error occurred during decryption: {e}")
        return df  # Return unmodified DataFrame on failure
