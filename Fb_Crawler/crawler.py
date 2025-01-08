from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains  # Make sure this import is included

import time
import os
from datetime import datetime
import csv

# Setup Chrome WebDriver (automatically downloads the latest ChromeDriver)
chrome_options = Options()
chrome_options.add_argument("--disable-notifications")

# Initialize the WebDriver with the options and the driver service
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), 
    options=chrome_options
)

def login_to_facebook(email, password):
    driver.get("https://www.facebook.com/login")

    # Wait for the login page to load
    time.sleep(2)

    # Find and fill the email and password fields
    driver.find_element(By.ID, "email").send_keys(email)
    driver.find_element(By.ID, "pass").send_keys(password)
    
    # Submit the login form
    driver.find_element(By.ID, "loginbutton").click()

    # Wait for the 2-step verification (if it's required)
    time.sleep(5)

    # Check if 2-step verification is triggered (check for the code input field)
    if driver.find_elements(By.ID, ":r1:"):
        print("2-Step Verification required!")
        code = input("Please enter the 2-Step verification code: ")

        # Find the input field for the 2-step verification using the ID ":r1:" and enter the code
        driver.find_element(By.ID, ":r1:").send_keys(code)
        driver.find_element(By.ID, ":r1:").send_keys(Keys.RETURN)
        
        print("Verification code submitted. Proceeding...")

        # Wait for the "Continue" button to appear and click it
        time.sleep(2)  # Wait briefly for the "Continue" button to load
        try:
            continue_button = driver.find_element(By.XPATH, "//span[text()='Continue']")
            continue_button.click()
            print("Clicked 'Continue' button. Proceeding with login...")
        except Exception as e:
            print(f"Failed to click 'Continue' button: {e}")
        
        # Wait for the login process to complete after verification
        time.sleep(5)

def get_comments(post_url):
    driver.get(post_url)
    time.sleep(3)

    time.sleep(20)
    
    # Click on the "Most relevant" section to toggle comments
    print("Finding on the 'Most relevant' button to toggle comments...")
    most_relevant_button = driver.find_element(By.XPATH, "//div[contains(@class, 'x6s0dn4 x78zum5 xdj266r x11i5rnm xat24cr x1mh8g0r xe0p6wg')]")
    most_relevant_button.click()
    time.sleep(2)

    # Click on the "All comments" option
    last_menu_item = driver.find_element(By.XPATH, "(//div[@role='menuitem'])[last()]")
    last_menu_item.click()
    time.sleep(2)

    # Locate the comment section div
    comment_section = driver.find_element(By.XPATH, "//div[contains(@class, 'html-div x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x1gslohp')]")
    comment_section.click()
    
    # Obtain the initial scroll height
    previous_scroll_height = comment_section.size["height"]
    # Scroll to load comments inside the comment container
    for _ in range(100):  # Scroll 3 times inside the comment section
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        print(comment_section.size)

        view_more_buttons = driver.find_elements(By.XPATH, "//div[contains(@class, 'x1i10hfl xjbqb8w xjqpnuy xa49m3k xqeqjp1 x2hbi6w x13fuv20 xu3j5b3 x1q0q8m5 x26u7qi x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xdl72j9 xe8uvvx xdj266r x11i5rnm xat24cr x2lwn1j xeuugli xexx8yu x18d9i69 xkhd6sd x1n2onr6 x16tdsg8 x1hl2dhg xggy1nq x1ja2u2z x1t137rt x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x3nfvp2 x87ps6o x1lku1pv x1a2a7pz x6s0dn4 xi81zsa x1q0g3np x1iyjqo2 xs83m0k xsyo7zv x1mnrxsn')]")
        
        see_more_buttons = driver.find_elements(By.XPATH, "//div[contains(@class, 'x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1sur9pj xkrqix3 xzsf02u x1s688f')]")

        # Loop through all the "View More" buttons and click on them
        for button in view_more_buttons:
            try:
                # You can use ActionChains for better handling of clicking on the button
                ActionChains(driver).move_to_element(button).click().perform()
                print("Clicked on 'View More' button")
                time.sleep(2)  # Add a delay to ensure the page loads
            except Exception as e:
                print(f"Failed to click on 'View More' button: {e}")
        
        for button in see_more_buttons:
            try:
                # You can use ActionChains for better handling of clicking on the button
                ActionChains(driver).move_to_element(button).click().perform()
                print("Clicked on 'See More' button")
                time.sleep(2)  # Add a delay to ensure the page loads
            except Exception as e:
                print(f"Failed to click on 'See More' button: {e}")
        
        time.sleep(3)
        current_scroll_height = comment_section.size["height"]
        print(f"Current scroll height: {comment_section.size['height']}")
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        # # If scroll height hasn't changed, it means we've reached the end
        if previous_scroll_height == current_scroll_height:
            print("End of the comment section reached.")
            # Prompt the user to continue or break
            user_input = input("Do you want to stop scrolling? (Y/N): ")
            if user_input.strip().lower() == 'y':
                print("Stopping scroll...")
                break
            else:
                print("Still scrolling...")
        
        # # Update the previous scroll height for the next iteration
        previous_scroll_height = current_scroll_height

    
    # Collect comments
    comments = []

    # Find all comment divs with class 'xwib8y2'
    comment_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'xwib8y2')]")
    
    for comment_element in comment_elements:
        try:
            # Extract the commenter's name
            name = comment_element.find_element(By.XPATH, ".//span[contains(@class, 'x3nfvp2')]").text.strip()
            
            # Extract the comment text
            comment_text = comment_element.find_element(By.XPATH, ".//div[contains(@class, 'xdj266r')]").text.strip()

            if name and comment_text:
                comments.append({"name": name, "comment": comment_text})

        except Exception as e:
            print(f"Error extracting comment: {e}")

    return comments

def get_post_content(driver):
    try:
        post_content_element = driver.find_element(By.XPATH, "//div[contains(@data-ad-preview, 'message')]")
        return post_content_element.text.strip()
    except Exception as e:
        print(f"Failed to get post content: {e}")
        return ""


def save_post_data(post_id, post_content, post_title, comments, folder_path="fbCrawlerData/"):
    # Create directory if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Save data to a CSV file
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    csv_filename = os.path.join(folder_path, f"post_data_{timestamp}.csv")

    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # Write header row
        writer.writerow(["PostID", "PostContent", "PostTitle", "PostComments"])
        # Write the post data
        writer.writerow([
            post_id,
            post_content,
            post_title,
            comments
        ])

    print(f"Post data saved to {csv_filename}")

def main():
    # Replace these with your Facebook credentials
    email = ""
    password = ""
    post_url = "https://www.facebook.com/pfbid0rBx5QQz4QPBkqMSfNcXK96JkwPwSUz2AWA9uuHFDq171pNphHmA4WwEXB7niiuarl"# Replace with the Facebook post URL
    
    # Login to Facebook
    login_to_facebook(email, password)
    
    # Get comments for the given post
    comments = get_comments(post_url)
    
    # Print all comments
    print("Comments:")
    for idx, comment in enumerate(comments, 1):
        print(f"{idx}. {comment['name']}: {comment['comment']}")

    post_content = get_post_content(driver)  # Extract the post content

    
    comments_array = [f"{comment['comment']}" for comment in comments]
    
    # Save the post data
    save_post_data(post_url, post_content, post_content, comments_array)
    # save_post_data("https://www.facebook.com/watch/?v=2793784774115213", post_content, post_content, comments_array)
    
    driver.quit()

if __name__ == "__main__":
    main()