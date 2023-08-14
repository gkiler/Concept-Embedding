import ScrapingFramework

import time
import requests
import os
from bs4 import BeautifulSoup
import io
import json
from os.path import exists
from datetime import datetime
from pathvalidate import sanitize_filename #not native
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

SOURCE_NAME = "WebMD"
BASE_URL = 'https://www.webmd.com/a-to-z-guides/health-topics'
HREF_BASE = ''

if __name__ == '__main__':
    firefox_options = Options()
    firefox_options.add_argument("--headless")  # Run Firefox in headless mode
    driver = webdriver.Firefox(options=firefox_options)
    driver.install_addon('ublock_origin-1.49.2.xpi')

    time.sleep(1)

    links = []
    for i in range(0,26):
        time.sleep(5)
        driver.get(BASE_URL)
        index_container = driver.find_element(By.CSS_SELECTOR,".az-index-nav-letters")
        index_container.find_elements(By.CSS_SELECTOR,"[data-metrics-link]")[i].click()
        links.extend(ScrapingFramework.links_from_containers_html(driver.page_source,'ul','az-index-results-group-list'))

    links = set(links)

    print(f"Retrieved {len(links)} links")

    file_set = set()
    diseases_path = os.getcwd() + f"\\Diseases\\{SOURCE_NAME}"
    for root,dirs,files in os.walk(diseases_path):
        for file in files:
            file_set.add(file)

    for link in links:
        title = link.text

        if "http" in link['href']:
            url = link['href']
        else:
            url = HREF_BASE+link['href']
        
        path = sanitize_filename(title).strip()
        if f"{path}.json" in file_set:
            print(f"Skipping {path}")
            continue

        print(f"Retrieving {url}")
        
        driver.get(url)
        time.sleep(5)

        html = driver.page_source
        ScrapingFramework.html_text_to_file(url,html,link.text,SOURCE_NAME)

        print(f"Retrieved {url}")
    driver.close()