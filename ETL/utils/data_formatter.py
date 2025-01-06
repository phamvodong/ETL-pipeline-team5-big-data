import json
import pandas as pd
from datetime import datetime

def format_local_data(df):
    """
    Format local data into the expected structure for S3/Kinesis
    
    Args:
        df: Pandas DataFrame with columns: 
            title, content, num_comments, comments, created_utc, post_id
    
    Returns:
        List of formatted dictionaries ready for upload
    """
    formatted_data = []
    timestamp = int(datetime.now().timestamp())
    
    for _, row in df.iterrows():
        # Parse comments from string representation
        comments = row['comments']
        if isinstance(comments, str):
            comments = eval(comments)  # Convert string repr of list to actual list
            
        formatted_item = {
            'source': 'reddit',
            'id': row['post_id'],
            'title': row['title'] if pd.notna(row['title']) else '',
            'content': row['content'] if pd.notna(row['content']) else '',
            'comments': comments if isinstance(comments, list) else [],
            'created_utc': int(row['created_utc']),
            'subreddit': 'local_upload',  # Default for local data
            'timestamp': timestamp
        }
        formatted_data.append(formatted_item)
        
    return formatted_data

def read_csv_data(filepath):
    """Helper to read CSV/TSV data into DataFrame"""
    try:
        df = pd.read_csv(filepath, sep='\t')
    except:
        df = pd.read_csv(filepath)
    return df
