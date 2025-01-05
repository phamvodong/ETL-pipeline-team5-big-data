import os
import time
import praw
import pandas as pd

# Reddit API credentials
REDDIT_CLIENT_ID = "cvn2EH5C4HP5LifPPvHDvA"
REDDIT_CLIENT_SECRET = "kC_u2qJLXOwXficJEFrYUQppiIfqjw"
REDDIT_USER_AGENT = "script:KN1111:1.0 (by u/LessCase7928)"

# Authenticate Reddit
reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID, client_secret=REDDIT_CLIENT_SECRET, user_agent=REDDIT_USER_AGENT)

# Ensure directories exist
reddit_directory_path = "data/reddit"
if not os.path.exists(reddit_directory_path):
    os.makedirs(reddit_directory_path)

def fetch_reddit_data(subreddits, keywords, limit=100):
    # Initialize an empty list for the data
    data = []
    post_ids = set()  # Set to store the post IDs and prevent duplicates

    # Retry logic for rate limit
    while True:
        try:
            for subreddit in subreddits:
                print(f"Fetching data from subreddit: {subreddit}")  # Debug print to track progress
                try:
                    subreddit_data = reddit.subreddit(subreddit)
                    for post in subreddit_data.search(" OR ".join(keywords), limit=limit):
                        if post.id not in post_ids:  # Check if the post has already been added
                            post_ids.add(post.id)  # Add the post ID to the set
                            data.append({
                                'subreddit': subreddit,
                                'title': post.title,
                                'content': post.selftext,
                                'author': post.author.name if post.author else None,
                                'upvotes': post.score,
                                'num_comments': post.num_comments,
                                'created_utc': post.created_utc,
                                'post_id': post.id  # Include the post ID for reference
                            })
                            print(f"Retrieved {len(data)} posts from {subreddit}.")
                        else:
                            print(f"Skipping duplicate post: {post.id}")
                except praw.exceptions.PRAWException as e:
                    print(f"Error occurred while fetching posts from {subreddit}: {e}")
                    continue  # Continue with the next subreddit if one fails
                except Exception as e:
                    print(f"An unexpected error occurred while fetching from {subreddit}: {e}")
                    continue  # Continue with the next subreddit if one fails

            # Save data once retrieved
            if data:
                reddit_data = pd.DataFrame(data)
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                reddit_data.to_csv(f"{reddit_directory_path}/reddit_data_{timestamp}.csv", index=False)
                print(f"Reddit data saved locally with {len(reddit_data)} records.")
            return reddit_data

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break  # Break if there's another error, as we don't want to retry indefinitely

# Example usage
if __name__ == "__main__":
    reddit_subreddits = [
        "aiart", "DefendingAIArt", "AIArtCreator", "ArtistHate", "aiwars", "AIHaters", "Human_Artists_Info", "art", "artists", "COPYRIGHT", "Deepfakes"
    ]
    reddit_keywords = [
    # Supporting AI
    "AI art", "AI tools", "GAN", "Deepfake", "DALL-E", "MidJourney",
    "AI video", "Stable Diffusion", "AI creator", "AI future",

    # Opposing AI
    "Anti AI", "AI theft", "Stop AI", "No AI", "Ban AI",
    "Stealing art", "AI fake", "Protect art", "Human art", "AI harm"
]

    reddit_data = fetch_reddit_data(reddit_subreddits, reddit_keywords)
