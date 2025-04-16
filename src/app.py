import streamlit as st
import boto3
import io
import os
import random
from dotenv import load_dotenv
from datetime import datetime
from PIL import Image
import pymysql 






# Load environment variables from .env file
def load_env_variables():
    load_dotenv()
    return {
        "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
        "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "aws_region": os.getenv("AWS_REGION", "us-east-2"),
        "s3_bucket_name": os.getenv("S3_BUCKET_NAME"),
        "db_host": os.getenv("DB_HOST"),
        "db_user": os.getenv("DB_USER"),
        "db_password": os.getenv("DB_PASSWORD"),
        "db_name": os.getenv("DB_NAME"),
        "db_port": int(os.getenv("DB_PORT", 3306)),
    }


# upload the selected file to the s3 bucket into uploads folder.
# def upload_to_s3(s3_client, file, bucket_name, key):
#     try: 
#         s3_client.upload_fileobj(
#             file, bucket_name, key
#         )
#         print(f"Successfully uploaded {file.name} to S3")
#     except Exception as e:
#         print(f"Error uploading {file.name}: {str(e)}")

def get_db_connection(env):
    return pymysql.connect(
        host=env['db_host'],
        user=env['db_user'],
        password=env['db_password'],
        database=env['db_name'],
        port=env['db_port'],
        cursorclass=pymysql.cursors.DictCursor
    )


# Get a random item per category
def get_random_item(env, category):
    connection = get_db_connection(env)
    with connection:
        with connection.cursor() as cursor:
            query = f"""
                SELECT key, brand, color, price 
                FROM uploads
                WHERE category = %s 
                ORDER BY RAND() LIMIT 1;
            """
            cursor.execute(query, (category,))
            result = cursor.fetchone()
    return result

def main():
    tab1, tab2 = st.tabs(['Upload Outfit', 'Random Outfit Generator'])

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

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=aws_credentials["aws_access_key_id"],
        aws_secret_access_key=aws_credentials["aws_secret_access_key"],
        region_name=aws_credentials["aws_region"],
    )

    with tab1: 
        st.title('Upload Clothes')

        uploaded_photo = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"])
        color = st.text_input("Color")
        brand = st.text_input("Brand")
        price = st.number_input("Price", min_value=0.0, format="%.2f")
        category = st.selectbox(
            "Category",
            options=["Shirts", "Bottoms", "Shoes"],
            index=0
        )


        if st.button("Upload"):
            if uploaded_photo and color and brand and price > 0:
                try: 
                    filename = uploaded_photo.name.replace(" ", "_")
                    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
                    s3_key = f"{category}/{category}_{filename}_{brand}_{color}_{timestamp}"

                    s3_client.upload_fileobj(
                            uploaded_photo,
                            aws_credentials["s3_bucket_name"],
                            s3_key,
                            ExtraArgs={
                                # "ContentType": uploaded_photo.type,
                                "Metadata": {
                                    "brand": brand,
                                    "color": color,
                                    "price": str(price),
                                    "category": category
                                }
                            }
                        )
                    
                    # print(f"Successfully uploaded {filename} to S3")
                    st.success(f'Successfully uploaded {filename} to S3')

                    # Clear form after upload
                    st.session_state.uploaded_photo = None
                    st.session_state.color = ""
                    st.session_state.brand = ""
                    st.session_state.price = 0.0
                    st.session_state.category = "Shirts"
                    
                except Exception as e:
                    st.error(f"Upload failed: {str(e)}")
                    # print(f"Error uploading {filename}: {str(e)}")
            else:
                st.warning("Please fill in all fields before uploading.")



    with tab2: 
        st.header("Generate Random Outfit")

        if st.button("Generate Outfit"):
            categories = ["Shirt", "Bottoms"] # , "Shoes"]
            outfit = {}
            total_price = 0

            for category in categories:
                item = get_random_item(aws_credentials, category)
                if item:
                    outfit[category] = item
                    total_price += float(item['price'])

            st.subheader("Your Random Outfit:")
            for category in categories:
                item = outfit.get(category)
                if item:
                    st.markdown(f"**{category.title()}** - Brand: `{item['brand']}`, Color: `{item['color']}`, Price: `${item['price']}`")

            st.markdown("---")
            st.subheader(f"💰 Total Price: ${total_price:.2f}")



    

if __name__ == "__main__":
    main()


