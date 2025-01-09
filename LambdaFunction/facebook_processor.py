import json
import boto3
import pandas as pd
import logging
from datetime import datetime
import ast
import hashlib

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def parse_comments(comments_str):
    """Parse comments string into a list of comments"""
    try:
        if not comments_str or not isinstance(comments_str, str):
            return []
            
        # Convert string representation of list to actual list
        comments = ast.literal_eval(comments_str)
        
        # Ensure each comment is a string and remove empty comments
        comments = [str(comment).strip() for comment in comments if comment]
        return comments
    except Exception as e:
        logger.error(f"Error parsing comments: {str(e)}")
        return []

def extract_id_from_url(url):
    """Extract numeric ID from Facebook URL or generate hash if not found"""
    try:
        if isinstance(url, str) and 'facebook.com' in url:
            # Try to extract ID from URL format like facebook.com/xyz/123456789
            parts = url.split('/')
            for part in reversed(parts):
                if part.isdigit():
                    return part
        
        # If no numeric ID found, generate hash from URL
        hash_object = hashlib.md5(str(url).encode())
        return hash_object.hexdigest()[:16]  # Take first 16 chars of hash
    except:
        return None

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    source_key = event['Records'][0]['s3']['object']['key']
    dest_bucket = 'processed-data-social-comment'
    
    logger.info(f"Processing file {source_key} from bucket {source_bucket}")
    
    try:
        # Read CSV from source
        logger.info("Reading source CSV file")
        response = s3.get_object(Bucket=source_bucket, Key=source_key)
        df = pd.read_csv(response['Body'])
        logger.info(f"Successfully read CSV with {len(df)} rows")
        
        processed_count = 0
        # Process each row
        for _, row in df.iterrows():
            try:
                # Parse comments from string representation
                comments = parse_comments(row['comments'])
                # Skip if no valid comments
                if not comments:
                    logger.info(f"Skipping post {row['id']} due to empty comments")
                    continue
                
                # Extract numeric ID from URL
                post_id = extract_id_from_url(row['id'])
                if not post_id:
                    logger.error(f"Could not extract valid ID from {row['id']}")
                    continue
                
                # Build processed item
                processed_item = {
                    'source': 'facebook',
                    'id': post_id,  # Use extracted numeric ID
                    'title': str(row['title']),
                    'content': str(row['content']),
                    'comments': comments,
                    'created_utc': int(datetime.now().timestamp()),  # Using current time since FB data doesn't have timestamp
                    'timestamp': int(datetime.now().timestamp()),
                    'partition_date': datetime.now().strftime('%Y-%m-%d')
                }
                
                # Save to processed bucket
                dest_key = f"facebook/partition_date={processed_item['partition_date']}/{processed_item['id']}.json"
                s3.put_object(
                    Bucket=dest_bucket,
                    Key=dest_key,
                    Body=json.dumps(processed_item),
                    ContentType='application/json'
                )
                processed_count += 1
                
            except Exception as row_error:
                logger.error(f"Error processing row with id {row.get('id', 'unknown')}: {str(row_error)}")
                continue
                
        logger.info(f"Successfully processed {processed_count} items out of {len(df)} total rows")
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Successfully processed {processed_count} items',
                'total_rows': len(df)
            })
        }
        
    except Exception as e:
        error_message = f"Error processing file {source_key}: {str(e)}"
        logger.error(error_message)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': error_message
            })
        }
