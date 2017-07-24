from pymongo import MongoClient
import time
import sys
import math
from multiprocessing import Pool, cpu_count, freeze_support
from datetime import datetime


def insert(year, carName, data):
    IP = 'localhost'  # '192.168.196.172'
    client = MongoClient(IP, 27017)
    # Select database
    db = client.final_project

    # Select collection
    collection = db.Radar

    radar = {"Board": carName, "year": year, 'data': data}
    collection.insert_one(radar)

def query(year, carName, adj_Dict, idx):
    IP = 'localhost'  # '192.168.196.172'
    client = MongoClient(IP, 27017)
    # Select database
    db = client.final_project

    # Select collection
    collection = db.mobile01_featureRank
    count = collection.find().count()
    # print(count)
    comment = collection.find({"Board": carName, "year": year, "feature": adj_Dict})
    try:

        level = comment[0]['level']
        printStr = 'now is going on ' + str(idx + 1) + ',which is ' + str(math.floor((idx + 1) / count * 100)) + str('% finished')
        sys.stdout.write('\r' + printStr)
        idx += 1
        return level

    except Exception as e:
        print("{} error in row{} , :".format('query', idx), e)

if __name__ == '__main__':
    adj_Dicts = ['comfortable', 'fuelEco', 'safe', 'space']
    carName_list = ['Volkswagen','Toyota','LEXUS','Mazda','Mitsubishi','Nissan','BMW','Benz','Honda','Ford']
    start = time.time()
    idx = 0
    for year in range(2008, (2017) + 1, 1):

        for carName in carName_list:
            data = [{'feature': 'preserve', 'level': None}]
            for adj_Dict in adj_Dicts:
                level = query(year, carName, adj_Dict, idx)
                row = {'feature': adj_Dict, 'level': level}
                # [{'feature': adj_Dict, 'level': level}, {'feature': adj_Dict, 'level': level}, {'feature': adj_Dict, 'level': level}]
                data.append(row)
            insert(year, carName, data)

    end = time.time()
    elapsed = end - start
    print("Time taken :{} seconds.".format(elapsed))