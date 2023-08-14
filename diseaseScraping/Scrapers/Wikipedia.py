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

SOURCE_NAME = 'Wikipedia'
HREF_BASE = "https://en.wikipedia.org"
BASE_URL = "https://en.wikipedia.org/wiki/List_of_diseases_(0%E2%80%939)"
if __name__ == '__main__':
    print(os.getcwd())
    firefox_options = Options()
    # firefox_options.add_argument("--headless")  # Run Firefox in headless mode
    driver = webdriver.Firefox(options=firefox_options)
    driver.install_addon('ublock_origin-1.49.2.xpi')

    driver.get(BASE_URL)

    time.sleep(1)

    element = driver.find_element(By.CLASS_NAME,"hlist")
    element = element.find_element(By.TAG_NAME,"ul")
    indices = element.find_elements(By.TAG_NAME,"a")
    
    links = []

    element = driver.find_element(By.CLASS_NAME,"mw-parser-output")
    elements = element.find_elements(By.TAG_NAME,"ul")
    for element in elements:
        links.extend([(x.get_attribute('href'),x.get_attribute('title')) for x in element.find_elements(By.TAG_NAME,"a")])
    
    element = driver.find_element(By.CLASS_NAME,"mw-parser-output")
    elements = element.find_elements(By.TAG_NAME,"ul")[1:]
    for element in elements:
        links.extend([(x.get_attribute('href'),x.get_attribute('title')) for x in element.find_elements(By.TAG_NAME,"a")])
    print(f"{len(links)} links so far...")
    
    indices = [x.get_attribute('href') for x in indices[1:]]
    for index in indices:
        driver.get(index)
        element = driver.find_element(By.CLASS_NAME,"mw-parser-output")
        elements = element.find_elements(By.TAG_NAME,"ul")[1:]
        for element in elements:
            links.extend([(x.get_attribute('href'),x.get_attribute('title')) for x in element.find_elements(By.TAG_NAME,"a")])
        print(f"{len(links)} links so far...")
        # break
        

    print(f"Retrieved {len(links)} links")

    file_set = set()
    diseases_path = os.getcwd() + f"\\Diseases\\{SOURCE_NAME}"
    for root,dirs,files in os.walk(diseases_path):
        for file in files:
            file_set.add(file)

    templinks = links
    links = []
    for link in templinks:
        try:
            if not "List_Of_Diseases" in link[0]:
                links.append(link)
        except:
            continue
    # links = set(links)
    for link,title in links[27:]:
        if link is None:
            continue
        if "http" in link:
            url = link
        else:
            url = HREF_BASE+link
        
        path = sanitize_filename(title).strip()
        if f"{path}.json" in file_set:
            print(f"Skipping {path}")
            continue

        print(f"Retrieving {url}")
        
        driver.get(url)
        # time.sleep(5)

        html = driver.page_source
        ScrapingFramework.html_text_to_file(url,html,title,SOURCE_NAME)

        print(f"Retrieved {url}")
    driver.close()