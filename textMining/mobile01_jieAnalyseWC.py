from pymongo import MongoClient
import time
import sys
import math
import jieba
from collections import Counter
import jieba.analyse
from multiprocessing import Pool,cpu_count,freeze_support
from datetime import datetime
# carName_list = ['BMW','LEXUS']
# carName_list = ['NISSAN','TOYOTA']
# carName_list = ['MITSUBISHI','HONDA']
# carName_list = ['FORD','BENZ']
# carName_list = ['VOLKSWAGEN','MAZDA']
#'BMW','LEXUS','NISSAN','TOYOTA','MITSUBISHI','HONDA','FORD','BENZ','VOLKSWAGEN','MAZDA'
wc = Counter()

# catch all content
def catch_allContent(comment):
    all_content = []
    all_content.append(comment['content'])
    for i in range(comment['reply_no']):
        all_content.append(comment['replies'][i]['content'])
    return all_content


def jiebaContent(content):#傳入" list "

    contents = ''
    print(len(content))
    for i in range(len(content)):
        contents += content[i]
    jiebaContent = jieba.analyse.extract_tags(contents, allowPOS=['nr', 'n', 'v', 'nz', 'ns', 'vn', 'a', 'an', 'x'])
    # print(jiebaContent)
    return jiebaContent


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
    freeze_support()
    pool = Pool(8)
    # cpus = cpu_count()
    # for i in range(0, 8):
    pool.apply_async(jiebaContent, args=(content,), callback=wordCount)
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
    start = time.time()

    try:
        for idx in range(count):
            content = catch_allContent(comment[idx])  #return allContent list
            multi(content)
            printStr = 'now is going on ' + str(idx + 1) + ',which is ' + str(math.floor((idx + 1) / count * 100)) + str('% finished')
            sys.stdout.write('\r' + printStr)

        with open('./count/{}{}.csv'.format(carName, year), 'a', encoding='utf8') as fw:
            for lang, counts in wc.most_common():
                fw.write('{},{}\n'.format(lang, counts))
        end = time.time()
        elapsed = end - start
        print("Time taken :{} seconds.".format(elapsed))

    except Exception as e:
        print("{} error in row{} , :".format(main, idx + 1), e)

if __name__ == '__main__':

    jieba.load_userdict("C:\\jupyter\\textMining\\moedict.txt")
    jieba.load_userdict("C:\\Users\\BIG DATA\\Desktop\\Project\\textMining\\yahoo_content.txt")
    with open('C:\\jupyter\\textMining\\moedict.txt', 'r', encoding='utf8') as frN:
        normal_words = frN.read().split('\n')   #stop-words

    carName = 'Volkswagen'
    year = 2010
    month_from = datetime(year, 1, 1, 0, 0)
    month_end = datetime(year + 1, 1, 1, 0, 0)
    # wc = Counter()
    main(month_from, month_end, carName, year)
