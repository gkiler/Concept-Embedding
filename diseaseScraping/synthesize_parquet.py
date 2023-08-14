import os
import pandas as pd
import numpy as np
from tqdm import tqdm
def get_parquet_files(directory):
    parquet_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".parquet"):
                parquet_files.append(os.path.join(root, file))
    return parquet_files

def concatenate_parquet_files(directory):
    parquet_files = get_parquet_files(directory)
    dataframes = []
    for file in tqdm(parquet_files):
        df = pd.read_parquet(file)
        dataframes.append(df)
        
    # chatgpt start
    num_dataframes = len(dataframes)
    chunk_size = num_dataframes // 4
    remainder = num_dataframes % 4

    # Split the list of dataframes into chunks
    chunks = [dataframes[i:i + chunk_size] for i in range(0, num_dataframes - remainder, chunk_size)]

    # If there's a remainder, distribute the remaining dataframes among the chunks
    if remainder:
        for i, dataframe in enumerate(dataframes[-remainder:], start=1):
            chunks[-i].append(dataframe)
    #chatgpt end

    print("Outputting dataframes...")
    for index, dflist in enumerate(chunks):
        concatdf = pd.concat(dflist,axis=0)
        concatdf.to_parquet(f"disease_data_{index}",index=False,compression="gzip")
        print("Dataframe completed...")
    print("Done!")
    # concatenated_df = pd.concat(dataframes,axis=0)
    # concatenated_df.columns = concatenated_df.columns.str.lower()
    # concatenated_df.to_parquet("DiseaseInfo.parquet", index=False,compression="gzip")

# Provide the directory path where the parquet files are located
directory_path = "Diseases"
concatenate_parquet_files(directory_path)
