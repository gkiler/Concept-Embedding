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

SOURCE_NAME = "RareDiseases.org"
BASE_URL = 'https://rarediseases.org/rare-diseases'
BASE_URL_2 = "https://rarediseases.org/gard-rare-disease"
HREF_BASE = 'https://rarediseases.org'

firefox_options = Options()
# firefox_options.add_argument("--headless")  # Run Firefox in headless mode
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
    print("Getting Rare Diseases...")
    while (True):
        links.extend(ScrapingFramework.links_from_containers_html(driver.page_source,"h5","article-headline color-br-blue"))
        print(f"{len(links)} links...")
        # break
        try:
            driver.find_element(By.CSS_SELECTOR,".pum-close.popmake-close").click()
            driver.find_element(By.CSS_SELECTOR,".pum-tc-box__checkbox.popmake-tcp-input.pum-enabled").click()
        except:
            pass

        scroll_distance = 200  # Adjust the value as needed
        
        time.sleep(2)
        for i in range(20):
            try:
                driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
                time.sleep(.5)
                driver.find_element(By.CSS_SELECTOR, ".next").click()
                time.sleep(.5)
                break
            except:
                continue
        if i > 15:
            break
        time.sleep(2)

    print(f"{len(links)} rare diseases retrieved")
    driver.get(BASE_URL_2)
    time.sleep(3)
    print("Getting GARD Rare Diseases...")
    while (True):
        time.sleep(1)
        links.extend(ScrapingFramework.links_from_containers_html(driver.page_source,"h5","article-headline color-br-blue"))
        print(f"{len(links)} links...")
        # break
        try:
            driver.find_element(By.CSS_SELECTOR,".pum-close.popmake-close").click()
            driver.find_element(By.CSS_SELECTOR,".pum-tc-box__checkbox.popmake-tcp-input.pum-enabled").click()
        except:
            pass

        scroll_distance = 200  # Adjust the value as needed
        
        time.sleep(2)
        for i in range(20):
            try:
                driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
                time.sleep(.5)
                driver.find_element(By.CSS_SELECTOR, ".next").click()
                time.sleep(.5)
                break
            except:
                continue
        if i > 15:
            break
        time.sleep(2)

    print(f"Retrieved (roughly) {len(links)} links")

    file_set = set()
    diseases_path = os.getcwd() + f"\\Diseases\\{SOURCE_NAME}"
    for root,dirs,files in os.walk(diseases_path):
        for file in files:
            file_set.add(file)

    for link in links:
        if "https://" in link['href']:
            url = link['href']
        else:
            url = HREF_BASE+link['href']
        title = link.text
        path = sanitize_filename(title).strip()
        if f"{path}.json" in file_set:
            print(f"Skipping {path}")
            continue

        print(f"Retrieving {url}")
        try:
            driver.get(url)
        except:
            time.sleep(30)
        time.sleep(5)
        
        try:
            driver.find_element(By.CLASS_NAME,"pum-close.popmake-close").click()
        except:
            pass

        for i in range(20):
            try:
                driver.execute_script(f"window.scrollBy(0, {250});")
                time.sleep(.5)
                driver.find_element(By.CLASS_NAME,"button.full-report").click()
                time.sleep(.5)
                break
            except:
                continue
        
        for i in range(4):
            try:
                html = driver.find_element(By.CLASS_NAME,"col-lg-9.col-12").text
            except:
                time.sleep(2)
        if html is None:
            html = driver.page_source
        title = link.text
        ScrapingFramework.html_text_to_file(url,html,title,SOURCE_NAME)

        print(f"Retrieved {url}")
    driver.close()