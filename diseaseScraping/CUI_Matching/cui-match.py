#This script returns UMLS CUIs based on an input file of strings, where each line in txt file is a separate string.
#If no results are found for a specific string, this will be noted in output and output file.
#Each set of results for a string is separated in the output file with '***'.

import requests
import argparse
from time import sleep
import re

#adapted to pandas CSV output from UMLS example on website  
parser = argparse.ArgumentParser(description='process user given parameters')
parser.add_argument('-k', '--apikey', required = True, dest = 'apikey', help = 'enter api key from your UTS Profile')
parser.add_argument('-v', '--version', required =  False, dest='version', default = 'current', help = 'enter version example-2015AA')
parser.add_argument('-o', '--outputfile', required = True, dest = 'outputfile', help = 'enter a name for your output file')
parser.add_argument('-s', '--sabs', required = False, dest='sabs',help = 'enter a comma-separated list of vocabularies without spaces, like MSH,SNOMEDCT_US,RXNORM')
parser.add_argument('-t', '--ttys', required = False, dest='ttys',help = 'enter a comma-separated list of term types, like PT,SY,IN')
parser.add_argument('-i', '--inputfile', required = True, dest = 'inputfile', help = 'enter a name for your input file')
#py cui-match.py -k "9e7c133a-a55b-4eed-bdc6-944440431257" --ttys "BD,BN,BPCK,BR,CCN,CDA,CDC,CDD,CD,CHN,CSN,DC10,DC9,DI,DP,GN,GPCK,IN,MIN,MS,N1,PIN,PR,PQ,PTCS,SBDC,SBDF,SCDG,SCD,SD,SU," -o "matched_cuis.csv" -i ""
args = parser.parse_args()
apikey = args.apikey
version = args.version
outputfile = args.outputfile
inputfile = args.inputfile
sabs = args.sabs
ttys = args.ttys

base_uri = 'https://uts-ws.nlm.nih.gov'
string_list = []

with open(inputfile, encoding='utf-8') as f:
    for line in f:
        if line.isspace() is False:    
            strings = line.strip()
            string_list.append(strings)
        else:
            continue

# print(string_list)

with open(outputfile, 'w', encoding='utf-8') as o:
    o.write('cui{S}drug_name\n')
    for string in string_list:
        page = 0
        
        # o.write('SEARCH STRING: ' + string + '\n' + '\n')
        
        while True:
            old = string
            string = re.sub(r'/', ' ', string)
            string = re.sub(r':.*', '', string)
            string = re.sub(r'—.*', '', string)
            string = re.sub(r'\([^)]*\)', '', string)
            string = re.sub(r'[^,\-a-zA-Z0-9 ]', '', string)
            print(f"Searching for {old} under name {string}...")
            # sleep(0.5)
            page += 1
            path = '/search/'+version
            query = {'partialSearch':'false','string':string, 'apiKey':apikey, 'rootSource':sabs, 'termType':ttys, 'pageNumber':page}
            try:
                output = requests.get(base_uri+path, params=query)
            except:
                sleep(5)
                continue
            output.encoding = 'utf-8'
            # print(output.url)
        
            outputJson = output.json()
            results = (([outputJson['result']])[0])['results']
            # print(query)
            if len(results) == 0:
                query = {'partialSearch':'true','string':string, 'apiKey':apikey, 'rootSource':sabs, 'termType':ttys, 'pageNumber':page}
                try:
                    output = requests.get(base_uri+path, params=query)
                    
                    output.encoding = 'utf-8'
                    outputJson = output.json()
                    results = (([outputJson['result']])[0])['results']
                except:
                    sleep(5)
                    continue
                if output.status_code != 200:
                    sleep(5)
                    continue

                if len(results) == 0:
                    if page == 1:
                        print('No results found for ' + string +'\n')
                        o.write(' ' + '{S}' + string+'\n')
                        break
                    else:
                        break
            
            for item in results:
                print(f'\033[1m{string}\033[0m maps to \033[1m{item["ui"]}\033[0m\n')
                o.write(item['ui'] + '{S}'+string+'\n')
                # o.write('UI: ' + item['ui'] + '\n' + 'Name: ' + item['name'] + '\n'  + 'URI: ' + item['uri'] + '\n' + 'Source Vocabulary: ' + item['rootSource'] + '\n' + '\n')
                break
            break

        # o.write('***' + '\n' + '\n')