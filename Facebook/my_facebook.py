import requests

# Facebook API credentials
ACCESS_TOKEN = "EAA5MY8QzQCMBOzfqsWMMxZBS3sNusDkHPLAelKec6ucBIfwDbL9pYFJRwc3ZCEZCW0dgoYC05nss1hr02QZCXSOe2ggC5eWnayZCtgQGEfzbG1NHMGRZC4J2i1SKuqLY4rAb1QweZBv1JVMdA9TsSB6bIndCeh8E4xChgaQqfFu0ExgNkT42qkgHCHT3NlGOukg"  # Replace with your access token
GRAPH_API_URL = "https://graph.facebook.com/v12.0"

# Search for posts with a specific hashtag
hashtag = "AIArt"  # Replace with your desired hashtag

# Search for the hashtag ID
hashtag_search_url = f"{GRAPH_API_URL}/ig_hashtag_search?user_id=YOUR_USER_ID&q={hashtag}&access_token={ACCESS_TOKEN}"
hashtag_response = requests.get(hashtag_search_url).json()

if "data" in hashtag_response and len(hashtag_response["data"]) > 0:
    hashtag_id = hashtag_response["data"][0]["id"]
    print(f"Found Hashtag ID: {hashtag_id}")

    # Fetch posts with the hashtag
    posts_url = f"{GRAPH_API_URL}/{hashtag_id}/top_media?user_id=YOUR_USER_ID&fields=id,caption,comments_count,like_count&access_token={ACCESS_TOKEN}"
    posts_response = requests.get(posts_url).json()

    # Process posts
    for post in posts_response.get("data", []):
        print(f"Post Caption: {post.get('caption')}")
        print(f"Likes: {post.get('like_count')}")
        print(f"Comments: {post.get('comments_count')}")
        print(f"Post ID: {post.get('id')}")
        print("-" * 40)

        # Fetch comments for the post
        if post.get("comments_count", 0) > 0:
            comments_url = f"{GRAPH_API_URL}/{post['id']}/comments?fields=from,message,like_count&access_token={ACCESS_TOKEN}"
            comments_response = requests.get(comments_url).json()

            print("Comments:")
            for comment in comments_response.get("data", []):
                print(f"  Comment by {comment['from']['name']}: {comment['message']}")
                print(f"  Likes: {comment.get('like_count', 0)}")
                print("  " + "-" * 30)
        else:
            print("No comments found for this post.")
        print("=" * 50)
else:
    print("No posts found for the hashtag.")
