import os
import time
import tweepy
import pandas as pd

# Twitter API credentials
TWITTER_API_KEY = "25J6h2sc8TKzSkJPfOBCBNPBk"
TWITTER_API_SECRET = "23MA8FNhuaJyShH4WR0YOcSgRTRpxVoGY27ZkCrgPkO9iByXeF"
TWITTER_BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAD%2B9xwEAAAAAsMu0ZFubSvAYFV4tUAV%2BrWF9sBM%3D0DNHJ10nK6SSJMPrOAz6VK7SiUtmrWKAvdABfvC9GprsSSfACT"
TWITTER_ACCESS_TOKEN = "1875798852755939328-5uOFs6CpqFlwlGxrrHAcoBoagtuzoJ"
TWITTER_ACCESS_SECRET = "21uqOpfX9UCHBowrXmZge2ZXfvYZWqVZoOZq3vDHCqBL4"

# Authenticate Twitter
twitter_client = tweepy.Client(
    consumer_key=TWITTER_API_KEY, 
    consumer_secret=TWITTER_API_SECRET, 
    access_token=TWITTER_ACCESS_TOKEN, 
    access_token_secret=TWITTER_ACCESS_SECRET, 
    bearer_token=TWITTER_BEARER_TOKEN
)

# Ensure directories exist
twitter_directory_path = "data/twitter"
if not os.path.exists(twitter_directory_path):
    os.makedirs(twitter_directory_path)

def fetch_twitter_data(keywords, max_results=10):
    query = " OR ".join(keywords) + " -is:retweet"
    
    # Initialize an empty list for the data
    data = []

    # Retry logic for rate limit
    while True:
        try:
            # Adjusted max_results to be between 10 and 100
            if max_results < 10 or max_results > 100:
                max_results = 10  # Default to 10 if an invalid value is given

            tweets = twitter_client.search_recent_tweets(query=query, tweet_fields=['created_at', 'text', 'author_id', 'public_metrics'], max_results=max_results)
            print(f"Retrieved {len(tweets)} tweets.")
            for tweet in tweets.data:
                data.append({
                    'created_at': tweet.created_at,
                    'text': tweet.text,
                    'author_id': tweet.author_id,
                    'like_count': tweet.public_metrics['like_count'],
                    'retweet_count': tweet.public_metrics['retweet_count']
                })

            # Save data once retrieved
            if data:
                twitter_data = pd.DataFrame(data)
                twitter_data.to_csv(f"{twitter_directory_path}/twitter_data.csv", index=False)
                print(f"Twitter data saved locally with {len(twitter_data)} records.")
            return twitter_data

        except tweepy.errors.TooManyRequests as e:
            # Twitter's rate limit exceeded, sleep until limit resets
            reset_time = int(e.response.headers['x-rate-limit-reset'])  # Get reset time from headers
            current_time = int(time.time())
            wait_time = reset_time - current_time + 5  # Adding some buffer time (5 seconds)
            print(f"Rate limit exceeded. Sleeping for {wait_time} seconds...")
            time.sleep(wait_time)  # Sleep until the rate limit resets

        except Exception as e:
            print(f"An error occurred: {e}")
            break  # Break if there's another error, as we don't want to retry indefinitely

# Example usage
if __name__ == "__main__":
    twitter_keywords = [
        "AI art", "generative AI", "DALL-E", "MidJourney", "Stable Diffusion", "GAN art", 
        "Neural style transfer", "AI-generated images", "Text-to-image AI", "Artbreeder",
        "AI video generation", "Generative AI videos", "Deepfake", "Synthesized videos",
        "Text-to-video AI", "AI creativity", "AI ethics in art", "AI in media"
    ]   
    twitter_data = fetch_twitter_data(twitter_keywords)
