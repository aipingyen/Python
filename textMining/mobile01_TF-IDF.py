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
import sys
from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfVectorizer

# catch all content
def catch_allContent(comment):
    all_content = []
    all_content.append(comment['content'])
    for i in range(comment['reply_no']):
        all_content.append(comment['replies'][i]['content'])
    # print(all_content)
    return all_content

def tf_idf(jieba_Content):  #jieba_Content is list , element is 文章斷詞
    word_tfidf = []
    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform(jieba_Content)  #fit content
    words = vectorizer.get_feature_names()
    for i in range(len(jieba_Content)):
        print('----Document %d----' % (i))
        for j in range(len(words)):
            if tfidf[i, j] > 0.4:   #找出關鍵字
                print(words[j], tfidf[i, j])
                word_tfidf.append(words[j]+","+str(tfidf[i, j]))
    write(word_tfidf)

def jiebaContent(content):#傳入" list "
    jieba_Content = []
    print(content)
    if content != None:
        for text in content:
            jieba_Content.append(' '.join(jieba.cut(text)))
        print(jieba_Content)
        return jieba_Content
    else:
        return None

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

def write(word_tfidf):
    with open('C:\\Users\\BIG DATA\\Desktop\\Project\\{}.csv'.format("VW08"), 'a', encoding='utf8') as fw1:
        fw1.write('\n'.join(word_tfidf))

def multi(content):
    freeze_support()
    cpus = cpu_count()
    pool = Pool(cpus)
    pool.apply_async(jiebaContent, args=(content,), callback=tf_idf)
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

            printStr = 'now is going on ' + str(idx + 1) + ',which is ' + str(math.floor((idx + 1) / count * 100)) + str('% finished')
            sys.stdout.write('\r' + printStr)
            multi(content)
        end = time.time()
        elapsed = end - start
        print("Time taken :{} seconds.".format(elapsed))

    except Exception as e:
        print("{} error in row{} , :".format(main, idx + 1), e)

if __name__ == '__main__':

    jieba.load_userdict("C:\\jupyter\\textMining\\moedict.txt")
    jieba.load_userdict("C:\\Users\\BIG DATA\\Desktop\\Project\\textMiningDICT\\yahoo_content.txt")
    with open('C:\\Users\\BIG DATA\\Desktop\\Project\\textMiningDICT\\stopWords.txt', 'r', encoding='utf8') as fr:
        normal_words = fr.read().split('\n')

    carName = 'Volkswagen'
    # for year in range(2013, (2017)+1, 1):
    year = 2008
    month_from = datetime(year, 1, 1, 0, 0)
    month_end = datetime(year + 1, 1, 1, 0, 0)
    wc = Counter()
    # print(year)
    main(month_from, month_end, carName, year)

#Volkswagen  小葉
#Toyota    飛龍
#LEXUS
#Mazda
#Mitsubishi   今晚小葉
#Nissan

#BMW
#Mercedes Benz