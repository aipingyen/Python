from pymongo import MongoClient
import time
import sys
import math
import jieba
from collections import Counter
import jieba.analyse
from multiprocessing import Pool, cpu_count, freeze_support
from datetime import datetime
import jieba.posseg as pseg


def analysis(words):
    wc = Counter()
    for word in words:
        if word in wc:
            wc[word] += 1
        else:
            wc[word] = 1
    return wc.most_common()


def query(carName, year):
    IP = 'localhost'  # '192.168.196.172'
    client = MongoClient(IP, 27017)
    # Select database
    db = client.final_project

    # Select collection
    collection = db.mobile01_adjTags

    count = collection.find({"Board": carName, "year": year}).count()
    print(count)
    comment = collection.find({"Board": carName, "year": year})
    start = time.time()
    words = []
    total_count = 0
    try:
        for idx in range(count):
            for i in range(len(comment[idx]['senAnalysis'])):
                emotion = (comment[idx]['senAnalysis'][i]['emotion'])  # return allContent list
                tags = comment[idx]['senAnalysis'][i]['label']
                if emotion != "negative":
                    words.append(tags)
                else:
                    pass

                printStr = 'now is going on ' + str(idx + 1) + ',which is ' + str(
                    math.floor((idx + 1) / count * 100)) + str('% finished')
                sys.stdout.write('\r' + printStr)
        WC = analysis(words)
        for word, count in WC:
            total_count += count
        with open('C:\\Users\\BIG DATA\\Desktop\\Project\\radar\\{}\\{}.csv'.format(carName, year), 'a', encoding='utf8') as fw:
            for word, counts in WC:
                w = round((int(counts) / total_count) * 100, 2)
                fw.write('{},{},{},{}\n'.format(carName, word, counts, w))
#計算這些標籤出現的次數 , 我們用年份及車場品牌作為依據去計算這些標籤權重
        end = time.time()
        elapsed = end - start
        print("Time taken :{} seconds.".format(elapsed))

    except Exception as e:
        print("{} error in row{} , :".format('query', comment[idx]['_id']), e)


if __name__ == '__main__':
    emotionDict = ['negativeDict', 'positiveDict']
    adj_Dicts = ['comfortable', 'fuelEco', 'safe', 'space']

    carName_list = ['Volkswagen', 'Toyota', 'LEXUS', 'Mazda', 'Mitsubishi', 'Nissan', 'BMW', 'Mercedes Benz', 'Honda',
                    'Ford']
    for carName in carName_list:
        for year in range(2008, (2017) + 1, 1):
        # year_from = 2008
        # year_end = 2017+1
            query(carName, year)

# fuelEco of 2017 BMW is None
# space of 2013 Ford is None
