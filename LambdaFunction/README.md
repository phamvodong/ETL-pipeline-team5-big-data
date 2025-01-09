### **Scripts Overview**

---

### **General Workflow**

| Script                  | Purpose                                  | Key Features                                                                                                                                                                                                                    |
| ----------------------- | ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `facebook_processor.py` | Process Facebook CSV data uploaded to S3 | - Extracts numeric IDs from URLs or generates MD5 hashes as IDs<br>- Parses comments, cleans them, and stores the processed data as JSON files in another S3 bucket<br>- Uses the current timestamp for partitioning data in S3 |
| `kinesis_to_s3.py`      | Transfers data from AWS Kinesis to S3    | - Decodes base64-encoded Kinesis stream data<br>- Writes JSON data to an S3 bucket with a path structured by the source and timestamp                                                                                           |
| `reddit_processor.py`   | Process Reddit CSV data uploaded to S3   | - Parses and cleans comments from CSV data<br>- Stores processed data in an S3 bucket with appropriate metadata and timestamped partitioning                                                                                    |
| `youtube_processor.py`  | Process YouTube CSV data uploaded to S3  | - Cleans and extracts content and comments from the dataset<br>- Parses timestamps and stores processed JSON files in S3 with partitioned paths                                                                                 |

### **Potential Enhancements**

- **Error Handling**:
  - Add retry logic for failed S3 operations (e.g., `s3.put_object`).
  - Improve logging for debugging and audit trails.
- **Performance**:

  - Use AWS Lambda layers for shared libraries (like `TextBlob`) to reduce redundancy in deployments.
  - Leverage AWS Glue for larger-scale ETL processes.

- **Testing**:

  - Create comprehensive unit tests for each script.
  - Mock AWS services using libraries like `moto` to validate S3 interactions locally.

- **Monitoring**:
  - Integrate AWS CloudWatch to monitor Lambda invocations, errors, and processing metrics.

### **Notes:**

Install dependencies with:

```bash
pip install -r requirements.txt
```
