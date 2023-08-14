import time
import requests
import os
import pyarrow
from os.path import exists
from pathvalidate import sanitize_filename #not native
import time
from multiprocessing import Pool

import pickle
import sys
import numpy as np
from tqdm import tqdm
import wikipedia
from mediawiki import MediaWiki
original_dir = os.getcwd()
sys.path.append('../')
from umlsparser import UMLSParser


import logging
from selenium.webdriver.remote.remote_connection import LOGGER
import pandas as pd
# Set the logging level to WARNING for the Selenium logger
LOGGER.setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("wikipediaapi").setLevel(logging.WARNING)

# Function to perform the search
def perform_search(search_tuple):
    cui = search_tuple[0]
    search_query = search_tuple[1]
    # Set up Selenium WebDriver
    
wiki = MediaWiki()
def perform_searches(cui_list):
    num_processors = 16
    wikipedia.set_rate_limiting(rate_limit=True,min_wait=20)

    # # Split cui_list into N chunks
    # chunk_size = len(cui_list) // num_processors
    # chunks = [cui_list[i:i+chunk_size] for i in range(0, len(cui_list), chunk_size)]

    with Pool(num_processors) as pool:
        results = list(tqdm(pool.imap(scrape_wikipedia_search, cui_list),total=len(cui_list)))
    results = [x for x in results if x is not None]
    return pd.DataFrame(results,index=None,columns=["cui","query","summary","fulltext"]) #,columns=["cui","query","summary","fulltext","source_url"]

def scrape_wikipedia_search(cui_list):
    
    # wiki = wikipediaapi.Wikipedia("UMLS Scraping",'en')
    cui = cui_list[0]
    query = cui_list[1]
    
    try:
        page = wiki.page(query)

        fulltext = page.content
        summary = page.summary
        # try:
        #     page = wiki.page(query)
        #     if not page.exists():
        #         return None
            # summary = page.summary
            # url = page.fullurl
            # fulltext = page.text
        # except:
        #     return None
        return (cui,query,summary,fulltext)
    except:
            return None
    
def split_list(lst, n):
    chunk_size = len(lst) // n
    remainder = len(lst) % n
    chunks = []

    index = 0
    for i in range(n):
        chunk = lst[index:index + chunk_size]
        if remainder > 0:
            chunk.append(lst[-remainder])
            remainder -= 1
        chunks.append(chunk)
        index += chunk_size

    return chunks

if __name__ == "__main__":
    # print(perform_search("Machine Learning"))
    
    cui_list_file = "cui_list.pkl"

    if os.path.exists(cui_list_file):
        # Load cui_list from file
        with open(cui_list_file, "rb") as file:
            cui_list = pickle.load(file)
    else:
        # Generate cui_list
        umlsdir = "C:\\Users\\gwenk\\OneDrive\\Documents\\Research\\Scraping\\2022AB"
        umls = UMLSParser(umlsdir)
        os.chdir(original_dir)
        CUIDict = umls.get_concepts().items()
        cui_list = []
        for cui, concept in CUIDict:
            try:
                name = concept.get_preferred_names_for_language("ENG")[0]
                cui_list.append((cui,name))
            except:
                continue

        # Save cui_list to file
        with open(cui_list_file, "wb") as file:
            pickle.dump(cui_list, file)

    cui_lists = split_list(cui_list,5)
    del cui_list
    for index, cui_list in enumerate(cui_lists):
        if index <= 2:
            continue
        df = perform_searches(cui_list)
        print(df)
        
        df.to_parquet(f"Wikipedia_pt{index}.parquet",engine='pyarrow',compression="gzip")
