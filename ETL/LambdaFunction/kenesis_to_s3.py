import json
import boto3
import base64
from datetime import datetime

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    bucket_name = 'raw-social-data'
    
    for record in event['Records']:
        try:
            # Decode Kinesis data
            payload = base64.b64decode(record['kinesis']['data'])
            data = json.loads(payload)
            
            # Generate key based on source and timestamp
            source = data['source']
            timestamp = datetime.now()
            
            key = f"{source}/{timestamp.strftime('%Y/%m/%d/%H')}/{data['id']}.json"
            
            # Store in S3
            s3.put_object(
                Bucket=bucket_name,
                Key=key,
                Body=json.dumps(data),
                ContentType='application/json'
            )
            
        except Exception as e:
            print(f"Error processing record: {e}")
            continue
    
    return {'statusCode': 200}