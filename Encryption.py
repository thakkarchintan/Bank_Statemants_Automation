import base64
import boto3
from dotenv import load_dotenv
from botocore.exceptions import NoCredentialsError
import botocore.exceptions
import os 

load_dotenv()

def aws_config():
    # Replace with your actual credentials
    aws_access_key = os.getenv("AWS_ACCESS_KEY")
    aws_secret_key = os.getenv("AWS_SCRETE_KEY")
    aws_region = "ap-south-1"  # Change to your AWS region

    # Configure Boto3 session
    session = boto3.Session(
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=aws_region
    )

    # Create an AWS client (Example: KMS client)
    try:
        print("AWS Configuration Successful! ✅")
        return session.client("kms")
    except NoCredentialsError:
        print("Error: AWS credentials not found or incorrect.")
        
def get_encrypt_key():
    try:
        kms_client = aws_config()
        if not kms_client:
            raise Exception("Failed to initialize AWS KMS client.")

        response = kms_client.generate_data_key(
            KeyId="alias/Fintellect_Key",  # Use alias or actual Key ID
            KeySpec="AES_256"
        )
        
        plaintext_key = base64.b64encode(response['Plaintext']).decode()  # For encryption
        encrypted_key = base64.b64encode(response['CiphertextBlob']).decode()  # Store securely
        
        return plaintext_key, encrypted_key
    
    except botocore.exceptions.ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == "NotFoundException":
            print("Error: The specified KMS key was not found.")
        elif error_code == "AccessDeniedException":
            print("Error: Access denied. Check IAM permissions for the KMS key.")
        elif error_code == "ValidationException":
            print("Error: Invalid parameters passed to AWS KMS.")
        else:
            print(f"An AWS ClientError occurred: {e}")
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return None, None  # Return None in case of failurex



