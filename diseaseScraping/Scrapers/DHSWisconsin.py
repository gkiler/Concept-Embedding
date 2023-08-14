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

SOURCE_NAME = 'Wisconsin Department of Health Services'
if __name__ == '__main__':
    base_url = 'https://www.dhs.wisconsin.gov/diseases/a-z.htm/a'
    base = 'https://www.dhs.wisconsin.gov'
    seen_links = {base_url}

    print("Getting indices")
    index_links = ScrapingFramework.links_from_container(base_url,'ul','c-az-nav__list')
    links = []
    print("Getting links")
    for link in index_links:
        seen_links.add(link['href'])
        url = base + link['href']
        link_list = ScrapingFramework.links_from_container(url,'ul','c-views-list c-az-views-list')
        
        for new_link in link_list:
            if new_link['href'] not in seen_links:
                seen_links.add(new_link['href'])
                links.append(new_link)
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
            url = base+link['href']
        
        path = sanitize_filename(title).strip()
        if f"{path}.json" in file_set:
            print(f"Skipping {path}")
            continue
        ScrapingFramework.html_link_to_file(url,link.text,SOURCE_NAME)
    driver.close()