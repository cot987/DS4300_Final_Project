import streamlit as st
import boto3
import io
import os
import random
from dotenv import load_dotenv
from PIL import Image

# Load environment variables from .env file
def load_env_variables():
    load_dotenv()
    return {
        "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
        "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "aws_region": os.getenv("AWS_REGION", "us-east-1"),
        "s3_bucket_name": os.getenv("S3_BUCKET_NAME"),
    }

# Streamlit page setup
st.set_page_config(page_title="👕 Outfit Picker", layout="wide")
st.title("🛍️ Outfit Picker from S3")

# Load environment variables
env_vars = load_env_variables()
bucket_name = env_vars["s3_bucket_name"]
region = env_vars["aws_region"]

# Categories to fetch (with dash)
categories = ["shirt", "pants", "shoes", "hat"]

# Get a random image and its price for a specific category
def get_image_and_price(bucket, folder, category_prefix):
    s3_client = boto3.client(
        "s3",
        region_name=region,
        aws_access_key_id=env_vars["aws_access_key_id"],
        aws_secret_access_key=env_vars["aws_secret_access_key"],
    )

    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=folder)
    if "Contents" not in response:
        return None, None

    # Filter files that start with "category-" and are image types
    category_images = [
        obj["Key"]
        for obj in response["Contents"]
        if obj["Key"].startswith(f"{folder}{category_prefix}-") and obj["Key"].lower().endswith((".png", ".jpg", ".jpeg"))
    ]

    if not category_images:
        return None, None

    # Choose random image from that category
    selected_key = random.choice(category_images)
    obj = s3_client.get_object(Bucket=bucket, Key=selected_key)

    image = Image.open(io.BytesIO(obj["Body"].read()))
    price = obj.get("Metadata", {}).get("price", None)

    return image, price

# Button to trigger outfit selection
if st.button("🎲 Pick Random Outfit"):
    with st.spinner("Loading outfit pieces..."):
        try:
            total_price = 0
            images = []
            captions = []

            for cat in categories:
                image, price = get_image_and_price(bucket_name, "uploads/", cat)
                if image:
                    display_price = float(price) if price else 0
                    images.append(image)
                    captions.append(f"{cat.capitalize()} - ${display_price:.2f}" if price else f"{cat.capitalize()} - Price N/A")
                    total_price += display_price
                else:
                    st.warning(f"No images found for category: {cat}")

            # Display all images in a row
            if images:
                cols = st.columns(len(images))
                for i, col in enumerate(cols):
                    with col:
                        col.image(images[i], caption=captions[i], use_container_width=True)

                st.markdown("---")
                st.subheader(f"🧾 Total Outfit Price: ${total_price:.2f}")

        except Exception as e:
            st.error(f"Something went wrong: {e}")
