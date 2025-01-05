import csv
import re
from googleapiclient.discovery import build
from datetime import datetime

def clean_text(text):
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove emojis, icons, and special characters - enhanced pattern
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text

# YouTube API Key
API_KEY = "AIzaSyBVytj9ZoAOVtHq2Pjs_T2w0TMc64axYiU"  # Replace with your API key

# Build the YouTube client
youtube = build('youtube', 'v3', developerKey=API_KEY)

# List of search queries
search_queries = ["#AIArt", "#AIVideo", "#AIGenerator", 'VideoGenerator' "#AIAnimation", "#AICreative", "#AIGenerated", "#StableDiffusion", "#MidJourney", "#AIContentCreator", "#AIVideoEditor", "#TextToVideo", "#AIImageGeneration"]
# Create CSV file with timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
csv_filename = f'youtube_data_{timestamp}.csv'

with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['Search Query', 'Video ID', 'Title', 'Comment ID', 'Comment'])

    # Process each search query
    for search_query in search_queries:
        print(f"\nFetching videos with '{search_query}'...")
        search_response = youtube.search().list(
            q=search_query,
            part="snippet",
            type="video",
            maxResults=10
        ).execute()

        # Process videos
        for video in search_response.get('items', []):
            video_id = video['id']['videoId']
            video_title = clean_text(video['snippet']['title'])

            try:
                comments_response = youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=5
                ).execute()

                for comment in comments_response.get('items', []):
                    comment_id = comment['id']
                    comment_text = clean_text(comment['snippet']['topLevelComment']['snippet']['textDisplay'])
                    
                    if comment_text.strip():
                        csvwriter.writerow([search_query, video_id, video_title, comment_id, comment_text])

            except Exception as e:
                continue

print(f"\nData has been exported to {csv_filename}")
