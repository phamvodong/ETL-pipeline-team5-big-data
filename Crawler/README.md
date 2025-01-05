## **Requirements**

This project uses the following tools and libraries:

- Python 3.8+
- AWS S3 (for cloud storage)
- [Tweepy](https://docs.tweepy.org/) (Twitter API client)
- [PRAW](https://praw.readthedocs.io/) (Reddit API client)
- [Pandas](https://pandas.pydata.org/) (Data manipulation)
- [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) (AWS SDK for Python)

---

**Create a new virtual environment:**

```bash
python -m venv venv
```

### Activate the virtual environment:

**On Windows:**

```bash
venv\Scripts\activate
```

**On macOS/Linux:**

```bash
source venv/bin/activate
```

---

Install the dependencies:

```bash
pip install -r requirements.txt
```

## **Usage**

### **Testing Connection**

Run the `connection_testing.py` script to test the connection to Twitter and Reddit APIs:

```bash
python ./connection_testing.py
```

### **1. Fetch Data**

Run the `fetch_data.py` script to collect historical data from Twitter and Reddit:

```bash
python ./fetch_data.py
```

The script will save:

- Twitter data to `data/twitter/twitter_data.csv`
- Reddit data to `data/reddit/reddit_data.csv`

### **2. Save Data to AWS S3**

Run the `save_to_s3.py` script to upload data to AWS S3:

```bash
python ./save_to_s3.py
```

The data will be organized in the following structure on S3:

```
social_media/
  ├── twitter/
  │   └── twitter_data.csv
  ├── reddit/
  │   └── reddit_data.csv
```

---

## **Folder Structure**

```
social-media-pipeline/
  ├── data/                   # Local data storage
  │   ├── twitter/            # Twitter data folder
  │   │   └── twitter_data.csv
  │   ├── reddit/             # Reddit data folder
  │       └── reddit_data.csv
  ├── fetch_data.py           # Script to fetch data
  ├── save_to_s3.py           # Script to upload data to S3
  ├── requirements.txt        # Python dependencies
  └── README.md               # Project documentation
```
