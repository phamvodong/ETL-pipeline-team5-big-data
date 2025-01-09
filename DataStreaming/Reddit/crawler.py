import os
import time
import praw
import pandas as pd
import re
import boto3
import json
from botocore.exceptions import ClientError

class KinesisProducer:
    def __init__(self, region_name='us-west-2'):
        try:
            self.client = boto3.client('kinesis', region_name=region_name)
            self.stream_name = 'social-media-stream'
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

# Reddit API credentials
REDDIT_CLIENT_ID = "cvn2EH5C4HP5LifPPvHDvA"
REDDIT_CLIENT_SECRET = "kC_u2qJLXOwXficJEFrYUQppiIfqjw"
REDDIT_USER_AGENT = "script:KN1111:1.0 (by u/LessCase7928)"
# Authenticate Reddit
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

# Initialize Kinesis producer
producer = KinesisProducer()

# Setup directories
reddit_directory_path = "reddit_data"
if not os.path.exists(reddit_directory_path):
    os.makedirs(reddit_directory_path)

processed_ids_file = os.path.join(reddit_directory_path, "processed_ids.txt")
processed_ids = set()

if os.path.exists(processed_ids_file):
    with open(processed_ids_file, "r") as f:
        processed_ids = set(f.read().splitlines())

def fetch_reddit_data(subreddits, keywords, limit=10000):
    data = []
    new_ids = set()

    for subreddit in subreddits:
        try:
            # Verify subreddit exists first
            try:
                subreddit_data = reddit.subreddit(subreddit)
                subreddit_data.id  # This will trigger a 404 if subreddit doesn't exist
            except Exception as e:
                print(f"Subreddit {subreddit} not found or inaccessible: {e}")
                continue

            for post in subreddit_data.search(" OR ".join(keywords), limit=limit):
                if post.id not in processed_ids and post.id not in new_ids:
                    # Safely get comments
                    comments = []
                    try:
                        post.comments.replace_more(limit=0)  # Remove MoreComments objects
                        comments = [
                            remove_emojis(comment.body)
                            for comment in post.comments[:10]  # Limit to first 10 comments
                            if hasattr(comment, 'body')  # Check if it's a regular comment
                        ]
                    except Exception as e:
                        print(f"Error fetching comments for post {post.id}: {e}")

                    post_data = {
                        'source': 'reddit',
                        'id': post.id,
                        'title': remove_emojis(post.title),
                        'content': remove_emojis(post.selftext),
                        'comments': comments,
                        'created_utc': post.created_utc,
                        'subreddit': subreddit,
                        'timestamp': int(time.time())
                    }
                    producer.send_data(post_data)
                    data.append(post_data)
                    new_ids.add(post.id)

        except Exception as e:
            print(f"Error fetching from {subreddit}: {e}")
            continue

    if data:
        with open(processed_ids_file, "a") as f:
            for post_id in new_ids:
                f.write(post_id + "\n")
    
    return data

def remove_emojis(text):
    if not text:
        return ""
    emoji_pattern = re.compile("[\U00010000-\U0010ffff\U0000FF00-\U0000FFEF]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

if __name__ == "__main__":
    subreddits = ["AIart", "AIGenerator", "ArtificialIntelligence"]
    keywords = ["AI art", "AI generator", "AI creation"]
    fetch_reddit_data(subreddits, keywords)