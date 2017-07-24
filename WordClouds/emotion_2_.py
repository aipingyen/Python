from pymongo import MongoClient
import time
import sys
import math
import jieba
import jieba.analyse
from multiprocessing import Pool, cpu_count, freeze_support
def analysis(sentence):

    jieba_text = jieba.cut(sentence, cut_all=False)
    negativeDict_len = []
    positiveDict_len = []
    words = ','.join(jieba_text).split(',')
    for word in words:
        if word in positiveDict:
            positiveDict_len.append(word)
        elif word in negativeDict:
            negativeDict_len.append(word)
    # print("negativeDict_list : ", negativeDict_len)
    # print("positiveDict_list : ", positiveDict_len)
    if len(negativeDict_len) > len(positiveDict_len):
        return ("negative")
    else:
        return ("positive")


def query():
    IP = 'localhost'  # '192.168.196.172'
    client = MongoClient(IP, 27017)
    # Select database
    db = client.final_project
    # Select collection
    collection = db.mobile01_adjTags

    count = collection.find().count()
    print(count)
    comment = collection.find()
    start = time.time()
    adjDict = {}
    try:
        for idx in range(count):
            for i in range(len(comment[idx]['senAnalysis'])):
                content = comment[idx]['senAnalysis'][i]['content']
                # print("content : ",content)
                emotion = analysis(content)
                # print(emotion)
                senAnalysis_var = 'senAnalysis.'+str(i)+'.emotion'
                collection.find_one_and_update({'_id':comment[idx]['_id']},{'$set':{senAnalysis_var: emotion}})  #JsonArray
                # print("update OK")
            printStr = 'now is going on ' + str(idx + 1) + ',which is ' + str(math.floor((idx + 1) / count * 100)) + str('% finished')
            sys.stdout.write('\r' + printStr)

        end = time.time()
        elapsed = end - start
        print("Time taken :{} seconds.".format(elapsed))

    except Exception as e:
        print("{} error in row{} , :".format(query, idx + 1), e)


if __name__ == '__main__':
    emotionDict = ['negativeDict', 'positiveDict']
    negativeDict = []
    positiveDict = []
    path = 'C:\\Users\\BIG DATA\\Desktop\\Project\\textMiningDICT\\sentiment\\'
    for emotion in emotionDict:
        jieba.load_userdict(path + emotion + ".txt")
    with open(path + 'negativeDict' + ".txt", 'r', encoding='utf8') as frW:
        negativeDict += frW.read().split('\n')
    with open(path + 'positiveDict' + ".txt", 'r', encoding='utf8') as frW:
        positiveDict += frW.read().split('\n')

    adj_Dicts = ['comfortable', 'fuelEco', 'safe', 'space']
    query()
