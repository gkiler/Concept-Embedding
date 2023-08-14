
import time
import requests
import os
from bs4 import BeautifulSoup
import io
import json
from os.path import exists
from datetime import datetime
from pathvalidate import sanitize_filename #not native

SOURCE_NAME = "NHSScot"
if __name__ == "__main__":
    originDir = os.getcwd()
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0"
    }    
    base_url = 'https://www.nhsinform.scot/'
    time.sleep(5)
    base_html = requests.get("https://www.nhsinform.scot/illnesses-and-conditions/a-to-z#A", headers=headers).text

    base_soup = BeautifulSoup(base_html, 'lxml')
    print('[NHS]Retrieved base indices...')
    
    osDir = originDir + "\\" + "Diseases\\" + "NHSScot"
    if not os.path.exists(osDir):
        os.makedirs(osDir)

    seen_link_set = {"https://www.nhsinform.scot/illnesses-and-conditions/a-to-z#A"}
    rows = base_soup.find_all('ul',class_='nhsuk-list nhsuk-list--border')
    disease_links_list = [row.find_all('a',href=True) for row in rows]
    disease_links = []
    for link_list in disease_links_list:
        for link in link_list:
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
        print('[NHS]Retrieving ', disease_link['href'], '...')
        url = base_url+disease_link['href']
        time.sleep(5)
        try:
            html_disease = requests.get(url, headers=headers)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        
        
        try:
            diseaseSoup = BeautifulSoup(html_disease.text, 'lxml')
            title = disease_link.text
        except:
            print('[NHSScot]Soup Error')
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
                "source_name": "NHSScot"
            }
        
        with io.open(jsonPath, 'w+', encoding='utf-8') as file:
            json.dump(data, file, indent = 4)
        # except:
        #     print('[NIH]Write error')