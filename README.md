# DS4300_Final_Project

Outfit Upload & Random Outfit Generator App
A Streamlit-based web app that allows users to upload clothing items and generate random outfits. Uploaded images are stored in Amazon S3, and metadata (brand, color, price, category) is stored in an RDS MySQL database via a Lambda trigger.


Features
- Upload clothes with details: image, brand, color, price, category.
- Generate a complete random outfit (shirt, bottoms, shoes).
- Display each item with its image and metadata.
- Calculate and show total outfit price.
- Uses AWS S3 for image storage and AWS RDS for metadata storage.
- Lambda function triggers on new S3 uploads to insert metadata into RDS.


Tech Stack
- Streamlit — for the frontend
- AWS S3 — for storing uploaded images
- AWS Lambda — for processing S3 upload events
- AWS RDS (MySQL) — for storing clothing metadata
- boto3 — AWS Python SDK
- pymysql — MySQL connector
- dotenv — environment variable management


Architecture Overview
User (Streamlit UI)
     |
     v
Uploads Image + Metadata
     |
     v
Amazon S3 (Bucket: uploads/)
     |
     v
Lambda Trigger
     |
     v
Stores metadata in RDS (MySQL)

When generating a random outfit, the Streamlit app queries the RDS for one random item per category, then fetches the corresponding images from S3 using signed URLs.


Create a .env file in the root directory:
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-2
S3_BUCKET_NAME=your-s3-bucket-name

DB_HOST=your-rds-endpoint
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_NAME=your-db-name
DB_PORT=3306
