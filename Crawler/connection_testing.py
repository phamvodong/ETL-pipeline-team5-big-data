import tweepy
import praw

# Twitter API credentials
TWITTER_API_KEY = "25J6h2sc8TKzSkJPfOBCBNPBk"
TWITTER_API_SECRET = "23MA8FNhuaJyShH4WR0YOcSgRTRpxVoGY27ZkCrgPkO9iByXeF"
TWITTER_BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAD%2B9xwEAAAAAsMu0ZFubSvAYFV4tUAV%2BrWF9sBM%3D0DNHJ10nK6SSJMPrOAz6VK7SiUtmrWKAvdABfvC9GprsSSfACT"
TWITTER_ACCESS_TOKEN = "1875798852755939328-5uOFs6CpqFlwlGxrrHAcoBoagtuzoJ"
TWITTER_ACCESS_SECRET = "21uqOpfX9UCHBowrXmZge2ZXfvYZWqVZoOZq3vDHCqBL4"

# Reddit API credentials
REDDIT_CLIENT_ID = "cvn2EH5C4HP5LifPPvHDvA"
REDDIT_CLIENT_SECRET = "kC_u2qJLXOwXficJEFrYUQppiIfqjw"
REDDIT_USER_AGENT = "script:KN1111:1.0 (by u/LessCase7928)"

# Authenticate Twitter
def test_twitter_connection():
    try:
        # twitter_client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
        twitter_client = tweepy.Client(consumer_key=TWITTER_API_KEY, consumer_secret=TWITTER_API_SECRET, access_token=TWITTER_ACCESS_TOKEN, access_token_secret=TWITTER_ACCESS_SECRET)
        # Test if we can fetch user details
        user = twitter_client.get_me()
        print(f"Twitter Connection Successful! Connected as {user.data['username']}")
        return True
    except tweepy.TweepyException as e:
        print(f"Twitter Connection Failed: {e}")
        return False


# Authenticate Reddit
# def test_reddit_connection():
#     try:
#         reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID, client_secret=REDDIT_CLIENT_SECRET, user_agent=REDDIT_USER_AGENT)
#         print("Successfully authenticated with Reddit API!")
#         # Test if we can fetch the user's Reddit profile
#         user = reddit.user.me()
#         print(f"Reddit Connection Successful! Connected as {user.name}")
#         return True
#     except Exception as e:
#         print(f"Reddit Connection Failed: {e}")
#         return False
def test_reddit_connection():
    try:
        reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID, client_secret=REDDIT_CLIENT_SECRET, user_agent=REDDIT_USER_AGENT)
        print("Successfully authenticated with Reddit API!")

        # Try fetching a post from a known subreddit (e.g., "Python")
        for submission in reddit.subreddit("Python").hot(limit=1):
            print(f"Successfully fetched a post: {submission.title}")

        return True
    except Exception as e:
        print(f"Reddit Connection Failed: {e}")
        return False

# Main function to test connections
if __name__ == "__main__":
    print("Testing Twitter Connection...")
    twitter_status = test_twitter_connection()
    print("\n")
    print("Testing Reddit Connection...")
    reddit_status = test_reddit_connection()

    if twitter_status and reddit_status:
        print("Both Twitter and Reddit connections are successful!")
    else:
        print("One or both connections failed. Please check the credentials and try again.")
