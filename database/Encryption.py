import base64
import boto3
from dotenv import load_dotenv
from botocore.exceptions import NoCredentialsError, ClientError
import os
import logging
import pandas as pd
from Crypto.Cipher import AES

# Load environment variables
load_dotenv(dotenv_path=os.path.join("home","ec2-user","app",".env"))

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def aws_config():
    """Configures AWS credentials and creates a KMS client."""
    aws_access_key = os.getenv("AWS_ACCESS_KEY")
    aws_secret_key = os.getenv("AWS_SECRET_KEY")
    aws_region = "ap-south-1"  # Change to your AWS region

    try:
        session = boto3.Session(
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )
        logging.info("AWS Configuration Successful! ✅")
        return session.client("kms")
    except NoCredentialsError:
        logging.error("Error: AWS credentials not found or incorrect.")
        return None

def get_encrypt_key():
    """Generates a data key using AWS KMS and returns the plaintext & encrypted key."""
    try:
        kms_client = aws_config()
        if not kms_client:
            raise Exception("Failed to initialize AWS KMS client.")

        response = kms_client.generate_data_key(
            KeyId="alias/Fintellect_Key",  # Use alias or actual Key ID
            KeySpec="AES_256"
        )

        plaintext_key = response['Plaintext']
        encrypted_key = base64.b64encode(response['CiphertextBlob']).decode()  # Store securely

        return plaintext_key, encrypted_key

    except ClientError as e:
        logging.error(f"AWS KMS ClientError: {e.response['Error']['Code']}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

    return None, None

def encrypt_aes_gcm(data, aes_key, aad=None):
    """Encrypts a given value using AES-GCM with Base64 encoding and optional AAD."""
    try:
        if data is None:
            raise ValueError("Cannot encrypt NoneType data.")

        # Ensure AES key is in bytes
        if isinstance(aes_key, str):
            aes_key = aes_key.encode()  # Convert string key to bytes

        # Validate AES key length
        if len(aes_key) not in [16, 24, 32]:
            raise ValueError("Invalid AES key length. It must be 16, 24, or 32 bytes.")

        # Convert data to string & bytes
        data_str = str(data).encode()

        # Create AES cipher in GCM mode with a random 12-byte nonce
        cipher = AES.new(aes_key, AES.MODE_GCM , nonce=os.urandom(12))

        # If AAD is provided, use it for authentication
        if aad:
            cipher.update(aad.encode())  # Adds authentication data

        # Encrypt the data
        ciphertext, tag = cipher.encrypt_and_digest(data_str)

        # Encode (Nonce + Ciphertext + Tag) as Base64
        encrypted_output = base64.b64encode(cipher.nonce + ciphertext + tag).decode()

        return encrypted_output
    except Exception as e:
        logging.error(f"Encryption failed for data: {data}. Error: {e}")
        return None

def decrypt_aes_gcm(encrypted_data, aes_key, aad=None):
    """Decrypts a given string using AES-GCM while handling Base64 encoding issues."""
    try:
        encrypted_bytes = base64.b64decode(encrypted_data)
        nonce, ciphertext, tag = encrypted_bytes[:12], encrypted_bytes[12:-16], encrypted_bytes[-16:]  # Fix nonce size

        cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)

        # If AAD was used in encryption, add it during decryption
        if aad:
            cipher.update(aad.encode())

        decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)

        return decrypted_data.decode()
    except ValueError as e:
        logging.error(f"Decryption failed: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected decryption error: {e}")
        return None

def encrypt_dataframe(df, encrypt_columns):
    """Encrypts specified columns in a dataframe using AES-GCM."""
    if df.empty:
        logging.warning("Received an empty DataFrame. Skipping encryption.")
        return df

    missing_cols = [col for col in encrypt_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns in DataFrame: {missing_cols}")

    plain_key, encrypted_key = get_encrypt_key()
    if plain_key is None:
        logging.error("Encryption key generation failed. Returning unmodified DataFrame.")
        return df

    encrypted_df = df.copy()
    for col in encrypt_columns:
        encrypted_df[col] = df[col].apply(lambda x: encrypt_aes_gcm(x, plain_key) if pd.notna(x) else x)

    encrypted_df["EncryptedKey"] = encrypted_key
    logging.info("Data encryption completed successfully.")
    return encrypted_df

def decrypt_dataframe(df, decrypt_columns):
    """Decrypts specified columns in a dataframe using AES-GCM."""
    if df.empty:
        logging.warning("Received an empty DataFrame. Skipping decryption.")
        return df

    if "EncryptedKey" not in df.columns:
        raise ValueError("Missing 'EncryptedKey' column. Cannot decrypt without encryption key.")

    kms_client = aws_config()
    if not kms_client:
        logging.error("Failed to initialize AWS KMS client. Returning unmodified DataFrame.")
        return df

    decrypted_rows = []
    for _, row in df.iterrows():
        try:
            encrypted_key = row["EncryptedKey"]
            decrypted_key_response = kms_client.decrypt(CiphertextBlob=base64.b64decode(encrypted_key))

            if "Plaintext" not in decrypted_key_response:
                logging.error("AWS KMS did not return a valid decryption key.")
                decrypted_rows.append(row)
                continue

            plain_key = decrypted_key_response["Plaintext"]

            for col in decrypt_columns:
                if pd.notna(row[col]):
                    decrypted_value = decrypt_aes_gcm(row[col], plain_key)
                    if decrypted_value is None:
                        logging.error(f"Failed to decrypt column {col} in row {row.name}")
                    row[col] = decrypted_value

            decrypted_rows.append(row)

        except Exception as e:
            logging.error(f"Row-level decryption failed: {e}")
            decrypted_rows.append(row)

    decrypted_df = pd.DataFrame(decrypted_rows)
    decrypted_df.drop(columns=["EncryptedKey"], inplace=True)

    logging.info("Data decryption completed successfully.")
    return decrypted_df

def convert_debit_credit_to_float(df):
    """
    Converts 'Debit' and 'Credit' columns in a DataFrame from string to float.
    Handles missing values and incorrect formats.
    """
    for col in ["Debit", "Credit"]:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)                      # Ensure all values are string
                .str.replace(",", "")             # Remove thousands separator if present
                .str.replace("₹", "")             # Remove currency symbols if present
                .str.strip()                      # Remove leading/trailing spaces
                .replace("", "0")                 # Replace empty strings with "0"
                .astype(float)                    # Convert to float
            )
    return df