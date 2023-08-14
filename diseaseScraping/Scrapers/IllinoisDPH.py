
import time
import requests
import os
from bs4 import BeautifulSoup
import io
import json
from os.path import exists
from datetime import datetime
from pathvalidate import sanitize_filename #not native

SOURCE_NAME = "Illinois DPH"
if __name__ == "__main__":
    originDir = os.getcwd()
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0"
    }    
    base_url = 'https://dph.illinois.gov/'
    time.sleep(5)
    base_html = requests.get("https://dph.illinois.gov/topics-services/diseases-and-conditions/diseases-a-z-list.html", headers=headers).text

    base_soup = BeautifulSoup(base_html, 'lxml')
    print('[Illinois DPH]Retrieved base indices...')
    
    osDir = originDir + "\\" + "Diseases\\" + "IDPH"
    if not os.path.exists(osDir):
        os.makedirs(osDir)

    seen_link_set = {"https://dph.illinois.gov/topics-services/diseases-and-conditions/diseases-a-z-list.html"}
    cols = base_soup.find_all('div',class_="cmp-text")
    link_list = [x.find_all('a',href=True) for x in cols]
    
    disease_links = []
    for item_list in link_list:
        for link in item_list:
            disease_links.append(link)
    
    file_set = set()
    diseases_path = os.getcwd() + f"\\Diseases\\{SOURCE_NAME}"
    for root,dirs,files in os.walk(diseases_path):
        for file in files:
            file_set.add(file)
    
    for disease_link in disease_links:
        title = disease_link.text
        
        path = sanitize_filename(title).strip()
        if f"{path}.json" in file_set:
            print(f"Skipping {path}")
            continue


        if disease_link['href'] in seen_link_set:
            continue

        seen_link_set.add(str(disease_link["href"]))
        # try:
        print('[Illinois DPH]Retrieving ', disease_link['href'], '...')
        url = base_url+disease_link['href']
        time.sleep(5)
        html_disease = requests.get(url, headers=headers)
        try:
            diseaseSoup = BeautifulSoup(html_disease.text, 'lxml')
            title = disease_link.text
        except:
            print('[Illinois DPH]Soup Error')
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
                "source_name": "Illinois DPH"
            }
        
        with io.open(jsonPath, 'w+', encoding='utf-8') as file:
            json.dump(data, file, indent = 4)
        # except:
        #     print('[NIH]Write error')