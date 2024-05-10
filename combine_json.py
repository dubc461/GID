import glob
import json


def read_json(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data


datapath = ''
json_list = [file_name for file_name in glob.glob(f"{datapath}/*.json")]

data_list = [
    item['b']
    for single_json in json_list
    for item in json.load(open(single_json))
    if 'b' in item
]
data_list.sort()

with open('GisAid_id.json', 'w') as file:
    file.write(json.dumps(list(set(data_list))))
