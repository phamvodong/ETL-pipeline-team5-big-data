import os
import time
import boto3
import json
from botocore.exceptions import ClientError
from datetime import datetime
from ..utils.data_formatter import read_csv_data, format_local_data
import json
import pandas as pd
from datetime import datetime

def format_local_data(df):
    """
    Format local data into the expected structure for S3/Kinesis
    
    Args:
        df: Pandas DataFrame with columns: 
            title, content, num_comments, comments, created_utc, post_id
    
    Returns:
        List of formatted dictionaries ready for upload
    """
    formatted_data = []
    timestamp = int(datetime.now().timestamp())
    
    for _, row in df.iterrows():
        # Parse comments from string representation
        comments = row['comments']
        if isinstance(comments, str):
            comments = eval(comments)  # Convert string repr of list to actual list
            
        formatted_item = {
            'source': 'reddit',
            'id': row['post_id'],
            'title': row['title'] if pd.notna(row['title']) else '',
            'content': row['content'] if pd.notna(row['content']) else '',
            'comments': comments if isinstance(comments, list) else [],
            'created_utc': int(row['created_utc']),
            'subreddit': 'local_upload',  # Default for local data
            'timestamp': timestamp
        }
        formatted_data.append(formatted_item)
        
    return formatted_data

def read_csv_data(filepath):
    """Helper to read CSV/TSV data into DataFrame"""
    try:
        df = pd.read_csv(filepath, sep='\t')
    except:
        df = pd.read_csv(filepath)
    return df


def upload_csv_to_s3(file_path, bucket_name='raw-social-data'):
    """
    Upload CSV file data to S3 following the same structure as fetched data
    """
    try:
        s3 = boto3.client('s3')
        
        # Read and format CSV data
        df = read_csv_data(file_path)
        processed_data = format_local_data(df)
            
        # Upload to S3 following the same directory structure
        current_time = datetime.now()
        failed_uploads = []
        
        for item in processed_data:
            try:
                # Use same path structure that Lambda expects
                key = f"reddit/{current_time.strftime('%Y/%m/%d/%H')}/{item['id']}.json"
                
                s3.put_object(
                    Bucket=bucket_name,
                    Key=key,
                    Body=json.dumps(item),
                    ContentType='application/json'
                )
                print(f"Uploaded {item['id']} to s3://{bucket_name}/{key}")
                
                # Also send to Kinesis stream
                producer.send_data(item)
                
            except Exception as e:
                failed_uploads.append({
                    'id': item['id'],
                    'error': str(e)
                })
        
        return {
            'status': 'success',
            'items_processed': len(processed_data),
            'failed_uploads': failed_uploads,
            'timestamp': current_time.isoformat()
        }
        
    except Exception as e:
        print(f"Error uploading CSV file: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }

if __name__ == "__main__":
    csv_file = "path/to/your/reddit_data.csv"  # Update this path
    result = upload_csv_to_s3(csv_file)
    print(json.dumps(result, indent=2))
