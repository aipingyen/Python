from pymongo import MongoClient
import time
import sys
import math
from collections import Counter
from multiprocessing import Pool, cpu_count, freeze_support

def insert(carName, year, WC):
    IP = 'localhost'
    client = MongoClient(IP, 27017)
    db = client.final_project
    collection = db.WordCloud
    data = []
    for word, counts in WC:
        WC_obj = {'name': word, 'value': counts}
        data.append(WC_obj)
    radar = {"Board": carName, "year": year, 'data': data}
    collection.insert_one(radar)

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

    words = []
    try:
        for idx in range(count):
            for i in range(len(comment[idx]['senAnalysis'])):
                emotion = (comment[idx]['senAnalysis'][i]['emotion'])  # return allContent list
                for feature in comment[idx]['senAnalysis'][i]['features']:
                    if emotion == "negative":
                        words.append('不' + feature)
                    else:
                        words.append(feature)

                printStr = 'now is going on ' + str(idx + 1) + ',which is ' + str(math.floor((idx + 1) / count * 100)) + str('% finished')
                sys.stdout.write('\r' + printStr)
        WC = analysis(words)
        # with open('C:\\Users\\BIG DATA\\Desktop\\Project\\WordCloud\\{}\\{}.csv'.format(carName, year), 'a', encoding='utf8') as fw:
        #     for word, counts in WC:
        #         fw.write('{},{}\n'.format(word, counts))
        insert(carName, year, WC)

    except Exception as e:
        print("{} error in row{} , :".format('query', comment[idx]['_id']), e)


if __name__ == '__main__':
    emotionDict = ['negativeDict', 'positiveDict']
    adj_Dicts = ['comfortable', 'fuelEco', 'safe', 'space']
    carName_list = ['Volkswagen', 'Toyota', 'LEXUS', 'Mazda', 'Mitsubishi', 'Nissan', 'BMW', 'Mercedes Benz', 'Honda', 'Ford']
    start = time.time()
    for carName in carName_list:
        for year in range(2008, (2017) + 1, 1):
        # year = 2008
            query(carName, year)
    end = time.time()
    elapsed = end - start
    print("Time taken :{} seconds.".format(elapsed))