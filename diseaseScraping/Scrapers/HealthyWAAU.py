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


SOURCE_NAME = 'Healthy Western Australians (gov)'
if __name__ == '__main__':
    base_url = 'https://www.healthywa.wa.gov.au/Health-conditions/Health-conditions-A-to-Z'
    base = 'https://www.healthywa.wa.gov.au'

    print("Getting indices")
    links = ScrapingFramework.links_from_containers(base_url,'div','az-result')
    
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
            url = base+link['href']
        
        path = sanitize_filename(title).strip()
        if f"{path}.json" in file_set:
            print(f"Skipping {path}")
            continue
        ScrapingFramework.html_link_to_file(url,link.text,SOURCE_NAME)