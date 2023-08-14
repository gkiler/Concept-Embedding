
import time
import requests
import os
from bs4 import BeautifulSoup
import io
import json
from os.path import exists
from datetime import datetime
from pathvalidate import sanitize_filename #not native

SOURCE_NAME = "NIH"
if __name__ == "__main__":
    originDir = os.getcwd()
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0"
    }    
    base_url = 'https://www.niams.nih.gov'
    time.sleep(5)
    base_html = requests.get("https://www.niams.nih.gov/health-topics/all-diseases", headers=headers).text

    base_soup = BeautifulSoup(base_html, 'lxml')
    print('[NIH]Retrieved base indices...')
    
    osDir = originDir + "\\" + "Diseases\\" + "NIH"
    if not os.path.exists(osDir):
        os.makedirs(osDir)

    diseases = base_soup.find_all('div',class_='text-card clearfix')
    disease_links = [disease.find('a',href=True) for disease in diseases]

    file_set = set()
    diseases_path = os.getcwd() + f"\\Diseases\\{SOURCE_NAME}"
    for root,dirs,files in os.walk(diseases_path):
        for file in files:
            file_set.add(file)

    for link in disease_links:
        title = link.text

        if "http" in link['href']:
            url = link['href']
        else:
            url = base_url+link['href']
        
        path = sanitize_filename(title).strip()
        if f"{path}.json" in file_set:
            print(f"Skipping {path}")
            continue
        # try:
        print('[NIH]Retrieving ', link['href'], '...')
        url = base_url+link['href']
        time.sleep(5)
        html_disease = requests.get(url, headers=headers)
        try:
            diseaseSoup = BeautifulSoup(html_disease.text, 'lxml')
            title = link.text
        except:
            print('[NIH]Soup Error')
            continue

        # try:
        diseaseName = title
        fileName = sanitize_filename(diseaseName)
        jsonPath = osDir + "\\" + fileName + ".json"
            
        date = datetime.now()
        
        data = {
                "name": diseaseName,
                "raw_html": diseaseSoup.prettify(),
                "source_url": url,
                "date_time_scraped": date.strftime("%d/%m/%Y %H:%M:%S"),
                "source_name": "NIH"
            }
        
        with io.open(jsonPath, 'w+', encoding='utf-8') as file:
            json.dump(data, file, indent = 4)
        # except:
        #     print('[NIH]Write error')