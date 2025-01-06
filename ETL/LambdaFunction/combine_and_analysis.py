import json
import boto3
from datetime import datetime
from textblob import TextBlob
import os

def analyze_sentiment_local(text):
    try:
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
            'scores': {
                'positive': float(max(0, polarity)),
                'negative': float(max(0, -polarity)),
                'neutral': float(1 - abs(polarity))
            },
            'analyzed_at': datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error: {e}")
        return None

def analyze_comments_sentiment(comments):
    if not comments:
        return []
    
    comment_sentiments = []
    for comment in comments:
        sentiment = analyze_sentiment_local(comment)
        if sentiment:
            comment_sentiments.append({
                'text': comment,
                'analysis': sentiment
            })
    return comment_sentiments

def lambda_handler(event, context):
    try:
        print("Processing event:", json.dumps(event))  # Add logging
        s3 = boto3.client('s3')
        source_bucket = event['Records'][0]['s3']['bucket']['name']
        dest_bucket = 'processed-social-data'
        
        data = []
        for record in event['Records']:
            print(f"Processing record: {record['s3']['object']['key']}")  # Add logging
            
            content = s3.get_object(
                Bucket=source_bucket,
                Key=record['s3']['object']['key']
            )
            
            item = json.loads(content['Body'].read())
            print(f"Retrieved item: {json.dumps(item)}")  # Add logging
            
            # Analyze main content
            main_text = f"{item.get('title', '')} {item.get('content', '')}"
            content_sentiment = analyze_sentiment_local(main_text)
            
            # Analyze comments
            comments_analysis = analyze_comments_sentiment(item.get('comments', []))
            
            # Calculate average sentiment scores for comments
            avg_comment_sentiment = {
                'positive': 0.0,
                'negative': 0.0,
                'neutral': 0.0
            }
            
            if comments_analysis:
                for comment in comments_analysis:
                    scores = comment['analysis']['scores']
                    avg_comment_sentiment['positive'] += scores['positive']
                    avg_comment_sentiment['negative'] += scores['negative']
                    avg_comment_sentiment['neutral'] += scores['neutral']
                
                total_comments = len(comments_analysis)
                for key in avg_comment_sentiment:
                    avg_comment_sentiment[key] /= total_comments
            
            if content_sentiment:
                result = {
                    'id': item.get('id'),
                    'source': item.get('source'),
                    'content': {
                        'text': main_text,
                        'sentiment': content_sentiment
                    },
                    'comments': {
                        'individual_analysis': comments_analysis,
                        'average_sentiment': avg_comment_sentiment
                    },
                    'analyzed_at': datetime.now().isoformat()
                }
                data.append(result)
                print(f"Processed item: {json.dumps(result)}")  # Add logging
        
        if data:
            timestamp = datetime.now().strftime('%Y/%m/%d/%H')
            key = f'sentiment/raw/dt={timestamp}/data.json'
            
            print(f"Uploading to S3: {dest_bucket}/{key}")  # Add logging
            s3.put_object(
                Bucket=dest_bucket,
                Key=key,
                Body=json.dumps(data),
                ContentType='application/json'
            )
        
        return {
            'statusCode': 200,
            'body': {
                'message': f'Processed {len(data)} items',
                'timestamp': datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")  # Add logging
        raise  # Re-raise the exception to see full error in CloudWatch