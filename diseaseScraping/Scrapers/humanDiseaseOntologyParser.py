import json
import pandas as pd
import pyarrow

# Specify the path to your JSON file
file_path = 'HumanDO.json'
def print_json_structure(data, indent=0):
    for key, value in data.items():
        print(' ' * indent + str(key))
        if isinstance(value, dict):
            print_json_structure(value, indent + 2)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    print_json_structure(item, indent + 2)


diseases = [("DISEASE_NAME","CUI","DEFINITION","SOURCE_URL","RELATIONSHIPS")]
# Potentially convert edges to sentences?
with open(file_path, 'r') as json_file:
    data = json.load(json_file)

    disease_name_dict = {}
    for node in data["graphs"][0]['nodes']:
        # try:
        try:
            test = node['lbl']
        except:
            continue
        disease_name_dict[ node['id'] ] = (node['lbl']) #translate label to website ID for edges
        # except:
        #     pass

    edges = {}
    for edge in data["graphs"][0]["edges"]: 
        if edge['sub'] not in edges:
            edges[ edge['sub'] ] = []
        edges[ edge['sub'] ].append(edge['pred'] + " " + disease_name_dict[edge['obj']])

    for node in data['graphs'][0]['nodes']:
        try:
            if node["type"] != "CLASS":
                continue
        except:
            continue
        if "obsolete" in node['lbl']: #ignore obsolete entries
            continue
        disease_name = node['lbl']
        source_url = node['id']
        try:
            definition = node["meta"]["definition"]["val"]
        except:
            definition = None
        cui = None
        try:
            for xref in node["meta"]["xrefs"]:
                if 'UMLS_CUI' in xref['val']:
                    cui = xref['val'][-8:]
        except:
            pass

        relationships = []
        if node['id'] in edges:
            for obj in edges[ node['id'] ]:
                relationships.append(
                    f"{disease_name} {obj}"
                )
        
        diseases.append((disease_name,cui,definition,source_url,relationships))

df = pd.DataFrame(diseases[1:],columns=diseases[0])
df.to_parquet('Diseases/HumanDiseaseOntology.parquet',compression='snappy',engine='pyarrow')