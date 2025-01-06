import boto3
import json

class KinesisProducer:
    def __init__(self):
        self.client = boto3.client('kinesis')
        self.stream_name = 'social-media-stream'
    
    def send_data(self, data):
        try:
            response = self.client.put_record(
                StreamName=self.stream_name,
                Data=json.dumps(data),
                PartitionKey=str(data.get('id', '1'))
            )
            return response
        except Exception as e:
            print(f"Error sending to Kinesis: {e}")
            return None