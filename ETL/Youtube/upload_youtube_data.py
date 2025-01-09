import os
import time
import boto3
import json
from botocore.exceptions import ClientError
from datetime import datetime
import re

class KinesisProducer:
    def __init__(self, region_name='us-west-2'):
        try:
            self.client = boto3.client('kinesis', region_name=region_name)
            self.stream_name = 'team5-social-media-stream'
        except ClientError as e:
            print(f"Error initializing Kinesis client: {e}")
            raise
    
    def send_data(self, data):
        try:
            response = self.client.put_record(
                StreamName=self.stream_name,
                Data=json.dumps(data),
                PartitionKey=str(data.get('id', '1'))
            )
            return response
        except ClientError as e:
            print(f"Error sending to Kinesis: {e}")
            return None

# Initialize Kinesis producer
producer = KinesisProducer()

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    return ' '.join(text.split())

def upload_youtube_data(input_file, bucket_name='raw-social-data'):
    """
    Upload YouTube data from local JSON file to S3 and Kinesis
    """
    try:
        s3 = boto3.client('s3')
        
        # Read local file
        with open(input_file, 'r') as file:
            video_data = json.load(file)
            
        # Ensure data follows expected structure
        processed_data = {
            'source': 'youtube',
            'id': video_data.get('id'),
            'title': clean_text(video_data.get('title', '')),
            'description': clean_text(video_data.get('description', '')),
            'published_at': video_data.get('published_at'),
            'comments': [clean_text(c) for c in video_data.get('comments', []) if c],
            'comments_disabled': video_data.get('comments_disabled', False),
            'search_query': video_data.get('search_query', ''),
            'timestamp': int(time.time())
        }
        
        # Upload to S3
        current_time = datetime.now()
        key = f"youtube/{current_time.strftime('%Y/%m/%d/%H')}/{processed_data['id']}.json"
        
        s3.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=json.dumps(processed_data),
            ContentType='application/json'
        )
        print(f"Uploaded to S3: s3://{bucket_name}/{key}")
        
        # Send to Kinesis stream
        kinesis_response = producer.send_data(processed_data)
        print(f"Sent to Kinesis stream: {kinesis_response}")
        
        return {
            'status': 'success',
            'uploaded_file': key,
            'timestamp': current_time.isoformat()
        }
        
    except Exception as e:
        print(f"Error uploading YouTube data: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }

if __name__ == "__main__":
    input_file = "path/to/your/youtube_data.json"  # Update this path
    result = upload_youtube_data(input_file)
    print(json.dumps(result, indent=2))
