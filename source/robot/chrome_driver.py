from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException
import os
import traceback
from .chrome_webdriver_update import download_driver, clear_cache

wd = os.getcwd()
cache_directory = wd + r'\source\robot\cache'
chrome_binary_path = wd + r'\source\robot\chromedriver'

def chrome_driver(show_browser):
    options = webdriver.ChromeOptions()
    # options.add_argument("user-data-dir=" + cache_directory)	
    # options.add_argument('headless')  # hiding browser page
    options.add_argument("--log-level=3")
    # options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'\
        #  (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.51")
    options.add_argument("--disable-gpu")
    # options.add_argument("-no-sandbox")
    options.add_argument("--disable-notifications")
    options.add_argument("--ignore-certificate-errors-spki-list")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors")
    options.add_argument("--disable-single-click-autofill")

    try:
        repo = 'https://raw.githubusercontent.com/peymanj/chromedriver/main/{version}/chromedriver.exe'
        driver_path = download_driver(repo)
        # driver = webdriver.Chrome(ChromeDriverManager(cache_valid_range=1000).install(),  chrome_options=options)
        driver = webdriver.Chrome(driver_path,  chrome_options=options)

    except Exception as e:
        traceback.print_exc()
        print(e)
        clear_cache()
        return str(e)
    
    
    # driver.set_page_load_timeout(30)
    if not show_browser:
        driver.set_window_position(-10000,0)
    else:
        driver.set_window_position(200,200)
    
    return driver	
