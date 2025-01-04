import praw

# Authentication
reddit = praw.Reddit(
    client_id="MY3RsXHBltk08XyMZxqE7w",  # Your Client ID
    client_secret="RA1M9hcJMy9lXTHAVE0XSIkh0JFfBA",  # Your Secret
    user_agent="AI art opinion personal use script by /u/Sufficient_Hawk7672"  # Replace with your Reddit username
)

# Example: Fetching Posts from a Subreddit
subreddit = reddit.subreddit("GenerativeArt")  # Replace with any subreddit you're interested in
for post in subreddit.hot(limit=10):
    print(f"Title: {post.title}")
    print(f"Author: {post.author}")
    print(f"Score: {post.score}")
    print(f"Comments: {post.num_comments}")
    print(f"URL: {post.url}\n")
