
import time
import requests
import os
from bs4 import BeautifulSoup
import io
import json
from os.path import exists
from datetime import datetime
from pathvalidate import sanitize_filename #not native

def links_from_container(base_html_link, container_type,container_class_name):
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0"
    }   
    print(f"Retrieving {base_html_link}...")
    time.sleep(5)
    base_soup = BeautifulSoup(requests.get(base_html_link,headers=headers).text,'lxml')
    print(f"Retrieved {base_html_link}")
    container_links = base_soup.find(container_type,class_=container_class_name)
    container_links = container_links.find_all('a',href=True)

    return container_links


def links_from_containers(base_html_link, container_type,container_class_name):
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0"
    }   
    print(f"Retrieving {base_html_link}...")
    time.sleep(5)
    base_soup = BeautifulSoup(requests.get(base_html_link,headers=headers).text,'lxml')
    print(f"Retrieved {base_html_link}")
    container_bits = base_soup.find_all(container_type,class_=container_class_name)
    # print(base_soup.prettify())
    container_links = []
    for bit in container_bits:
        temp = bit.find_all('a',href=True)
        for link in temp:
            container_links.append(link)

    return container_links

def links_from_containers_html(html, container_type,container_class_name):
    base_soup = BeautifulSoup(html,'lxml')
    container_bits = base_soup.find_all(container_type,class_=container_class_name)
    # print(base_soup.prettify())
    container_links = []
    for bit in container_bits:
        temp = bit.find_all('a',href=True)
        for link in temp:
            container_links.append(link)

    return container_links

def links_from_selfs_html(html, container_type,container_class_name):
    base_soup = BeautifulSoup(html,'lxml')
    container_links = base_soup.find_all(container_type,class_=container_class_name)

    return container_links

def html_link_to_file(html_link,title,source):
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0"
    }   
    time.sleep(5)
    print(f"Retrieving {html_link}")
    soup = BeautifulSoup(requests.get(html_link, headers=headers).text,'lxml')
    print(f"Retrieved {html_link}")

    fileName = sanitize_filename(title).strip()
    try:
        os.mkdir(f"Diseases")
    except:
        pass
    try:
        os.mkdir(f"Diseases\\{source}")
    except:
        pass
    jsonPath = os.getcwd() + "\\Diseases\\" + source + "\\" + fileName + ".json"
        
    date = datetime.now()
    
    data = {
            "name": title,
            "raw_html": soup.prettify(),
            "source_url": html_link,
            "date_time_scraped": date.strftime("%d/%m/%Y %H:%M:%S"),
            "source_name": source
        }
    
    with io.open(jsonPath, 'w+', encoding='utf-8') as file:
        json.dump(data, file, indent = 4)

    return True

def html_text_to_file(url,html,title,source):

    fileName = sanitize_filename(title).strip()
    try:
        os.mkdir(f"Diseases")
    except:
        pass
    try:
        os.mkdir(f"Diseases\\{source}")
    except:
        pass
    
    jsonPath = os.getcwd() + "\\Diseases\\" + source + "\\" + fileName + ".json"
        
    date = datetime.now()
    
    data = {
            "name": title,
            "raw_html": html,
            "source_url": url,
            "date_time_scraped": date.strftime("%d/%m/%Y %H:%M:%S"),
            "source_name": source
        }
    
    with io.open(jsonPath, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent = 4)

    return True