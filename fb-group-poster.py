import os
import json
import time
import asyncio
from apify import Actor  # Updated import
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

async def main():
    # Initialize the Actor environment
    await Actor.init()
    
    # Now it's safe to get the actor input
    input_data = await Actor.get_input()
    
    # Get group URLs and split them into a list
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
    # Set the binary location for Chromium (make sure it's installed in your Docker image)
    options.binary_location = "/usr/bin/chromium"
    
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get('https://www.facebook.com')
        time.sleep(2)
        
        # Use credentials if provided; otherwise, try cookies
        if username and password:
            driver.find_element(By.ID, "email").send_keys(username)
            driver.find_element(By.ID, "pass").send_keys(password)
            driver.find_element(By.NAME, "login").click()
            time.sleep(5)
        elif cookies:
            for cookie in cookies:
                driver.add_cookie(cookie)
            driver.refresh()
            time.sleep(3)
        else:
            print("❌ Error: No authentication method provided (either cookies or username/password).")
            return
        
        for group in groups_links_list:
            driver.get(group)
            time.sleep(3)
            try:
                post_box = driver.find_element(By.XPATH, "//div[@aria-label='Create a public post…']")
                post_box.click()
                time.sleep(2)
                post_box.send_keys(message)
                time.sleep(2)
                
                post_button = driver.find_element(By.XPATH, "//*[@aria-label='Post']")
                post_button.click()
                time.sleep(delay)
                
                print(f"✅ Successfully posted to {group}")
            except Exception as e:
                print(f"⚠️ Failed to post in {group}: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()

if __name__ == '__main__':
    asyncio.run(main())
