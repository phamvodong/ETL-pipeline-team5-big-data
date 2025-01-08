# Facebook Comment Crawler

This project is a Facebook comment crawler built with Python and Selenium. The crawler automates the process of logging into Facebook, navigating to a post, extracting its details (title, content, and comments), and saving them into a structured file format.

## Features

- Logs into Facebook with provided credentials.
- Crawls posts from a URLs.
- Extracts:
  - Post ID
  - Post Title
  - Post Content
  - Comments (including usernames and timestamps).
- Saves the extracted data into a CSV file.

## Requirements

To run the crawler, ensure you have the following installed:

- Python 3.7+
- Chrome browser
- Chromedriver (automatically managed by `webdriver-manager`)

## Installation

1. **Install dependencies:**
   Use `pip` to install the required libraries:

   ```bash
   pip install -r requirements.txt
   ```

2. **Update configuration:**
   Replace your Facebook credentials and target post URLs in the script:
   ```python
   email = "your_facebook_email"
   password = "your_facebook_password"
   ```

## Usage

1. **Run the crawler:**
   Execute the script in the terminal:

   ```bash
   python crawler.py
   ```

2. **View Results:**
   Extracted data will be saved in the `fbCrawlerData` folder as a CSV file, with the following structure:
   ```csv
   Post ID, Post Title, Post Content, Post Comments
   123456789, "Example Title", "This is the post content.", "['Comment 1', 'Comment 2']"
   ```

## File Structure

```
│
├── crawler.py               # Main script
├── fbCrawlerData/           # Output folder for CSV files
├── requirements.txt         # Dependency list
├── README.md                # Project documentation
```

## Dependencies

This project uses the following libraries:

- Selenium
- WebDriver Manager
- datetime
- csv
- os

## Notes

- **Facebook Credentials:** Your Facebook account credentials must be used for login. It is recommended to use a test or throwaway account for this purpose.
- **Browser Automation:** This project uses Chrome and Chromedriver for automation.
- **Privacy Disclaimer:** Ensure that you comply with Facebook's Terms of Service and data privacy laws when using this tool.
