from pymongo import MongoClient
import time
import sys
import math
from multiprocessing import Pool, cpu_count, freeze_support
from datetime import datetime

def insert(title_id, year, carName, senAnalysis):
    IP = 'localhost'  # '192.168.196.172'
    client = MongoClient(IP, 27017)
    # Select database
    db = client.final_project

    # Select collection
    collection = db.mobile01_adjTags  #collection : 分析這篇文章+評論的內容是否有出現特徵字
    if len(senAnalysis) != 0:
        conAnalysis = {'reference': title_id, 'year': year, 'Board':carName, 'senAnalysis': senAnalysis}
        collection.insert_one(conAnalysis)

def wordcount(contents, title_id, carName, year):
    featureLabel = ['comfortable', 'fuelEco', 'safe', 'space']
    senAnalysis = []
    for i in range(len(contents)):
        str_comfortable = []
        str_fuelEco = []
        str_safe = []
        str_space = []
        for word in word_dict['comfortable']:
            if word in contents[i]:
                str_comfortable.append(word)
            else:
                None
        for word in word_dict['fuelEco']:
            if word in contents[i]:
                str_fuelEco.append(word)
            else:
                None
        for word in word_dict['safe']:
            if word in contents[i]:
                str_safe.append(word)
            else:
                None
        for word in word_dict['space']:
            if word in contents[i]:
                str_space.append(word)
            else:
                None
        count_list = [len(str_comfortable), len(str_fuelEco), len(str_safe), len(str_space)]
        str_list = [str_comfortable, str_fuelEco, str_safe, str_space]
        idx = count_list.index(max(count_list))
        if max(count_list) != 0:
            sentence = {'label': featureLabel[idx], 'emotion':None, 'content': contents[i], 'count': len(str_list[idx]),
                        'features': str_list[idx]}
            senAnalysis.append(sentence)
    insert(title_id, year, carName, senAnalysis)


def catch_allContent(comment):
    all_content = []
    all_content.append(comment['content'])
    for i in range(comment['reply_no']):
        all_content.append(comment['replies'][i]['content'])
    return all_content


def query(month_from, month_end, carName, year):
    IP = 'localhost'  # '192.168.196.172'
    client = MongoClient(IP, 27017)
    # Select database
    db = client.final_project

    # Select collection
    collection = db.mobile01

    count = collection.find({"Board": carName, "tm": {"$gte": month_from, "$lt": month_end}}).count()
    print(count)
    comment = collection.find({"Board": carName, "tm": {"$gte": month_from, "$lt": month_end}})
    start = time.time()
    try:
        for idx in range(count):
            contents = catch_allContent(comment[idx])  # return allContent list
            #             multi(content)
            wordcount(contents, comment[idx]['_id'], carName, year)

            printStr = 'now is going on ' + str(idx + 1) + ',which is ' + str(
                math.floor((idx + 1) / count * 100)) + str('% finished')
            sys.stdout.write('\r' + printStr)

        end = time.time()
        elapsed = end - start
        print("Time taken :{} seconds.".format(elapsed))

    except Exception as e:
        print("{} error in row{} , :".format('query', comment[idx]['_id']), e)


if __name__ == '__main__':

    path = 'C:\\Users\\BIG DATA\\Desktop\\Project\\textMiningDICT\\adjDict_W2C\\'
    word_dict = {}
    adj_Dicts = ['comfortable', 'fuelEco', 'safe', 'space']
    for adj_Dict in adj_Dicts:
        with open(path + adj_Dict + ".txt", "r", encoding='utf-8') as fr:
            data = fr.read().strip().split('\n')
            dict_list = [word for word in data if len(word) > 0]
            word_dict[adj_Dict] = dict_list

    # carName = 'LEXUS'
    carName_list = ['Volkswagen','Toyota','LEXUS','Mazda','Mitsubishi','Nissan','BMW','Mercedes Benz','Honda','Ford']
    for carName in carName_list:
        for year in range(2008, (2017)+1, 1):
        # year = 2008
            month_from = datetime(year, 1, 1, 0, 0)
            month_end = datetime(year + 1, 1, 1, 0, 0)
            # print(month_end)
            query(month_from, month_end, carName, year)

#Volkswagen,'Toyota','LEXUS','Mazda','Mitsubishi','Nissan','BMW','Mercedes Benz'