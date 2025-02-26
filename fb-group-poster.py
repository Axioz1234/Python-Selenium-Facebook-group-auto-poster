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

# Import for explicit waits
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

async def main():
    # Initialize the Actor environment
    await Actor.init()
    
    # Get the actor input
    input_data = await Actor.get_input()
    # Expecting a JSON input with keys:
    # "Facebook_Profile_URL", "Message", "Delay", "Cookies", "Username", "Password"
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
    options.add_argument("--window-size=1920,1080")
    options.binary_location = "/usr/bin/chromium"  # Path to Chromium in Docker
    service = Service(executable_path="/usr/bin/chromedriver")  # Path to ChromeDriver

    try:
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print("❌ Error starting Chrome WebDriver:", e)
        traceback.print_exc()
        return

    try:
        driver.get("https://www.facebook.com")
        time.sleep(2)
        
        # Log in via credentials if provided; otherwise, add cookies.
        if username and password:
            driver.find_element(By.ID, "email").send_keys(username)
            driver.find_element(By.ID, "pass").send_keys(password)
            driver.find_element(By.NAME, "login").click()
            time.sleep(5)
        elif cookies:
            for cookie in cookies:
                if "sameSite" in cookie:
                    # Accept both correct and lower-case variants
                    if cookie["sameSite"] == "lax":
                        cookie["sameSite"] = "Lax"
                    elif cookie["sameSite"] == "no_restriction":
                        cookie["sameSite"] = "None"
                    elif cookie["sameSite"] not in ["Strict", "Lax", "None"]:
                        print(f"Cookie '{cookie.get('name')}' has invalid sameSite value '{cookie['sameSite']}', removing it.")
                        del cookie["sameSite"]
                driver.add_cookie(cookie)
            driver.refresh()
            time.sleep(3)
        else:
            print("❌ Error: No authentication method provided (either cookies or username/password).")
            return

        wait = WebDriverWait(driver, 20)
        
        for group_url in groups_links_list:
            driver.get(group_url)
            time.sleep(3)
            
            # Step 1: Click "Write something..." button
            # Using your provided absolute XPath:
            write_xpath = "//*[@id='mount_0_0_gi']/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div[2]/div/div/div[4]/div/div/div[2]/div/div/div[2]/div[1]/div/div/div/div[1]/div"
            try:
                write_something = wait.until(EC.element_to_be_clickable((By.XPATH, write_xpath)))
                driver.execute_script("arguments[0].scrollIntoView(true);", write_something)
                time.sleep(1)
                write_something.click()
                print(f"✅ Clicked 'Write something...' on {group_url}")
                time.sleep(2)
            except Exception as e:
                print(f"⚠️ Could not click 'Write something...' on {group_url}: {e}")
                traceback.print_exc()
                continue
            
            # (For now, we stop here; later steps: type text, click Post, etc.)
            
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    asyncio.run(main())
