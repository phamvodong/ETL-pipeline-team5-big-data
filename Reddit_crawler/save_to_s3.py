import boto3
import os

# AWS S3 credentials
AWS_ACCESS_KEY = "your_aws_access_key"
AWS_SECRET_KEY = "your_aws_secret_key"
BUCKET_NAME = "your_bucket_name"

# S3 Client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

# Function to upload files
def upload_to_s3(file_path, s3_folder):
    file_name = os.path.basename(file_path)
    s3_path = f"{s3_folder}/{file_name}"
    s3_client.upload_file(file_path, BUCKET_NAME, s3_path)
    print(f"Uploaded {file_path} to s3://{BUCKET_NAME}/{s3_path}")

# Example usage
if __name__ == "__main__":
    # Define local folders and S3 folders
    local_files = [
        ("data/twitter/twitter_data.csv", "social_media/twitter"),
        ("data/reddit/reddit_data.csv", "social_media/reddit"),
    ]

    # Upload each file
    for local_file, s3_folder in local_files:
        upload_to_s3(local_file, s3_folder)
