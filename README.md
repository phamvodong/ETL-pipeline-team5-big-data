# Social Media Data Processing Pipeline

## Table of Contents

- [Overview](#overview)
- [Folder Structure](#folder-structure)
- [Data Sources](#data-sources)
- [Setup](#setup)
- [Running the Project](#running-the-project)

## Overview

The project is structured into several components:

1. **Data Streaming**:
   - Crawlers for Facebook, Reddit, and YouTube to collect raw social media data.
   - Upload scripts for sending data to S3.
2. **Glue**:

   - Transformations and ETL jobs for processing data.

3. **Lambda Functions**:

   - Functions that process, filter, and enrich the data, including sentiment analysis and formatting for further use.

4. **Utils**:
   - Utility scripts for data formatting and Kinesis producer for streaming data.

The pipeline ingests data from social media platforms, processes it using AWS Lambda, analyzes sentiment using local scripts, and stores the results in S3 buckets for further use or analysis.

## Folder Structure

Here is an overview of the project structure:

```
├── README.md
│
├── data/
│   ├── fb_data.csv
│   ├── reddit_data.csv
│   └── youtube_data.csv
│
├── DataStreaming/
│   │
│   ├── Facebook/
│   │     ├── crawler.py
│   │     ├── README.md
│   │     └── requirements.txt
│   │
│   ├── Reddit/
│   │   ├── crawler.py
│   │   ├── README.md
│   │   ├── requirements.txt
│   │   └── upload_reddit_data.py
│   │
│   └── Youtube/
│      ├── crawler.py
│      ├── README.md
│      ├── requirements.txt
│      └── upload_youtube_data.py
│
├── Glue/
│   ├── job.py
│   ├── README.md
│   └── requirements.txt
│
├── LambdaFunction/
│   ├── kenesis_to_s3.py
│   ├── README.md
│   ├── reddit_proccessor.py
│   ├── requirements.txt
│   └── youtube_processor.py
│
└── utils/
    ├── data_formatter.py
    └── kinesis-producer.py

```

## Data Sources

- **Facebook Data**: Collected through a Facebook crawler. The data is stored in CSV files under the `data` directory.
- **Reddit Data**: Collected through a Reddit crawler. The raw data is stored in CSV files and processed via Lambda.
- **YouTube Data**: YouTube video data is collected and stored in CSV format. The YouTube data includes video details and comments.

## Setup

Before running the project, make sure you have the following:

1. **AWS Account**: You need an AWS account to use services like Lambda, Kinesis, and S3.
2. **AWS CLI**: Make sure the AWS CLI is installed and configured with your credentials.
3. **Python 3.x**: Ensure you have Python 3.x installed along with pip for managing dependencies.

### Install Dependencies

Each directory that contains a Python script or crawler includes a `requirements.txt` file that lists the necessary Python packages. You can install the dependencies by navigating to the respective directory and running:

```bash
pip install -r requirements.txt
```

## Running the Project

The project consists of multiple components. Here's how you can run each part:

1. **Data Crawlers** (Facebook, Reddit, YouTube):

   - Navigate to the respective platform's folder (e.g., `DataStreaming/Facebook`).
   - Run the `crawler.py` to collect the data.
   - Optionally, use the `upload_..._data.py` script to upload the crawled data to S3.

   Example:

   ```bash
   python crawler.py
   ```

2. **Lambda Functions**:

   - The Lambda functions can be deployed to AWS Lambda to process incoming data.
   - The functions include Facebook, Reddit, and YouTube processors, which process the raw data, perform sentiment analysis, and store the results in S3.
   - Each Lambda function is designed to work with S3 triggers.

3. **Sentiment Analysis**:

   - The `local_sentiment_analysis.py` script analyzes the sentiment of content and comments from social media posts.
   - You can run this script locally by providing input files in JSON format.

   Example:

   ```bash
   python local_sentiment_analysis.py
   ```
