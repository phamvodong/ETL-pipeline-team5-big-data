# **YouTube Data Streamer**

This project includes two scripts for processing and uploading YouTube data to AWS Kinesis and S3 for further analytics and processing.

---

## **Requirements**

This project uses the following tools and libraries:

- Python 3.8+
- [Google API Client](https://googleapis.github.io/google-api-python-client/) (YouTube Data API client)
- [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) (AWS SDK for Python)
- `json` (JSON file handling)
- `re` (Text cleaning and regex)
- `datetime` (Date and time operations)
- `time` (Time-based operations)
- `os` (File system operations)

---

Install the dependencies:

```bash
pip install -r requirements.txt
```

---

## **Usage**

### **1. Crawler Script (`crawler.py`)**

This script fetches YouTube data for specified search queries and streams the data to AWS Kinesis.

#### How to Run:

1. Replace the `API_KEY` variable in `crawler.py` with your YouTube Data API key.
2. Update the search queries in the `search_queries` list in the script as needed.
3. Execute the script:

   ```bash
   python crawler.py
   ```

#### Functionality:

- Fetches YouTube videos and comments based on the search queries.
- Sends video data to AWS Kinesis for further processing.

---

### **2. Upload Script (`upload_youtube_data.py`)**

This script uploads YouTube video data from a local JSON file to AWS S3 and Kinesis.

#### How to Run:

1. Replace the `input_file` variable with the path to your local JSON file containing YouTube video data.
2. Execute the script:

   ```bash
   python upload_youtube_data.py
   ```

#### Functionality:

- Reads a local JSON file with YouTube video data.
- Cleans the data (removing unwanted characters from text fields).
- Uploads the data to an S3 bucket (`raw-social-data` by default).
- Sends the data to an AWS Kinesis stream for further processing.

---

## **Folder Structure**

```
youtube-data-streamer/
  ├── crawler.py               # Script to fetch and stream YouTube data to Kinesis
  ├── upload_youtube_data.py   # Script to upload YouTube data to S3 and Kinesis
  ├── README.md                # Project documentation
  ├── requirements.txt         # List of dependencies for the project
```

---

## **AWS Requirements**

### **1. S3 Bucket**

- The `upload_youtube_data.py` script uses an S3 bucket (`raw-social-data` by default).
- Ensure the bucket exists and your IAM user has `s3:PutObject` permissions.

### **2. Kinesis Stream**

- Both scripts use an AWS Kinesis stream (`team5-social-media-stream` by default).
- Ensure the stream exists and your IAM user has `kinesis:PutRecord` permissions.

---

## **Data Flow**

1. **Crawler Script:**

   - Fetches data from YouTube using the YouTube Data API.
   - Streams the data to Kinesis for processing.

2. **Upload Script:**
   - Reads YouTube data from a local file.
   - Uploads the data to:
     - **S3** for long-term storage.
     - **Kinesis** for real-time processing.

---

## **Notes**

- **Rate Limits:** The YouTube API has quota limits. Adjust the number of queries or results if necessary.
- **Error Handling:** Both scripts include error handling for AWS and YouTube API operations.
- **Partitioning:** Uploaded data in S3 is organized by date (e.g., `youtube/YYYY/MM/DD/HH/`).

---

## **Example Output**

### **Kinesis Data Structure:**

```json
{
  "source": "youtube",
  "id": "123abc",
  "title": "Example Video Title",
  "description": "Example video description.",
  "published_at": "2023-01-01T00:00:00Z",
  "comments": ["Great video!", "Loved it!"],
  "comments_disabled": false,
  "search_query": "#AIart",
  "timestamp": 1672531200,
  "partition_date": "2023-01-01"
}
```

### **S3 Key Structure:**

```
youtube/YYYY/MM/DD/HH/{video_id}.json
```

Example:

```
youtube/2025/01/09/15/123abc.json
```

---

## **Troubleshooting**

- **Invalid API Key:** Ensure your YouTube Data API key is active and correct.
- **AWS Permissions:** Verify your IAM user has the necessary permissions for Kinesis and S3.
- **Quota Exceeded:** Monitor your YouTube API usage to avoid exceeding the quota.
