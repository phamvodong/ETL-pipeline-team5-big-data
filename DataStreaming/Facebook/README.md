# Facebook Comments Scraper

This project is a Facebook Comments Scraper that automates the process of logging into Facebook, navigating to a specific post, extracting comments, and saving the post data to a CSV file. It utilizes Selenium for browser automation.

---

## **Features**

- **Login to Facebook**: Automates logging into Facebook using your credentials.
- **Extract Post Content**: Scrapes the main content of a Facebook post.
- **Extract Comments**: Collects all visible comments from a Facebook post, including nested replies (if available).
- **Save Data**: Saves the post content and comments in a structured CSV format.

---

## **Requirements**

### Tools and Libraries:

- Python 3.8+
- Google Chrome (latest version)
- Selenium WebDriver
- [WebDriver Manager](https://pypi.org/project/webdriver-manager/)

### Install Dependencies:

Install dependencies with:

```bash
pip install -r requirements.txt
```

---

## **Usage**

### Step 1: **Set Up the Environment**

1. Ensure that you have Python installed and accessible in your terminal.
2. Install Google Chrome and ensure it is up-to-date.

### Step 2: **Edit the Script**

- Replace the `email` and `password` variables in the `main()` function with your Facebook credentials.
- Update the `post_url` variable with the URL of the Facebook post you want to scrape.

### Step 3: **Run the Script**

Run the script using:

```bash
python crawler.py
```

### Step 4: **Check the Output**

- The script saves the post data, including comments, in a CSV file within the `facebook_data` folder (created automatically).
- The file is named with a timestamp: `post_data_YYYY-MM-DD_HH-MM-SS.csv`.

---

## **Features in Detail**

### **1. Login to Facebook**

The script automates the login process, including handling optional 2-Step Verification (requires manual input).

### **2. Extract Post Content**

Scrapes the main content of the Facebook post using the specified URL.

### **3. Extract Comments**

- The script scrolls through the comment section and loads additional comments by clicking "View More" buttons.
- Captures the names of commenters and their comments.

### **4. Save Data**

The data is saved in a structured CSV file with the following columns:

- **PostID**: The Facebook post URL.
- **PostContent**: The main content of the Facebook post.
- **PostTitle**: Same as the content (can be customized later).
- **PostComments**: All the comments captured.

---

## **Folder Structure**

```text
fbCrawler/
├── facebook_data/                           # Folder for saving scraped data
│   ├── post_data_YYYY-MM-DD_HH-MM-SS.csv    # Output file
├── crawler.py                           # Main script
├── requirements.txt                         # Dependencies
└── README.md                                # Project documentation
```

---

## **Known Issues and Limitations**

1. **2-Step Verification**: If enabled, the script will pause for manual input of the verification code.
2. **Dynamic Facebook Changes**: The script might break if Facebook updates its HTML structure.
3. **Rate Limits**: Frequent usage may trigger Facebook's rate limits or CAPTCHA challenges.

---

## **Future Enhancements**

- Add support for handling CAPTCHA challenges.
- Handle exceptions more gracefully for better error reporting.
