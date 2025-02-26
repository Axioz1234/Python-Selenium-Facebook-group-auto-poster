import os
import time
import Apify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

async def main():
    # Get input from Apify
    input_data = await Apify.get_input()

    # Get required inputs
    groups_links_list = input_data.get("Facebook_Profile_URL", [])
    message = input_data.get("Message", "")
    delay = input_data.get("Delay", 15)  # Default delay is 15 seconds
    cookies = input_data.get("Cookies", [])

    if not groups_links_list or not message:
        print("❌ Error: Missing required input fields (groups or message).")
        return

    # Configure Selenium Chrome Driver
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")

    service = Service("chromedriver")  # Ensure the ChromeDriver is available
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Open Facebook
        driver.get('https://www.facebook.com')
        time.sleep(2)

        # Add cookies if provided
        if cookies:
            for cookie in cookies:
                driver.add_cookie(cookie)
            driver.refresh()
            time.sleep(3)
