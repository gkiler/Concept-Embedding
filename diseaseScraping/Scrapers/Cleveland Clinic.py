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

SOURCE_NAME = "Cleveland Clinic"
BASE_URL = 'https://my.clevelandclinic.org/health/diseases'
HREF_BASE = 'https://my.clevelandclinic.org/'

if __name__ == '__main__':

    firefox_options = Options()
    firefox_options.add_argument("--headless")  # Run Firefox in headless mode
    driver = webdriver.Firefox(options=firefox_options)
    driver.install_addon('ublock_origin-1.49.2.xpi')

    driver.get(BASE_URL)
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR,"button.library-search-nav__browse-btn.js-library-search-nav__browse-btn").click()
    time.sleep(1)
    try:
        element = driver.find_element(By.CSS_SELECTOR, '[class="4ea145c8-50ee-441e-b90b-91733b641527 az-letters js-az-letter"]')
    except:
        pass
    time.sleep(1)
    alphabet_buttons = driver.find_elements(By.CSS_SELECTOR, '.js-enabled')

    links = []
    for button in alphabet_buttons:
        print("Retrieving indices...")
        button.click()
        time.sleep(2.5)
        links.extend(ScrapingFramework.links_from_containers_html(driver.page_source,'div','l-3col--1'))
        links.extend(ScrapingFramework.links_from_containers_html(driver.page_source,'div','l-3col--2'))
        links.extend(ScrapingFramework.links_from_containers_html(driver.page_source,'div','l-3col--3'))
        print("Retrieved an index")

    links = set(links)

    
    print(f"Retrieved {len(links)} links")

    file_set = set()
    diseases_path = os.getcwd() + f"\\Diseases\\{SOURCE_NAME}"
    for root,dirs,files in os.walk(diseases_path):
        for file in files:
            file_set.add(file)
    
    for link in links:
        url = link['href']
        title = link.text
        path = sanitize_filename(title).strip()
        if f"{path}.json" in file_set:
            print(f"Skipping {path}")
            continue

        print(f"Retrieving {url}")
        try:
            driver.get(url)
        except:
            print(f"{url} machine broke")
            continue
        time.sleep(5)

        html = driver.page_source
        ScrapingFramework.html_text_to_file(url,html,title,'Cleveland Clinic')

        print(f"Retrieved {url}")
    driver.close()