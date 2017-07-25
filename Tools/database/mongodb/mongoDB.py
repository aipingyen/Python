import json
import pprint
from pymongo import MongoClient


client = MongoClient('192.168.196.172', 27017)

# Select database
db = client.final_project

# Select collection
collection = db.mobile01


with open('car_list_wname.txt', 'r') as f:
    data_str = f.readlines()
    for idx, data in enumerate(data_str):
        data = data.strip()
        if len(data) != 0:
            final_data = json.loads(data)
            collection.insert_one(final_data)
        if idx % 400 == 0:
            print(idx)