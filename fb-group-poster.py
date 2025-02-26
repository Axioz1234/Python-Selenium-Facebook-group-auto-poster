import os
import time
import Apify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

async def main():
    # Get input from Apify
    input_data = await Apify.get_input()

    # Load Facebook credentials from environment variables
    account = os.getenv("FB_ACCOUNT")
    password = os.getenv("FB_PASSWORD")

    # Get group links and message from Apify input
    groups_links_list = input_data.get("groups_links_list", [])
    message = input_data.get("message", "")

    if not account or not password:
        print("❌ Error: Missing Facebook credentials in environment variables!")
        return

    if not groups_links_list or not message:
        print("❌ Error: Missing required input fields (groups or message).")
        return

    # Configure Selenium Chrome Driver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  # Run in headless mode for Apify
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 2})

    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Login to Facebook
        driver.get('https://www.facebook.com')
        time.sleep(2)

        driver.find_element(By.ID, "email").send_keys(account)
        driver.find_element(By.ID, "pass").send_keys(password)
        driver.find_element(By.NAME, "login").click()
        time.sleep(5)

        # Post on each group
        for group in groups_links_list:
            driver.get(group)
            time.sleep(3)
            
            try:
                post_box = driver.find_element(By.XPATH, "//div[@aria-label='Create a public post…']")
                post_box.click()
                time.sleep(2)
                post_box.send_keys(message)
                time.sleep(2)

                # Click the post button
                post_button = driver.find_element(By.XPATH, "//*[@aria-label='Post']")
                post_button.click()
                time.sleep(5)

                print(f"✅ Successfully posted to {group}")

            except Exception as e:
                print(f"⚠️ Failed to post in {group}: {e}")

    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        driver.quit()

Apify.run(main)