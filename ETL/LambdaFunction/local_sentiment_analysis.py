import json
import boto3
from datetime import datetime
from textblob import TextBlob
import os

def analyze_sentiment_local(text):
    """Match Glue job sentiment analysis logic"""
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    
    if polarity > 0.3:
        sentiment = 'POSITIVE'
    elif polarity < -0.3:
        sentiment = 'NEGATIVE'
    else:
        sentiment = 'NEUTRAL'
        
    return {
        'sentiment': sentiment,
        'score': str(polarity)
    }

def analyze_text_content(source_type, item):
    """Analyze main content based on source type"""
    if source_type == 'youtube':
        main_text = f"{item.get('title', '')} {item.get('description', '')}"
    else:  # reddit
        main_text = f"{item.get('title', '')} {item.get('content', '')}"
    
    return analyze_sentiment_local(main_text)

def get_comments_list(source_type, item):
    """Extract comments based on source type"""
    comments = item.get('comments', [])
    if not isinstance(comments, list):
        comments = []
    
    # Filter out deleted/empty comments
    return [c for c in comments if c and c != '[deleted]']


def analyze_comments_sentiment(comments):
    """Process comments array for YouTube data"""
    if not comments or not isinstance(comments, list):
        return []
    
    # Handle nested array structure
    if comments and isinstance(comments[0], list):
        comments = comments[0]  # Take first array of comments
    
    # Filter out None/null values
    comments = [c for c in comments if c and isinstance(c, str)]
    
    results = []
    for comment in comments:
        analysis = TextBlob(str(comment))
        polarity = analysis.sentiment.polarity
        
        if polarity > 0.3:
            sentiment = 'POSITIVE'
        elif polarity < -0.3:
            sentiment = 'NEGATIVE'
        else:
            sentiment = 'NEUTRAL'
            
        results.append({
            'score': str(polarity),
            'sentiment': sentiment
        })
    return results

def ensure_test_dir():
    """Create test_data directory if it doesn't exist"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    test_dir = os.path.join(script_dir, 'test_data')
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    return test_dir

def process_local_file(input_file_path, output_file_path=None):
    """Process a local JSON file to match Glue job output format"""
    try:
        test_dir = ensure_test_dir()
        
        if not output_file_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file_path = os.path.join(test_dir, f'sentiment_results_{timestamp}.json')

        with open(input_file_path, 'r') as f:
            item = json.loads(f.read())
        
        # Clean comments array before processing
        if 'comments' in item and isinstance(item['comments'], list):
            if item['comments'] and isinstance(item['comments'][0], list):
                item['comments'] = item['comments'][0]  # Take first array
            item['comments'] = [c for c in item['comments'] if c and isinstance(c, str)]
        
        # Create result in same format as Glue job
        result = {
            'source': item.get('source', 'unknown'),
            'id': item.get('id'),
            'title': item.get('title', ''),
            'content': item.get('content', ''),
            'comments': item.get('comments', []),
            'created_utc': item.get('created_utc', int(datetime.now().timestamp())),
            'timestamp': int(datetime.now().timestamp()),
            'partition_date': datetime.now().strftime('%Y-%m-%d'),
            'content_sentiment': analyze_sentiment_local(
                f"{item.get('title', '')} {item.get('content', '')}"
            ),
            'comments_sentiment': analyze_comments_sentiment(item.get('comments', []))
        }
        
        # Remove any null values
        result = {k: v for k, v in result.items() if v is not None}
        
        # Save results
        if output_file_path:
            with open(output_file_path, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"Results saved to {output_file_path}")
        
        return result
            
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        raise

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Test with sample file
    input_file = os.path.join(script_dir, "test_data", "sample_reddit_post.json")
    output_file = os.path.join(script_dir, "test_data", "sentiment_results.json")
    
    # Create sample data if it doesn't exist
    if not os.path.exists(input_file):
        sample_data = {
            "source": "youtube",
            "id": "test123",
            "title": "Sample YouTube Video",
            "content": "This is a sample video description",
            "comments": [
                "This is great!",
                "I love this video",
                "Suckkkkkk"
            ],
            "created_utc": int(datetime.now().timestamp()),
            "timestamp": int(datetime.now().timestamp()),
            "partition_date": datetime.now().strftime('%Y-%m-%d')
        }
        os.makedirs(os.path.dirname(input_file), exist_ok=True)
        with open(input_file, 'w') as f:
            json.dump(sample_data, f, indent=2)
    
    result = process_local_file(input_file, output_file)
    print(json.dumps(result, indent=2))
