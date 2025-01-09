import json
import boto3
import pandas as pd
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def parse_comments(comments_str):
    try:
        if not comments_str or not isinstance(comments_str, str):
            return []
        # Remove invalid characters and try to evaluate
        clean_str = comments_str.replace('||', ',').strip('[]')
        comments_list = [comment.strip(' "\'') for comment in clean_str.split(',') if comment.strip()]
        return comments_list
    except Exception as e:
        logger.error(f"Error parsing comments: {str(e)}")
        return []

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
                comments = parse_comments(row['comments'])
                # Skip if comments is empty
                if not comments:
                    logger.info(f"Skipping post {row['post_id']} due to empty comments")
                    continue
                    
                processed_item = {
                    'source': 'reddit',
                    'id': str(row['post_id']),
                    'title': str(row['title']),
                    'content': str(row['content']),
                    'comments': comments,
                    'created_utc': int(row['created_utc']),
                    'timestamp': int(datetime.now().timestamp()),
                    'partition_date': datetime.now().strftime('%Y-%m-%d')
                }
                
                # Save to processed bucket
                dest_key = f"reddit/partition_date={processed_item['partition_date']}/{processed_item['id']}.json"
                s3.put_object(
                    Bucket=dest_bucket,
                    Key=dest_key,
                    Body=json.dumps(processed_item),
                    ContentType='application/json'
                )
                processed_count += 1
                
            except Exception as row_error:
                logger.error(f"Error processing row with post_id {row.get('post_id', 'unknown')}: {str(row_error)}")
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