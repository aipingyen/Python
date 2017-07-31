import sqlite3
import time
import sys
import math
import jieba
from collections import Counter
from multiprocessing import Pool,cpu_count,freeze_support
import jieba.analyse

wc = Counter()

def jiebaContent(content):
    if content != None:
        # print("content : ",content)   #傳入" list "
        # jieba.load_userdict("C:\\jupyter\\textMining\\moedict.txt")
        contents = ''
        for idx in range(len(content)):
            contents += content[idx]
        jiebaContent = jieba.analyse.extract_tags(contents, allowPOS=['nr', 'n', 'v', 'nz', 'ns', 'vn', 'a', 'an'])
        # print("jiebaContent ; ",jiebaContent)
        # wordCount(jiebaContent)
        judgeLexical(jiebaContent)
        # return jiebaContent
    else:
        return None

def judgeLexical(jiebaContent):
    import jieba.posseg as pseg
    for word in jiebaContent:
        word_pseg = pseg.cut(word)
        for w in word_pseg:
            print(w.flag,w.word)

def wordCount(jiebaContent):
    global wc
#     wc = Counter()
    for word_raw in jiebaContent:
        word = word_raw.replace('\r\n', '').replace('\n', '').upper()
        if word not in normal_words:    # and sign_words
            if word in wc:
                wc[word] += 1
            else:
                wc[word] = 1
    # return wc.most_common()

def multi(content):
    freeze_support()
    pool = Pool(7)
    # cpus = cpu_count()
    # for i in range(0, 8):
    pool.apply_async(jiebaContent, args=(content, ), callback = wordCount)
    pool.close()
    pool.join()

# connect to mobile01.db
def main():
    conn = sqlite3.connect("C:\\Users\\BIG DATA\\Desktop\\car_price_db\\yahoo_new_car.sqlite3")
    cur = conn.cursor()
    count = cur.execute("select count(distinct(intro)) from yahooNewCars_filtered;").fetchone()[0]
    print(count)
    sql = "select distinct(intro) from yahooNewCars_filtered ;"
    cur.execute(sql)
    import jieba.posseg as pseg
    try:
        for idx, row in enumerate(cur):
            sentence = [ line for line in row[0].split('。') if len(line) > 0 ]
            # print(sentence)
            a = jiebaContent(sentence)
            printStr = 'now is going on ' + str(idx+1) + ',which is ' + str(math.floor((idx+1) / count * 100)) + str(
                '% finished')
            sys.stdout.write('\r' + printStr)
            with open(u'./count/yahoo0724.csv', 'a', encoding='utf8') as fw:
                for lang, counts in wc.most_common():
                    fw.write('{},{}\n'.format(lang, counts))

    except Exception as e:
        print("connMobile01 error in row{} , :".format(idx+1), e)
        conn.rollback()

    conn.commit()
    conn.close()

if __name__ == '__main__':
    start = time.time()
    with open('..\\jupyter\\textMining\\moedict.txt','r',encoding='utf8') as frN:
        normal_words = frN.read().split('\n')
    with open('..\\jupyter\\textMining\\stopWords.txt','r',encoding='utf8') as frW:
        stop_words = frW.read().split('\n')
    with open('..\\jupyter\\textMining\\eng_stop_words.txt','r',encoding='utf8') as frW:
        eng_stop_words = frW.read().split('\n')
    normal_words += stop_words
    normal_words += eng_stop_words
    main()
    end = time.time()
    elapsed = end - start
    print("Time taken :{} seconds.".format(elapsed))
