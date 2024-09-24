import json
import boto3
import urllib.request
import os
import ssl

def create_s3_bucket(bucket_name):
    """
    Create an S3 bucket.
    """
    s3 = boto3.client('s3')
    try:
        s3.create_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' created successfully.")
    except Exception as e:
        print(f"Error creating bucket: {e}")

def upload_image_to_s3(bucket_name, image_url):
    """
    Upload an image to S3 bucket.
    """
    try:
        image_name = os.path.basename(image_url)
        urllib.request.urlretrieve(image_url, image_name)
        s3 = boto3.client('s3')
        s3.upload_file(image_name, bucket_name, image_name)
        print(f"Uploaded {image_name} to S3 bucket '{bucket_name}'.")
        os.remove(image_name)  # Remove the local image file after upload
    except Exception as e:
        print(f"Error uploading image to S3: {e}")

if __name__ == "__main__":
    # Disable SSL certificate verification
    ssl._create_default_https_context = ssl._create_unverified_context

    # Read JSON data
    with open('a1.json') as file:
        data = json.load(file)

    # Extract image URLs
    image_urls = [song['img_url'] for song in data['songs']]

    # Create S3 bucket
    bucket_name = 'mymusicbckt'
    create_s3_bucket(bucket_name)

    # Upload images to S3 bucket
    for url in image_urls:
        upload_image_to_s3(bucket_name, url)
