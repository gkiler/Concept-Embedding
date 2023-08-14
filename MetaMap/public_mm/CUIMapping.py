import argparse
from skr_web_api import Submission, BATCH_VALIDATION_URL
import re
import json
import subprocess
from time import time
import pandas as pd
import os
from time import sleep
import pyarrow
from tqdm import tqdm

def unescape_string(textstring):
    """Remove leading backslashes from text string"""
    return textstring.replace('\\', '')

if __name__ == '__main__':
    string_list = []
    inputfile = input("Enter text file name of queries: ")
    with open(inputfile, encoding='utf-8') as f:
        for line in f:
            if line.isspace() is False:    
                string = line.strip()
                string = re.sub(r'/', ' ', string)
                string = re.sub(r':.*', '', string)
                string = re.sub(r'—.*', '', string)
                string = re.sub(r'\([^)]*\)', '', string)
                string = re.sub(r'[^,\-a-zA-Z0-9 ]', '', string)
                string_list.append(string)
            else:
                continue
    
    mappings = []
    commands = []
    # ["wsl", "~", "cd", "/mnt/c/Users/gwenk/OneDrive/Documents/Research/Scraping/MetaMap/public_mm",";", "echo", f"heart attack", "|", "./bin/metamap", "-AINps", "--conj", "-Q", "4", "-V", "USAbase"]
    for string in string_list:
        commands.append(["wsl", "~", "cd", "/mnt/c/Users/gwenk/OneDrive/Documents/Research/Scraping/MetaMap/public_mm",";", "echo", f"{string}", "|", "./bin/metamap", "-AINps", "--conj", "-Q", "4", "-V", "USAbase"])
    n  = 16

    #START SERVER BEFORE RUNNING
    outputs = []
    for j in tqdm(range(max(int(len(commands)/n), 1))):
        procs = [subprocess.Popen(i,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False) for i in commands[j*n: min((j+1)*n, len(commands))]]
        for p in procs:
            print(f"Dealing with {p.args[6]}")
            try:
                p.wait(30)
            except subprocess.TimeoutExpired:
                p.terminate()
            print("CUIs: "+", ".join(re.findall(r"C\d{7}",str(p.communicate()[0].decode("utf-8")))))
            # print(p.communicate())
        outputs.extend([(process.args[6],process.communicate()[0].decode("utf-8")) for process in procs])

    for string, output in outputs:
        cuis = ", ".join(re.findall(r"C\d{7}",str(output)))
        mappings.append((string,cuis))
    df = pd.DataFrame(mappings,columns=["string_id","cui"])
    print(df)
    df.to_parquet(f"{inputfile[:-4]}_CUI_Mappings.parquet",compression="gzip",engine='pyarrow')
    quit()
    for index, string in enumerate(string_list[:10]):
        # os.system("cd /mnt/c/Users/gwenk/OneDrive/Documents/Research/Scraping/MetaMap/public_mm")
        cp = subprocess.run(["wsl","~","cd","/mnt/c/Users/gwenk/OneDrive/Documents/Research/Scraping/MetaMap/public_mm",
                             ";","echo",f"{string}",
                             "|","./bin/metamap","-AINps --conj -Q 4 -V USAbase"],capture_output=True)
        output = cp.stdout
        cuis = ", ".join(re.findall(r"C\d{7}",str(output)))
        mappings.append((string,cuis))
    df = pd.DataFrame(mappings,columns=["string_id","cui"])
    print(df)