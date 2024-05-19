from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

url = "https://my.ucell.uz/Account/Login"

# Chrome options to disable cache
chrome_options = Options()
chrome_options.add_argument("--disable-cache")

# Initialize the WebDriver with Chrome options
driver = webdriver.Chrome(options=chrome_options)

# Open the URL
driver.get(url)

# Refresh the page every 1 minute (60 seconds)
while True:
    time.sleep(50)  # Wait for 60 seconds
    driver.refresh()  # Refresh the page without clearing cache
