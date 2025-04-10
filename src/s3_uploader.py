import os
import time
import random
from pathlib import Path
import boto3
from dotenv import load_dotenv

# The folder where source files live
DATA_FOLDER = "/Users/tristanco/Desktop/25s-s3-upload-example/clothes"
# How frequently to upload a file, in seconds
UPLOAD_INTERVAL = 2
# Total number of uploads to perform (optional, can be adjusted)
NUM_UPLOADS = 4
# The name of the s3 bucket you're uploading to
S3_BUCKET_NAME = "ds4300-project-co"


# Load the values from .env into dictionary
def load_env_variables():
    load_dotenv()
    return {
        "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
        "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "aws_region": os.getenv("AWS_REGION", "us-east-1"),
        "s3_bucket_name": os.getenv("S3_BUCKET_NAME"),
    }


# Get all PNG files from the input folder
def get_all_png_files(folder_path):
    png_files = list(Path(folder_path).glob("*.png"))  # Adjust the pattern as needed
    if not png_files:
        raise FileNotFoundError(f"No PNG files found in {folder_path}")
    return png_files


# Generate random price metadata
def generate_random_price():
    return round(random.uniform(10, 100), 2)  # Generate random price between $10.00 and $100.00


# Upload the selected file to the s3 bucket into the uploads folder with metadata
def upload_to_s3(s3_client, file_path, bucket_name):
    try:
        # Generate random price for the image
        price = generate_random_price()

        # Open the file and upload it to S3 with metadata
        with open(file_path, "rb") as file:
            s3_client.upload_fileobj(
                file,
                bucket_name,
                f"uploads/{Path(file_path).name}",
                ExtraArgs={"Metadata": {"price": str(price)}},  # Add price as metadata
            )
        
        print(f"Successfully uploaded {file_path.name} with price metadata: ${price}")
    except Exception as e:
        print(f"Error uploading {file_path.name}: {str(e)}")


def main():
    # Load AWS credentials from .env
    aws_credentials = load_env_variables()

    # Validate required environment variables
    if not aws_credentials["aws_access_key_id"]:
        raise ValueError("No AWS Access key id set")
    if not aws_credentials["aws_secret_access_key"]:
        raise ValueError("No AWS Secret Access key set")
    if not aws_credentials["aws_region"]:
        raise ValueError("No AWS Region Set")
    if not aws_credentials["s3_bucket_name"]:
        raise ValueError("S3_BUCKET_NAME environment variable is not set")

    # Using the boto3 library, initialize S3 client
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=aws_credentials["aws_access_key_id"],
        aws_secret_access_key=aws_credentials["aws_secret_access_key"],
        region_name=aws_credentials["aws_region"],
    )

    print(
        f"Starting S3 uploader. Will upload all files every {UPLOAD_INTERVAL} seconds."
    )

    try:
        # Get all PNG files from the folder
        png_files = get_all_png_files(DATA_FOLDER)

        for count_uploads, file_path in enumerate(png_files, 1):
            upload_to_s3(s3_client, file_path, aws_credentials["s3_bucket_name"])

            # Wait for the specified interval before uploading the next file
            if count_uploads < len(png_files):
                print(f"Waiting {UPLOAD_INTERVAL} seconds before next upload...")
                time.sleep(UPLOAD_INTERVAL)

        print(f"Uploaded {len(png_files)} files to S3.")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
