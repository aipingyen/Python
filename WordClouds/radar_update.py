from pymongo import MongoClient
import time
import sys
import math
from multiprocessing import Pool, cpu_count, freeze_support
from datetime import datetime


def update(year,carName,level):
    IP = 'localhost'  # '192.168.196.172'
    client = MongoClient(IP, 27017)
    # Select database
    db = client.final_project

    # Select collection
    collection = db.Radar

    radar = {"Brand": carName, "year": year}
    print(radar)
    collection.find_one_and_update(radar, {'$set': {'radar.0.level': level}})

def input():
    with open("C:\\Users\\BIG DATA\\Desktop\\yearbrandValues(priceSend)0721.txt", "r", encoding='utf-8') as fr:
        data = fr.read().strip().split('\n')
    print(data)
    for idx in data:
        row = idx.replace('(','').replace(')','').replace('\t','').split(',')
        print(row[0],row[1],row[2])
        update(int(row[0]),row[1],int(row[2]))

if __name__ == '__main__':
    start = time.time()
    input()
    end = time.time()
    elapsed = end - start
    print("Time taken :{} seconds.".format(elapsed))
