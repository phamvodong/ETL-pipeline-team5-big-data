import sys
import json
import logging
import boto3
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import *
from pyspark.sql.types import *
from textblob import TextBlob
from awsglue.dynamicframe import DynamicFrame
import pandas as pd

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def analyze_sentiment(text):
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
        'score': str(polarity)  # Convert to string for MapType compatibility
    }

def flatten_comments(comments):
    """Helper function to safely flatten nested comment arrays"""
    try:
        logger.info(f"Input comments data: {comments}, Type: {type(comments)}")
        
        # Handle empty/null cases
        if comments is None or comments == [] or comments == "[]":
            logger.info("Comments is empty/null, returning empty list")
            return []
            
        # Handle different comment structures    
        if isinstance(comments, list):
            logger.info(f"Comments is list with length {len(comments)}")
            
            # Handle nested array cases
            if len(comments) > 0 and isinstance(comments[0], list):
                logger.info("Found nested array, taking first array")
                comments = comments[0]
            
            # Filter out invalid values
            valid_comments = []
            for c in comments:
                logger.info(f"Processing comment: {c}, Type: {type(c)}")
                if c and str(c).strip() and str(c) != 'nan' and str(c) != 'null':
                    try:
                        comment_str = str(c).strip()
                        if comment_str:  # Only add non-empty strings
                            valid_comments.append(comment_str)
                            logger.info(f"Added valid comment: {comment_str}")
                    except:
                        logger.error(f"Error converting comment to string: {c}")
                        continue
                else:
                    logger.info(f"Skipped invalid comment: {c}")
                        
            logger.info(f"Final valid comments count: {len(valid_comments)}")
            return valid_comments
            
        logger.info("Comments is not a list, returning empty list")
        return []
        
    except Exception as e:
        logger.error(f"Error flattening comments: {str(e)}")
        return []

def analyze_comment_list(comments):
    """Process comments array with error handling"""
    try:
        flattened_comments = flatten_comments(comments) 
        if not flattened_comments:
            return []
            
        results = []
        for comment in flattened_comments:
            if not comment or str(comment).strip() == '' or str(comment) == 'nan':
                continue
                
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
    except Exception as e:
        logger.error(f"Error analyzing comments: {str(e)}")
        return []

# Get job arguments including secrets
args = getResolvedOptions(sys.argv, [
    'JOB_NAME',
])

# Initialize Glue context
glueContext = GlueContext(SparkContext.getOrCreate())
spark = glueContext.spark_session
job = Job(glueContext)

# Set MongoDB connection parameters
mongo_uri ="mongodb+srv://{}.mongodb.net/?retryWrites=true&w=majority".format('team5-social-media')
MONGODB_DATABASE = "social_media"
MONGODB_COLLECTION = "sentiment_analysis"

# Define schema for YouTube format
schema = StructType([
    StructField("source", StringType(), True),
    StructField("id", StringType(), True),
    StructField("title", StringType(), True),
    StructField("content", StringType(), True),
    StructField("comments", ArrayType(StringType()), True),  # Array of strings
    StructField("created_utc", IntegerType(), True),
    StructField("timestamp", IntegerType(), True),
    StructField("partition_date", StringType(), True)
])

# Read data from Glue catalog
social_data = glueContext.create_dynamic_frame.from_catalog(
    database="social-media-db",
    table_name="processed_data_social_comment"
).toDF()

# Log initial schema
logger.info("=== Initial Schema ===")
logger.info(social_data.schema)

# Add this after creating social_data DataFrame
logger.info("=== Source Distribution ===")
social_data.groupBy("source").count().show()

# After reading from Glue catalog, add source validation
logger.info("=== Initial Source Distribution ===")
social_data.groupBy("source").count().show(truncate=False)

# Ensure no source filtering is happening
social_data = social_data.filter(col("source").isNotNull())

logger.info("=== Source Distribution After Null Filter ===")
social_data.groupBy("source").count().show(truncate=False)

# Handle comments column transformation
social_data = social_data.withColumn(
    "comments",
    when(col("comments").isNull(), array().cast(ArrayType(StringType())))
    .when(col("comments").cast("string").contains("array"), 
        from_json(
            regexp_replace(col("comments").cast("string"), "\\{array=\\[(.*)\\]\\}", "[$1]"),
            ArrayType(StringType())
        )
    )
    .otherwise(
        when(col("comments").cast(ArrayType(StringType())).isNotNull(), 
            col("comments").cast(ArrayType(StringType())))
        .otherwise(array().cast(ArrayType(StringType())))
    )
)

# Ensure final array type
social_data = social_data.withColumn(
    "comments",
    coalesce(col("comments"), array().cast(ArrayType(StringType())))
)

# Log transformed schema and data
logger.info("=== After Transform ===")
logger.info(social_data.schema)
logger.info("=== Sample Data ===")
social_data.select("id", "comments").show(5, truncate=False)

# Apply schema validation
social_data = social_data.select([
    "source", "id", "title", "content", "comments",
    "created_utc", "timestamp", "partition_date"
])

# Log data after validation
logger.info("=== Data after Validation ===")
sample_validated = social_data.limit(5).collect()
for row in sample_validated:
    logger.info(f"Validated Row: {row.asDict()}")
    logger.info(f"Comments after validation: {row['comments']}")

# Register UDFs for sentiment analysis
sentiment_udf = udf(analyze_sentiment, MapType(StringType(), StringType()))
analyze_comments_udf = udf(
    analyze_comment_list,
    ArrayType(MapType(StringType(), StringType()))
)

# Apply sentiment analysis to content and comments
df_with_sentiment = social_data.withColumn(
    "content_sentiment",
    sentiment_udf(concat(col("title"), lit(" "), col("content")))
).withColumn(
    "comments_sentiment",
    analyze_comments_udf(col("comments"))
)

# After sentiment analysis, convert to pandas DataFrame
sentiment_results = []
for row in df_with_sentiment.collect():
    try:
        row_dict = row.asDict()
        logger.info("\n=== Processing Row ===")
        logger.info(f"Row ID: {row_dict.get('id')}")
        logger.info(f"Source: {row_dict.get('source')}")
        logger.info(f"Raw comments type: {type(row_dict.get('comments'))}")
        logger.info(f"Raw comments value: {row_dict['comments']}")
        logger.info(f"Row Dict Keys: {row_dict.keys()}")

        flattened_comments = flatten_comments(row_dict.get('comments', []))
        logger.info(f"Flattened comments result: {flattened_comments}")
        
        # Check S3 data for this ID
        logger.info("Checking S3 data...")
        try:
            s3_client = boto3.client('s3')
            response = s3_client.get_object(
                Bucket='processed-data-social-comment',
                Key=f"source={row_dict['source']}/partition_date={row_dict['partition_date']}/{row_dict['id']}.json"
            )
            s3_data = json.loads(response['Body'].read().decode('utf-8'))
            logger.info(f"S3 data for ID {row_dict['id']}: {s3_data}")
        except Exception as e:
            logger.error(f"Error reading S3 data: {str(e)}")

        sentiment_data = {
            'source': row_dict['source'],
            'id': row_dict['id'],
            'title': row_dict['title'],
            'content': row_dict['content'],
            'comments': flattened_comments,
            'created_utc': int(row_dict['created_utc']),
            'timestamp': int(row_dict['timestamp']),
            'partition_date': row_dict['partition_date'],
            'content_sentiment': {
                'score': str(row_dict['content_sentiment']['score']),
                'sentiment': row_dict['content_sentiment']['sentiment']
            },
            'comments_sentiment': row_dict['comments_sentiment'] if row_dict['comments_sentiment'] else []
        }
        
        # Log final comments data
        logger.info(f"Final comments for id {row_dict['id']}: {sentiment_data['comments']}")
        
        # Changed: Include all records, not just those with comments or content
        sentiment_results.append(sentiment_data)
        logger.info(f"Added sentiment data for id: {row_dict['id']}")
            
    except Exception as e:
        logger.error(f"Error processing row: {str(e)}")
        continue

# Filter out any null values before creating DataFrame
sentiment_results = [
    {k: v for k, v in data.items() if v is not None}
    for data in sentiment_results
]

# Define output schema for sentiment data
sentiment_schema = StructType([
    StructField("source", StringType(), True),
    StructField("id", StringType(), True),
    StructField("title", StringType(), True),
    StructField("content", StringType(), True),
    StructField("comments", ArrayType(StringType()), True),  # Single array
    StructField("created_utc", LongType(), True),
    StructField("timestamp", LongType(), True),
    StructField("partition_date", StringType(), True),
    StructField("content_sentiment", StructType([
        StructField("score", StringType(), True),
        StructField("sentiment", StringType(), True)
    ]), True),
    StructField("comments_sentiment", ArrayType(
        StructType([
            StructField("score", StringType(), True),
            StructField("sentiment", StringType(), True)
        ])
    ), True)
])

# Create pandas DataFrame
pd_df = pd.DataFrame(sentiment_results)

# Convert pandas DataFrame to Spark DataFrame with explicit schema
spark_df = spark.createDataFrame(pd_df, schema=sentiment_schema)

# Convert to DynamicFrame
sentiment_dynamic_frame = DynamicFrame.fromDF(spark_df, glueContext, "sentiment_data")

# Write to S3 with partition columns that exist in the data
logger.info("Writing results to S3...")
glueContext.write_dynamic_frame.from_options(
    frame=sentiment_dynamic_frame,
    connection_type="s3",
    connection_options={
        "path": "s3://processed-data-social-comment/sentiment/",
        "partitionKeys": ["source", "partition_date"]
    },
    format="json"
)

# Write to MongoDB
logger.info("Writing to MongoDB Atlas...")

try:

    # Log DataFrame info before MongoDB conversion
    logger.info(f"DataFrame info before MongoDB conversion:")
    logger.info(f"Total records: {len(pd_df)}")
    logger.info("Source distribution:")
    print(pd_df['source'].value_counts())

    # Convert DataFrame to list of dictionaries for MongoDB 
    records = []
    source_tracking = {'facebook': 0, 'youtube': 0, 'reddit': 0}
    
    for _, row in pd_df.iterrows():
        try:
            record = row.to_dict()
            source = record.get('source', 'unknown')
            
            # Track sources
            if source in source_tracking:
                source_tracking[source] += 1
            
            logger.info(f"Processing record - Source: {source}, ID: {record.get('id')}")
            
            # Ensure source is not None or empty
            if not record.get('source'):
                logger.warning(f"Skipping record with invalid source: {record.get('id')}")
                continue

            # Ensure comments is a list
            if 'comments' in record:
                comments = record['comments']
                if not isinstance(comments, list):
                    if pd.isna(comments) or comments is None:
                        comments = []
                    else:
                        comments = list(comments)
                record['comments'] = [str(c) for c in comments if c and str(c).strip()]
            else:
                record['comments'] = []
                
            # Convert numpy/pandas types to Python native types
            record = json.loads(json.dumps(record, default=str))
            records.append(record)
            
        except Exception as e:
            logger.error(f"Error converting row to MongoDB record: {str(e)}")
            continue
    
    # Debug log the records after creating them
    logger.info(f"Converted {len(records)} records for MongoDB")
    logger.info("Source distribution in converted records:")
    sources = {}
    for r in records:
        src = r.get('source')
        sources[src] = sources.get(src, 0) + 1
    logger.info(str(sources))

    # Initialize MongoDB client
    from pymongo import MongoClient
    
    # MongoDB Atlas connection string - removed directConnection since we're connecting to a cluster
    connection_string = "mongodb+srv://admin:admin@team5-social-media.5whnv.mongodb.net/?retryWrites=true&w=majority&appName=team5-social-media"
    
    # Create MongoDB client with updated options
    client = MongoClient(
        connection_string,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=5000,
        retryWrites=True
    )
    
    # Get database and collection
    db = client[MONGODB_DATABASE]
    collection = db[MONGODB_COLLECTION]
    
    # Insert documents in batches with retry logic
    batch_size = 100
    for i in range(0, len(records), batch_size):
        try:
            batch = records[i:i + batch_size]
            collection.insert_many(batch, ordered=False)
            logger.info(f"Inserted batch {i//batch_size + 1} of {len(records)//batch_size + 1}")
        except Exception as batch_error:
            logger.error(f"Error inserting batch: {str(batch_error)}")
            continue
    
    logger.info("Successfully written to MongoDB Atlas!")
    
    # Close MongoDB connection
    client.close()

except Exception as e:
    logger.error(f"Error writing to MongoDB: {str(e)}")
    raise e

job.commit()