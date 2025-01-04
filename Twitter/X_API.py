import tweepy

# Authentication
api_key = "Qcqj82Ex8WwvASVQ5uH8JyvZY"
api_secret = "95so8dJmAFyXq5rAoc5QVXHqeMQGbrzJZG8j3sPkZ71Iq8bRWc"
bearer_token = "AAAAAAAAAAAAAAAAAAAAADGvxwEAAAAAEaoK19CTre%2B%2F0L4LYcIrjgXy79I%3DMSJsXlQXPHwuseZ2W4M9giXXLdRfEUO9P7y9ekC1WRF7fsZhNy"

client = tweepy.Client(bearer_token)

# Fetch tweets about AI art
query = "AI generative art -is:retweet"
tweets = client.search_recent_tweets(query=query, tweet_fields=["created_at", "public_metrics", "text", "author_id"], max_results=50)

# Print tweet details
for tweet in tweets.data:
    print(f"Text: {tweet.text}")
    print(f"Author ID: {tweet.author_id}")
    print(f"Created At: {tweet.created_at}")
    print(f"Likes: {tweet.public_metrics['like_count']}")
    print(f"Retweets: {tweet.public_metrics['retweet_count']}\n")
