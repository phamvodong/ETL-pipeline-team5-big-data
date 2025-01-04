from mastodon import Mastodon

# Authentication
mastodon = Mastodon(
    access_token="RNC78YFJeaTax8oOyjbSUXycNcFA0uEQAy6dopsPNQo",  # Replace with your access token
    api_base_url="https://mastodon.art"  # Replace with your Mastodon instance URL
)

# Search for posts with a specific hashtag
hashtag = "AIArt"
results = mastodon.timeline_hashtag(hashtag, limit=10)

# Print details of each post
for post in results:
    print(f"Author: {post['account']['display_name']} (@{post['account']['username']})")
    print(f"Content: {post['content']}")
    print(f"Created At: {post['created_at']}")
    print(f"Favorites: {post['favourites_count']}")
    print(f"Boosts: {post['reblogs_count']}")
    print("-" * 50)
