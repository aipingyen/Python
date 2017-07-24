from pymongo import MongoClient
import time
import sys
import math
import jieba
from collections import Counter
import jieba.analyse
from multiprocessing import Pool,cpu_count,freeze_support
from datetime import datetime
import jieba.posseg as pseg

# carName_list = ['BMW','LEXUS']
# carName_list = ['NISSAN','TOYOTA']
# carName_list = ['MITSUBISHI','HONDA']
# carName_list = ['FORD','BENZ']
# carName_list = ['VOLKSWAGEN','MAZDA']
#'BMW','LEXUS','NISSAN','TOYOTA','MITSUBISHI','HONDA','FORD','BENZ','VOLKSWAGEN','MAZDA'


# catch all content
def catch_allContent(comment):
    all_content = []
    all_content.append(comment['content'])
    for i in range(comment['reply_no']):
        all_content.append(comment['replies'][i]['content'])
    return all_content


def jiebaContent(content):  #傳入list 一個element是一篇文章(主文、回文)
    contents = ""
    for i in range(len(content)):
        contents += content[i]
    jiebaContent = jieba.analyse.extract_tags(contents, allowPOS=['nr', 'n', 'v', 'nz', 'ns', 'vn', 'a', 'an', 'x'])
    return jiebaContent   #return 一個list [我們指定的詞性字詞]


def wordCount(jiebaContent):#傳入" list "
    global wc
    for word_raw in jiebaContent:
        # print(word_raw)
        word = word_raw.replace('\r\n', '').replace('\n', '').upper()
        if word not in normal_words:
            if word in wc:
                wc[word] += 1
            else:
                wc[word] = 1
        # print(wc.most_common())

def multi(content):
    freeze_support()  # Windows 平台要加上這句，避免 RuntimeError
    cpus = cpu_count()-1  # 使用核心數-1，避免資源緊繃
    pool = Pool(cpus)
    pool.apply_async(jiebaContent, args=(content,), callback=wordCount) # 分別將任務分散到cpu中運算
    pool.close()
    pool.join()

# connect to mobile01.db
def main(month_from, month_end, carName, year):
    IP = 'localhost'  # '192.168.196.172'
    client = MongoClient(IP, 27017)
    # Select database
    db = client.final_project

    # Select collection
    collection = db.mobile01

    count = collection.find({"Board":carName, "tm": {"$gte": month_from, "$lt": month_end}}).count()
    print(count)
    comment = collection.find({"Board": carName, "tm": {"$gte": month_from, "$lt": month_end}})
    verb = {}
    adj = {}
    noun = {}
    try:
        for idx in range(count):
            content = catch_allContent(comment[idx])  #return allContent list
            multi(content)
            #jiebaContent(content)
            printStr = 'now is going on ' + str(idx + 1) + ',which is ' + str(math.floor((idx + 1) / count * 100)) + str('% finished')
            sys.stdout.write('\r' + printStr)

        with open('C:\\Users\\BIG DATA\\Desktop\\Project\\{}\\{}.csv'.format(carName, year), 'a', encoding='utf8') as fw1:
            for word, counts in wc.most_common():
                fw1.write('{},{}\n'.format(word, counts))
                word_pseg = pseg.cut(word)
                for w in word_pseg:
                    if w.flag == "vn" or w.flag == "v":
                        verb[w.word] = counts
                        # print(w.word+" "+ii[1])
                    elif w.flag == "an" or w.flag == "a":
                        adj[w.word] = counts
                        # print(w.word)
                    else:
                        noun[w.word] = counts
                        # print(w.word)
        with open(u'C:\\Users\\BIG DATA\\Desktop\\Project\\{}\\{}_verb.csv'.format(carName, year), 'a', encoding='utf8') as fw2:
            for word, counts in verb.items():
                fw2.write('{},{}\n'.format(word, counts))
        with open(u'C:\\Users\\BIG DATA\\Desktop\\Project\\{}\\{}_noun.csv'.format(carName, year), 'a', encoding='utf8') as fw3:
            for word, counts in noun.items():
                fw3.write('{},{}\n'.format(word, counts))
        with open(u'C:\\Users\\BIG DATA\\Desktop\\Project\\{}\\{}_adj.csv'.format(carName, year), 'a', encoding='utf8') as fw4:
            for word, counts in adj.items():
                fw4.write('{},{}\n'.format(word, counts))
    except Exception as e:
        print("{} error in row{} , :".format(main, idx + 1), e)

if __name__ == '__main__':

    jieba.load_userdict("C:\\jupyter\\textMining\\moedict.txt")
    jieba.load_userdict("C:\\Users\\BIG DATA\\Desktop\\Project\\textMiningDICT\\yahoo_contentDict.txt")
    with open('C:\\Users\\BIG DATA\\Desktop\\Project\\textMiningDICT\\stopWords.txt', 'r', encoding='utf8') as fr:
        normal_words = fr.read().split('\n')
    start = time.time()
    carName = 'Toyota'
    # for year in range(2008, (2017)+1, 1):
    year = 2008
    month_from = datetime(year, 1, 1, 0, 0)
    month_end = datetime(year + 1, 1, 1, 0, 0)
    wc = Counter()
    # print(year)
    main(month_from, month_end, carName, year)
    end = time.time()
    elapsed = end - start
    print("Time taken :{} seconds.".format(elapsed))

#Volkswagen  宜靜    all
#Toyota    飛龍      -2014   ing
#LEXUS    小葉      all
#Mazda                      ing
#Mitsubishi   今晚小葉   -2010  (cut off)
#Nissan

#BMW
#Mercedes Benz

#collection.find({"Board": carName, "tm": {"$gte": month_from, "$lt": month_end}},{"$text":{"$search":關鍵字}})