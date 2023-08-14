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

SOURCE_NAME = "DrugsDOTcom"
BASE_URL = 'https://www.drugs.com/medical_conditions.html'
HREF_BASE = 'https://www.drugs.com'

if __name__ == '__main__':
    firefox_options = Options()
    firefox_options.add_argument("--headless")  # Run Firefox in headless mode
    driver = webdriver.Firefox(options=firefox_options)
    driver.install_addon('ublock_origin-1.49.2.xpi')

    driver.get(BASE_URL)
    time.sleep(1)

    links = []
    index_links = []
    index_links.extend(ScrapingFramework.links_from_containers_html(driver.page_source,'nav','ddc-paging'))

    for index_link in index_links:
        if "http" in index_link['href']:
            url = index_link['href']
        else:
            url = HREF_BASE+index_link['href']

        print(f"Retrieving {url}")
        
        driver.get(url)
        time.sleep(5)

        links.extend(ScrapingFramework.links_from_containers_html(driver.page_source,'ul','ddc-list-column-2'))

        print(f"Retrieved {url}")

        print(f"Retrieved {len(links)} links so far...")

    # links = set(links)

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
        try:
            if f"{path}.json" in file_set:
                print(f"Skipping {path}")
                continue
        except:
            continue


        print(f"Retrieving {url}")
        
        driver.get(url)
        time.sleep(5)

        html = driver.page_source
        title = link.text
        ScrapingFramework.html_text_to_file(url,html,title,SOURCE_NAME)

        print(f"Retrieved {url}")
    driver.close()