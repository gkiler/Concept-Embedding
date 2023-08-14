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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

SOURCE_NAME = "Rare Diseases NIH"
BASE_URL = 'https://rarediseases.info.nih.gov/diseases'
HREF_BASE = 'https://rarediseases.info.nih.gov/'

firefox_options = Options()
firefox_options.add_argument("--headless")  # Run Firefox in headless mode
driver = webdriver.Firefox(options=firefox_options)
driver.install_addon('ublock_origin-1.49.2.xpi')

def click_button_get_links(button,link_type,link_label):
    driver.find_element(By.CSS_SELECTOR,button).click()
    time.sleep(3)

    links = []
    links.extend(ScrapingFramework.links_from_containers_html(driver.page_source,link_type,link_label))
    return links

if __name__ == '__main__':

    driver.get(BASE_URL)
    time.sleep(3)

    links = []
    
    for i in range(2,592):
        links.extend(ScrapingFramework.links_from_containers_html(driver.page_source,"div","result mb-5 cursor-pointer"))
        print(f"{len(links)} links...")

        # try:
        #     driver.find_element(By.CSS_SELECTOR,".pum-close.popmake-close").click()
        #     driver.find_element(By.CSS_SELECTOR,".pum-tc-box__checkbox.popmake-tcp-input.pum-enabled").click()
        # except:
        #     pass

        scroll_distance = 500  # Adjust the value as needed
        
        time.sleep(5)
        driver.find_element(By.XPATH,f"//a[@href='/diseases?search=&page={i}']").click()
        # break


    print(f"Retrieved (roughly) {len(links)} links")

    file_set = set()
    diseases_path = os.getcwd() + f"\\Diseases\\{SOURCE_NAME}"
    for root,dirs,files in os.walk(diseases_path):
        for file in files:
            file_set.add(file)

    for link in links:
        title = re.search(r"/([^/]+)$",link['href']).group(1)

        if "https://" in link['href']:
            url = link['href']
        else:
            url = HREF_BASE+link['href']
        
        path = sanitize_filename(title).strip()
        if f"{path}.json" in file_set:
            print(f"Skipping {path}")
            continue
        
        driver.get(url)
        time.sleep(5)

        html = driver.page_source
        
        ScrapingFramework.html_text_to_file(url,html,title,SOURCE_NAME)

        print(f"Retrieved {url}")
    driver.close()