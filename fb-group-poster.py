import os
import json
import time
import asyncio
import traceback

from apify import Actor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# For explicit waits
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

async def main():
    # Initialize the Actor environment
    await Actor.init()
    
    # Get the actor input
    input_data = await Actor.get_input()
    urls_str = input_data.get("Facebook_Profile_URL", "")
    groups_links_list = [url.strip() for url in urls_str.split(",") if url.strip()]
    message = input_data.get("Message", "")
    delay = input_data.get("Delay", 15)
    
    # Parse Cookies JSON if provided
    cookies_input = input_data.get("Cookies", "")
    cookies = []
    if cookies_input:
        try:
            cookies = json.loads(cookies_input)
        except Exception as e:
            print("Error parsing Cookies JSON:", e)
            traceback.print_exc()
    
    # Get optional credentials
    username = input_data.get("Username", "")
    password = input_data.get("Password", "")
    
    if not groups_links_list or not message:
        print("❌ Error: Missing required input fields (Facebook group URLs or message).")
        return

    # Configure Selenium Chrome options
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = "/usr/bin/chromium"  # Make sure Chromium is installed in your Docker image
    service = Service(executable_path="/usr/bin/chromedriver")  # Ensure ChromeDriver is installed
    
    try:
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print("❌ Error starting Chrome WebDriver:", e)
        traceback.print_exc()
        return

    try:
        driver.get("https://www.facebook.com")
        time.sleep(2)
        
        # Login via credentials or cookies
        if username and password:
            driver.find_element(By.ID, "email").send_keys(username)
            driver.find_element(By.ID, "pass").send_keys(password)
            driver.find_element(By.NAME, "login").click()
            time.sleep(5)
        elif cookies:
            for cookie in cookies:
                if "sameSite" in cookie and cookie["sameSite"] not in ["Strict", "Lax", "None"]:
                    print(f"Cookie '{cookie.get('name')}' has invalid sameSite value '{cookie['sameSite']}', removing it.")
                    del cookie["sameSite"]
                driver.add_cookie(cookie)
            driver.refresh()
            time.sleep(3)
        else:
            print("❌ Error: No authentication method provided (either cookies or username/password).")
            return

        wait = WebDriverWait(driver, 15)
        
        for group_url in groups_links_list:
            driver.get(group_url)
            time.sleep(3)
            
            # 1) Click the Discussion tab using a locator that finds a tab containing the word "Discussion"
            try:
                discussion_tab = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//a[@role='tab' and contains(., 'Discussion')]"))
                )
                discussion_tab.click()
                time.sleep(2)
            except Exception as e:
                print(f"⚠️ Could not click Discussion tab on {group_url}: {e}")
                traceback.print_exc()
                continue

            # 2) Click "Write something..." button
            try:
                write_something = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and contains(., 'Write something')]"))
                )
                write_something.click()
                time.sleep(2)
            except Exception as e:
                print(f"⚠️ Could not click 'Write something...' on {group_url}: {e}")
                traceback.print_exc()
                continue

            # 3) Type text into the popup field (using aria-label; adjust if needed)
            try:
                popup_field = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Create a public post…']"))
                )
                popup_field.click()
                popup_field.send_keys(message)
                time.sleep(1)
            except Exception as e:
                print(f"⚠️ Could not type into the popup field on {group_url}: {e}")
                traceback.print_exc()
                continue

            # 4) Click the Post button
            try:
                post_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Post']"))
                )
                post_button.click()
                time.sleep(delay)
                print(f"✅ Successfully posted to {group_url}")
            except Exception as e:
                print(f"⚠️ Failed to post in {group_url}: {e}")
                traceback.print_exc()

    except Exception as e:
        print(f"❌ Error during processing: {e}")
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    asyncio.run(main())
