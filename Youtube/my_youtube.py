import os
import time
from googleapiclient.discovery import build
from datetime import datetime
import re
import pandas as pd
import csv
from pathlib import Path

# YouTube API credentials
API_KEY = "AIzaSyBVytj9ZoAOVtHq2Pjs_T2w0TMc64axYiU"
youtube = build('youtube', 'v3', developerKey=API_KEY)

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    return ' '.join(text.split())

def save_to_csv(data, filename):
    output_dir = Path('youtube_data')
    output_dir.mkdir(exist_ok=True)
    
    file_path = output_dir / filename
    file_exists = file_path.exists()
    
    with open(file_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys() if data else [])
        if not file_exists:
            writer.writeheader()
        writer.writerows(data)

def fetch_youtube_data(search_queries, max_results=1000):
    start_date = datetime(2010, 1, 1).isoformat() + 'Z'
    all_videos = []
    
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
                        maxResults=10000
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
                    'id': video_id,
                    'title': clean_text(video['snippet']['title']),
                    'description': clean_text(video['snippet']['description']),
                    'published_at': video['snippet']['publishedAt'],
                    'comments': '||'.join(comments),  # Join comments with delimiter
                    'comments_disabled': comments_disabled,
                    'search_query': query,
                    'timestamp': int(time.time())
                }
                
                all_videos.append(video_data)

        except Exception as e:
            print(f"Error fetching videos for query {query}: {e}")
            continue
            
    if all_videos:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        save_to_csv(all_videos, f'youtube_data_{timestamp}.csv')
        print(f"Saved {len(all_videos)} videos to CSV file")

if __name__ == "__main__":
    search_queries = [
        "#AIart", "#AIVideo", "#AIGenerator", "#AIAnimation", "#AICreative",
        "#AIArtwork", "#AIGenerated", "#DigitalArt", "#AIImageGeneration",
        "#ComputerArt", "#GenerativeAI", "#AICreator", "#AIDesign", "#AIInnovation",
        "#AITechnology", "#AIFuture", "#AIProgress", "#AICreativity",
        "#AIArtist", "#AIWorld", "#AIRevolution", "#AITrends", "#AIEvolution",
        "#AIDevelopment", "#AIResearch", "#AIScience", "#AIIndustry",
        "AI art", "AI tools", "GAN", "Deepfake", "DALL-E", "MidJourney",
        "AI video", "Stable Diffusion", "AI creator", "AI future",
        "AI innovation", "AI progress", "AI technology", "AI advancements",
        "AI benefits", "AI creativity", "AI potential", "AI generation",
        "AI development", "AI research", "AI industry", "AI transformation",
        "AI evolution", "AI revolution", "AI breakthroughs", "AI achievements",
        "Anti AI", "AI theft", "Stop AI", "No AI", "Ban AI",
        "Stealing art", "AI fake", "Protect", "Human art", "AI harm",
        "AI danger", "AI risks", "AI threat", "AI concerns", "AI ethics",
        "AI regulation", "AI impact", "AI controversy", "AI debate",
        "AI infringement", "AI lawsuit", "AI copyright", "AI exploitation",
        "AI manipulation", "AI fraud", "AI deception", "AI problems",
        "AI drawbacks", "AI limitations", "AI challenges", "AI issues"
    ]
    fetch_youtube_data(search_queries)