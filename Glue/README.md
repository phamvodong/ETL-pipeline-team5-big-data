# Social Media Sentiment Analysis Script

This script is designed to analyze social media data (such as comments from platforms like YouTube) by performing sentiment analysis on both the content and the comments. It uses AWS Glue for data transformation, `TextBlob` for sentiment analysis, and writes the results to both Amazon S3 and MongoDB.

## Overview

The script does the following:

- Reads raw social media data from AWS Glue.
- Applies sentiment analysis on both the content and comments of the social media posts.
- Writes the results to Amazon S3 and MongoDB Atlas.

## Features

- **Sentiment Analysis**: Classifies text as `POSITIVE`, `NEGATIVE`, or `NEUTRAL` based on sentiment polarity.
- **Data Transformation**: Handles nested comment arrays, flattens them, and processes invalid or empty data.
- **Output Storage**: Writes the sentiment analysis results to Amazon S3 in JSON format and inserts the data into MongoDB for storage and future use.
- **Logging and Error Handling**: Comprehensive logging and error handling to ensure robustness.

## Requirements

Before running this script, make sure you have the following installed:

- **AWS Glue**: To read and process data from AWS Glue catalog.
- **MongoDB Atlas**: A MongoDB cluster to store sentiment analysis results.
- **Python 3.x** and the following libraries:
  - `boto3`: AWS SDK for Python.
  - `pyspark`: Spark-based transformations for Glue.
  - `textblob`: For sentiment analysis.
  - `pandas`: Data manipulation.
  - `pymongo`: MongoDB client to interact with MongoDB Atlas.

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Script Workflow

### 1. **Data Ingestion**

- The script reads social media data from AWS Glue catalog.
- It processes the `comments` column, ensuring it is properly formatted (handling nested arrays, empty data, etc.).

### 2. **Sentiment Analysis**

- The `TextBlob` library is used to analyze sentiment:
  - **Positive**: Polarity > 0.3
  - **Negative**: Polarity < -0.3
  - **Neutral**: Otherwise
- Sentiment analysis is applied to both the content (combination of title and content) and individual comments.

### 3. **Output Storage**

- The results are written to:
  - **S3**: Sentiment analysis results are saved in S3 as JSON files, partitioned by `source` and `partition_date`.
  - **MongoDB**: Sentiment analysis results are stored in MongoDB for later access and analysis.

### 4. **Error Handling and Logging**

- The script logs detailed information about the data transformation, sentiment analysis, and writing to output destinations.
- Errors are captured and logged to ensure transparency in the processing pipeline.

## How to Run the Script

1. Ensure that your AWS Glue environment is set up correctly.
2. Replace the MongoDB connection string in the script with your MongoDB Atlas connection details.
3. Run the script on AWS Glue using the following command:

```bash
aws glue start-job-run --job-name <your-glue-job-name>
```

### Script Execution

Once the job is started, the script will:

1. Load the data from AWS Glue.
2. Transform the `comments` column, flattening nested arrays and handling invalid entries.
3. Apply sentiment analysis to the content and comments.
4. Write the transformed and sentiment-analyzed data to S3 and MongoDB.

## Logs

The script uses Python's `logging` module to capture important information about its execution. Logs are displayed in the console and include details about:

- Data schema before and after transformation.
- Processing of each row, including comments and sentiment analysis results.
- Errors encountered during data processing or writing to output storage.

### Example Log Output:

```
INFO:root:=== Initial Schema ===
INFO:root:=== After Transform ===
INFO:root:=== Sample Data ===
INFO:root:Flattened comments result: ['Great post!', 'Interesting article']
INFO:root:Inserted batch 1 of 5
INFO:root:Successfully written to MongoDB Atlas!
```

## Error Handling

- If any error occurs during comment processing, sentiment analysis, or writing to storage (S3/MongoDB), the script logs the error and continues processing other records.
- Empty or invalid comments are handled gracefully, and no data will be lost or processed incorrectly.
