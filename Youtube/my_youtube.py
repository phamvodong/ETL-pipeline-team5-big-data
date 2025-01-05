from googleapiclient.discovery import build

# YouTube API Key
API_KEY = "YOUR_YOUTUBE_API_KEY"  # Replace with your API key

# Build the YouTube client
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Search for videos with a specific keyword/hashtag
search_query = "#AIArt"  # Replace with your desired hashtag/keyword
search_response = youtube.search().list(
    q=search_query,
    part="snippet",
    type="video",
    maxResults=10
).execute()

# Process videos
print(f"Fetching videos with '{search_query}'...\n")
for video in search_response.get('items', []):
    video_id = video['id']['videoId']
    video_title = video['snippet']['title']
    video_channel = video['snippet']['channelTitle']

    # Fetch video details
    video_details = youtube.videos().list(
        part="statistics",
        id=video_id
    ).execute()

    video_stats = video_details['items'][0]['statistics']
    comment_count = int(video_stats.get('commentCount', 0))

    # Print video details
    print(f"Video Title: {video_title}")
    print(f"Channel: {video_channel}")
    print(f"Views: {video_stats.get('viewCount', 0)}")
    print(f"Likes: {video_stats.get('likeCount', 0)}")
    print(f"Comments: {comment_count}")
    print(f"URL: https://www.youtube.com/watch?v={video_id}")
    print("-" * 40)

    # Fetch comments if available
    if comment_count > 0:
        print("Fetching comments...\n")
        comments_response = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=5
        ).execute()

        for comment in comments_response.get('items', []):
            comment_snippet = comment['snippet']['topLevelComment']['snippet']
            comment_author = comment_snippet['authorDisplayName']
            comment_text = comment_snippet['textDisplay']
            comment_likes = comment_snippet['likeCount']

            print(f"  Comment by {comment_author}:")
            print(f"  {comment_text}")
            print(f"  Likes: {comment_likes}")
            print("  " + "-" * 30)
    else:
        print("No comments found for this video.")
    
    print("=" * 50)
