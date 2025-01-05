import os
import time
import praw
import pandas as pd
import re

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

# Path for storing processed IDs
processed_ids_file = os.path.join(reddit_directory_path, "processed_ids.txt")

# Load existing processed IDs
if os.path.exists(processed_ids_file):
    with open(processed_ids_file, "r") as f:
        processed_ids = set(f.read().splitlines())
else:
    processed_ids = set()


def clear_processed_ids():
    with open(processed_ids_file, 'w') as f:
        pass  # Open and close the file without writing anything, effectively clearing it.
    print("Processed IDs cleared.")


def delete_processed_ids():
    if os.path.exists(processed_ids_file):
        os.remove(processed_ids_file)
        print("Processed IDs file deleted.")
    else:
        print("Processed IDs file does not exist.")


def fetch_reddit_data(subreddits, keywords, limit=10000):
    data = []
    new_ids = set()

    for subreddit in subreddits:
        print(f"Fetching data from subreddit: {subreddit}")
        try:
            subreddit_data = reddit.subreddit(subreddit)
            for post in subreddit_data.search(" OR ".join(keywords), limit=limit):
                if post.id not in processed_ids and post.id not in new_ids:
                    new_ids.add(post.id)
                    data.append({
                    # 'subreddit': post.subreddit.display_name,
                    'title':  remove_emojis(post.title),
                    'content':  remove_emojis(post.selftext),
                    # 'author': post.author.name if post.author else None,
                    # 'upvotes': post.score,
                    # 'downvotes': post.downs,
                    'num_comments': post.num_comments,
                    # 'comments': [comment.body.encode('ascii', 'ignore').decode('ascii') for comment in post.comments],
                    'comments': [remove_emojis(comment.body.encode('ascii', 'ignore').decode('ascii')) for comment in post.comments],
                    'created_utc': post.created_utc,
                    'post_id': post.id
                    })
                    print(f"Added post: {post.id} - {post.title}")
                else:
                    print(f"Skipped duplicate post: {post.id}")
        except Exception as e:
            print(f"Error while fetching from {subreddit}: {e}")
            continue

    if data:
        # Save new data to CSV
        reddit_data = pd.DataFrame(data)
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        reddit_data.to_csv(f"{reddit_directory_path}/reddit_data_{timestamp}.csv", index=False)
        print(f"Saved {len(reddit_data)} new posts to CSV.")

        # Update the processed IDs file
        with open(processed_ids_file, "a") as f:
            for post_id in new_ids:
                f.write(post_id + "\n")
        print(f"Updated processed IDs file with {len(new_ids)} new IDs.")
    else:
        print("No new posts to save.")
    return data


def remove_emojis(text):
    # Regular expression to match emojis
    emoji_pattern = re.compile("[\U00010000-\U0010ffff\U0000FF00-\U0000FFEF]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def fetch_reddit_data_with_only_keywords(keywords, limit=1000000):
    data = []
    new_ids = set()

    print(f"Fetching data from all of Reddit")

    try:
        # Search across all of Reddit using 'all' subreddit
        for post in reddit.subreddit('all').search(" OR ".join(keywords), limit=limit):
            if post.id not in processed_ids and post.id not in new_ids:
                new_ids.add(post.id)
                data.append({
                    # 'subreddit': post.subreddit.display_name,
                    'title':  remove_emojis(post.title),
                    'content':  remove_emojis(post.selftext),
                    # 'author': post.author.name if post.author else None,
                    # 'upvotes': post.score,
                    # 'downvotes': post.downs,
                    'num_comments': post.num_comments,
                    # 'comments': [comment.body.encode('ascii', 'ignore').decode('ascii') for comment in post.comments],
                    'comments': [remove_emojis(comment.body.encode('ascii', 'ignore').decode('ascii')) for comment in post.comments],
                    'created_utc': post.created_utc,
                    'post_id': post.id
                })
                print(f"Added post: {post.id} - {post.title}")
            else:
                print(f"Skipped duplicate post: {post.id}")

    except Exception as e:
        print(f"Error while fetching data: {e}")

    if data:
        # Save new data to CSV
        reddit_data = pd.DataFrame(data)
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        reddit_data.to_csv(f"{reddit_directory_path}/reddit_data_{timestamp}.csv", index=False)
        print(f"Saved {len(reddit_data)} new posts to CSV.")

        # Update the processed IDs file
        with open(processed_ids_file, "a") as f:
            for post_id in new_ids:
                f.write(post_id + "\n")
        print(f"Updated processed IDs file with {len(new_ids)} new IDs.")
    else:
        print("No new posts to save.")
    return data

# Example usage
if __name__ == "__main__":
    reddit_subreddits = [
        # "aiart", "AIArtCreator","art", "artists", "COPYRIGHT", "Human_Artists_Info", 
        "DefendingAIArt",  "ArtistHate", "aiwars", "AIHaters", 
    ]
    reddit_keywords = [
        # Supporting AI
        # "AI art", "AI tools", "GAN", "Deepfake", "DALL-E", "MidJourney",
        # "AI video", "Stable Diffusion", "AI creator", "AI future",
        # "AI innovation", "AI progress", "AI technology", "AI advancements",
        # "AI benefits", "AI creativity", "AI potential",

        # Opposing AI
        # "Anti AI", "AI theft", "Stop AI", "No AI", "Ban AI",
        # "Stealing art", "AI fake", "Protect", "Human art", "AI harm",
        # "AI danger", "AI risks", "AI threat", "AI concerns", "AI ethics",
        # "AI regulation", "AI impact", "AI controversy", "AI debate",
        # "AI infringement", "AI lawsuit", "AI copyright", "AI exploitation", "AI manipulation", "AI fraud",

        # General keywords
        "Anti", "Stop", "No", "Ban", "theft", "fake", "Protect", "Human", "harm",
        "talent", "skill", "creativity", "innovation", "progress", "technology", "advancements",
    ]
    # clear_processed_ids()
    # delete_processed_ids()
    reddit_data = fetch_reddit_data(reddit_subreddits, reddit_keywords)
    # fetch_reddit_data_with_only_keywords = fetch_reddit_data_with_only_keywords(reddit_keywords)
