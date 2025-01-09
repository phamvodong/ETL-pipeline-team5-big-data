import json
import boto3
import pandas as pd
from datetime import datetime
import re
import logging
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def clean_text(text):
    try:
        if not text:
            return ""
        text = re.sub(r'http\S+', '', text)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        return ' '.join(text.split())
    except Exception as e:
        logger.error(f"Error cleaning text: {str(e)}")
        return ""

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
    try:
        logger.info(f"Processing event: {json.dumps(event)}")
        request_id = context.aws_request_id
        logger.info(f"Request ID: {request_id}")

        s3 = boto3.client('s3')
        source_bucket = event['Records'][0]['s3']['bucket']['name']
        source_key = event['Records'][0]['s3']['object']['key']
        dest_bucket = 'processed-data-social-comment'
        
        try:
            response = s3.get_object(Bucket=source_bucket, Key=source_key)
            df = pd.read_csv(response['Body'])
            logger.info(f"Successfully loaded CSV with {len(df)} rows")
        except ClientError as e:
            logger.error(f"Failed to read source file {source_key}: {str(e)}")
            return {'statusCode': 500, 'error': 'Failed to read source file'}
        
        processed_count = 0
        error_count = 0
        
        for _, row in df.iterrows():
            try:
                comments = parse_comments(row['comments'])
                # Skip if comments is empty
                if not comments:
                    logger.info(f"Skipping video {row['id']} due to empty comments")
                    continue
                    
                processed_item = {
                    'source': 'youtube',
                    'id': str(row['id']),
                    'title': clean_text(str(row['title'])),
                    'content': clean_text(str(row['description'])),
                    'comments': comments,
                    'created_utc': int(datetime.strptime(row['published_at'], '%Y-%m-%dT%H:%M:%SZ').timestamp()),
                    'timestamp': int(datetime.now().timestamp()),
                    'partition_date': datetime.now().strftime('%Y-%m-%d')
                }
                
                dest_key = f"youtube/partition_date={processed_item['partition_date']}/{processed_item['id']}.json"
                
                try:
                    s3.put_object(
                        Bucket=dest_bucket,
                        Key=dest_key,
                        Body=json.dumps(processed_item),
                        ContentType='application/json'
                    )
                    processed_count += 1
                except ClientError as e:
                    logger.error(f"Failed to write {dest_key}: {str(e)}")
                    error_count += 1
                    
            except Exception as e:
                logger.error(f"Error processing row {row.get('video_id', 'unknown')}: {str(e)}")
                error_count += 1
                continue
        
        logger.info(f"Processing complete. Processed: {processed_count}, Errors: {error_count}")
        return {
            'statusCode': 200,
            'body': json.dumps({
                'processed': processed_count,
                'errors': error_count,
                'requestId': request_id
            })
        }
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'requestId': context.aws_request_id
            })
        }