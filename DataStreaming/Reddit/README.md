# README for Reddit Crawler and Data Uploader

This project consists of two main scripts: **`crawler.py`**, designed for fetching, processing, and uploading Reddit data to AWS services such as Kinesis and S3.

## **Project Overview**

### **`crawler.py`**

- Fetches Reddit posts and their comments from specified subreddits based on keywords.
- Sends the processed data to an AWS Kinesis data stream for further processing.
- Saves processed post IDs locally to avoid duplicate processing.

## **Setup and Installation**

### **1. Prerequisites**

- Python 3.8+
- AWS account with S3 and Kinesis configured.
- AWS CLI installed and configured with appropriate permissions.
- Reddit API credentials (client ID, client secret, user agent).
- Required Python libraries: `pandas`, `boto3`, `praw`.

### **2. Install Dependencies**

Install dependencies:

```bash
pip install -r requirements.txt
```

### **3. Add .env file**

Create **`.env`** based on the **`.env-example`**

```.env
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USER_AGENT=
```

## **Usage**

### **1. Running the Crawler (`crawler.py`)**

#### **Input**

- **Subreddits**: A list of subreddit names to scrape.
- **Keywords**: A list of keywords to filter posts.
- **AWS Kinesis Stream**: Sends data to the `social-media-stream` Kinesis stream.

#### **Output**

- Data saved in a local directory (`data/reddit`).
- Processed post IDs stored in `processed_ids.txt` to prevent reprocessing.
- Real-time upload of Reddit data to Kinesis.

#### **Run the Script**

Update the `subreddits` and `keywords` lists in the script, then execute:

```bash
python crawler.py
```

---

## **Folder Structure**

```text
project/
├── crawler.py                        # Fetches Reddit data
├── .env                              # Env file
├── requirements.txt                  # Python dependencies
└── README.md                         # Project documentation
```

---

## **Key Functions**

### **`crawler.py`**

1. **`fetch_reddit_data(subreddits, keywords, limit=10000)`**  
   Fetches Reddit data based on subreddits and keywords. Limits to 10,000 posts per query.

2. **`remove_emojis(text)`**  
   Removes emojis and unsupported Unicode characters from text.

3. **`KinesisProducer`**  
   Sends data to an AWS Kinesis stream.

---

## **AWS Integration**

### **Kinesis**

- **Stream Name**: `social-media-stream`
- Data is sent in real-time with attributes like `id`, `title`, `content`, and `comments`.

### **S3**

- **Bucket Name**: `raw-social-data`
- Files are uploaded with a structured path:
  `reddit/YYYY/MM/DD/HH/<post_id>.json`

## **Error Handling**

### **`crawler.py`**

- Skips inaccessible subreddits and handles errors while fetching comments.
- Logs issues with specific posts or comments.

## **Known Limitations**

1. **Reddit Rate Limits**: May encounter API rate limits during high-volume scraping.
2. **AWS Costs**: Kinesis and S3 incur costs based on usage.

## **Future Enhancements**

- Add support for handling Reddit's pagination for larger datasets.
- Implement retry logic for failed Kinesis uploads.
- Introduce a dashboard for monitoring upload statuses and errors.
