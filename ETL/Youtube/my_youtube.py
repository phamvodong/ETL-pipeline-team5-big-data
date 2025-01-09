import os
import time
from googleapiclient.discovery import build
from datetime import datetime
from dateutil import parser
import re
import boto3
import json
from botocore.exceptions import ClientError

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
# YouTube API credentials
API_KEY = "AIzaSyA3mzd3mYNINALY03sNSBIAqmZIL4NxZUs"
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Initialize Kinesis producer
producer = KinesisProducer()

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    return ' '.join(text.split())

def fetch_youtube_data(search_queries, max_results=1000):
    start_date = datetime(2022, 1, 1).isoformat() + 'Z'
    
    for query in search_queries:
        try:
            search_response = youtube.search().list(
                q=query,
                part="snippet",
                type="video",
                maxResults=max_results,
                publishedAfter=start_date,
                order='date'
            ).execute()

            for video in search_response.get('items', []):
                video_id = video['id']['videoId']
                comments = []
                comments_disabled = False
                
                try:
                    comments_response = youtube.commentThreads().list(
                        part="snippet",
                        videoId=video_id,
                        maxResults=100
                    ).execute()
                    
                    comments = [
                        clean_text(c['snippet']['topLevelComment']['snippet']['textDisplay'])
                        for c in comments_response.get('items', [])
                    ]

                except Exception as e:
                    if 'commentsDisabled' in str(e):
                        comments_disabled = True
                    else:
                        print(f"Error fetching comments for video {video_id}: {e}")

                video_data = {
                    'source': 'youtube',
                    'id': video_id,
                    'title': clean_text(video['snippet']['title']),
                    'description': clean_text(video['snippet']['description']),
                    'published_at': video['snippet']['publishedAt'],
                    'comments': comments,
                    'comments_disabled': comments_disabled,
                    'search_query': query,
                    'timestamp': int(time.time())
                }
                
                producer.send_data(video_data)

        except Exception as e:
            print(f"Error fetching videos for query {query}: {e}")
            continue

if __name__ == "__main__":
    search_queries = [
        "#AIart", 
        "#AIVideo", 
        "#AIGenerator",
        "#StableDiffusion",
        "#MidJourney"
    ]
    fetch_youtube_data(search_queries)