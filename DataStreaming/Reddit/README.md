# README for Reddit Crawler and Data Uploader

This project consists of two main scripts: **`crawler.py`** and **`upload_reddit_data.py`**, designed for fetching, processing, and uploading Reddit data to AWS services such as Kinesis and S3.

---

## **Project Overview**

### **`crawler.py`**

- Fetches Reddit posts and their comments from specified subreddits based on keywords.
- Sends the processed data to an AWS Kinesis data stream for further processing.
- Saves processed post IDs locally to avoid duplicate processing.

### **`upload_reddit_data.py`**

- Reads Reddit data from a CSV file.
- Formats and uploads the data to:
  - An AWS S3 bucket for long-term storage.
  - An AWS Kinesis data stream for real-time processing.

---

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

---

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

### **2. Uploading CSV Data (`upload_reddit_data.py`)**

#### **Input**

- **CSV File**: A file containing Reddit post data with fields like `title`, `content`, `comments`, `created_utc`, and `post_id`.
- **AWS S3 Bucket**: Uploads formatted data to an S3 bucket.
- **AWS Kinesis Stream**: Sends formatted data to the `social-media-stream` Kinesis stream.

#### **Output**

- Data uploaded to the specified S3 bucket with a structured path: `reddit/YYYY/MM/DD/HH/<post_id>.json`.
- Data sent to the Kinesis stream for real-time processing.

#### **Run the Script**

Update the `csv_file` variable with the path to your data file and execute:

```bash
python upload_reddit_data.py
```

---

## **Folder Structure**

```text
project/
├── reddit_data/
│   ├── processed_ids.txt             # Tracks processed Reddit post IDs
│   └── reddit_data.csv               # Example CSV file for upload script
├── crawler.py                        # Fetches Reddit data
├── upload_reddit_data.py             # Uploads local data to AWS
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

### **`upload_reddit_data.py`**

1. **`read_csv_data(filepath)`**  
   Reads CSV or TSV files into a Pandas DataFrame.

2. **`format_local_data(df)`**  
   Formats local CSV data into a structure compatible with S3 and Kinesis.

3. **`upload_csv_to_s3(file_path, bucket_name)`**  
   Uploads formatted data to an S3 bucket and sends it to Kinesis.

---

## **AWS Integration**

### **Kinesis**

- **Stream Name**: `social-media-stream`
- Data is sent in real-time with attributes like `id`, `title`, `content`, and `comments`.

### **S3**

- **Bucket Name**: `raw-social-data`
- Files are uploaded with a structured path:
  `reddit/YYYY/MM/DD/HH/<post_id>.json`

---

## **Error Handling**

### **`crawler.py`**

- Skips inaccessible subreddits and handles errors while fetching comments.
- Logs issues with specific posts or comments.

### **`upload_reddit_data.py`**

- Tracks failed uploads and returns a summary with details of failures.

---

## **Known Limitations**

1. **Reddit Rate Limits**: May encounter API rate limits during high-volume scraping.
2. **AWS Costs**: Kinesis and S3 incur costs based on usage.
3. **Local File Storage**: Ensure enough space for storing data locally before uploading.

---

## **Future Enhancements**

- Add support for handling Reddit's pagination for larger datasets.
- Implement retry logic for failed Kinesis uploads.
- Introduce a dashboard for monitoring upload statuses and errors.
