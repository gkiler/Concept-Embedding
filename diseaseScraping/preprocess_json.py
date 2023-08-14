import pyarrow
import os
import pandas as pd
import json
from bs4 import BeautifulSoup
from multiprocessing import Pool
from tqdm import tqdm

def remove_html_tags(text):
    soup = BeautifulSoup(text, "html.parser")
    stripped_text = soup.get_text(separator=" ")
    return stripped_text

def process_json_file(file_path):
    with open(file_path, 'r') as file:
        json_data = json.load(file)

    if "name" in json_data:
        json_data["name"] = json_data["name"].strip()

    return json_data

def get_folders(directory):
    folder_list = []

    # Iterate through all items in the directory
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        # Check if the item is a directory
        if os.path.isdir(item_path):
            folder_list.append(item_path)

    return folder_list

def json_files_to_dataframe(directory):
    file_paths = []

    # Collect all file paths in the directory
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.json'):
                file_path = os.path.join(root, filename)
                file_paths.append(file_path)
    import numpy as np
    # Parallelize the processing of JSON files
    results = []
    with Pool() as pool:
        
        
            # Use tqdm to create a progress bar
        with tqdm(total=len(file_paths)) as pbar:
            for result in pool.imap_unordered(process_json_file, file_paths):
                results.append(result)
                pbar.update(1)

    columns = set()
    data = []

    # Collect the processed JSON data
    for result in results:
        data.append(result)
        columns.update(result.keys())

    # Create an empty DataFrame with the collected column names
    df = pd.DataFrame(data,columns=list(columns))

    return df

if __name__ == '__main__':
    # Provide the directory path containing the JSON files
    directory_path = os.getcwd() + "\\Diseases"

    folders = get_folders(directory_path)

    # df = json_files_to_dataframe(directory_path)
    # df.to_parquet("Diseases\\diseaseInfo_v2_1.parquet")
    for folder in folders:
        print(f"{folder} to json...")
        json_files_to_dataframe(folder).to_parquet(f"{folder}.parquet")
