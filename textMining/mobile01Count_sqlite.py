import sqlite3
import json
import sys
import math
import jieba
from collections import Counter
# wc = Counter()
# carName_list = ['BMW','LEXUS']
# carName_list = ['NISSAN','TOYOTA']
# carName_list = ['MITSUBISHI','HONDA']
# carName_list = ['FORD','BENZ']
carName_list = ['VOLKSWAGEN','MAZDA']
#'BMW','LEXUS','NISSAN','TOYOTA','MITSUBISHI','HONDA','FORD','BENZ','VOLKSWAGEN','MAZDA'


# catch all text and counter
def catch_allContent(comment):
    all_content = ''
    all_content += comment['content']
    for i in range(comment['reply_no']):
        all_content += comment['replies'][i]['content']

    return all_content
# catch_allContent()


def jiebaContent(content):
    jieba.load_userdict("C:\\jupyter\\textMining\\moedict.txt")
    strip_con = jieba.cut(content,cut_all=False)
    jiebaContent = ','.join(strip_con).split(',')
    return jiebaContent


def wordCount(jiebaContent):
    global wc
    with open('C:\\jupyter\\textMining\\moedict.txt','r',encoding='utf8') as frN:
        normal_words = frN.read().split('\n')
    with open('C:\\jupyter\\textMining\\stopWords.txt','r',encoding='utf8') as frW:
        stop_words = frW.read().split('\n')
    with open('C:\\jupyter\\textMining\\eng_stop_words.txt','r',encoding='utf8') as frW:
        eng_stop_words = frW.read().split('\n')
    normal_words += stop_words
    normal_words += eng_stop_words
#     wc = Counter()
    for word_raw in jiebaContent:
        word = word_raw.replace('\r\n', '').replace('\n', '').upper()
        if word not in normal_words:    # and sign_words
            if word in wc:
                wc[word] += 1
            else:
                wc[word] = 1
    # return wc.most_common()



# connect to mobile01.db
def connMobile01(name):
    conn = sqlite3.connect("C:\\Users\\BIG DATA\\PycharmProjects\\untitled\\Mobile01.db")
    cur = conn.cursor()
    print(carName)
    count = cur.execute("select count(*) from mobile01 where board=?;", (name,)).fetchone()[0]
    print(count)
    sql = "select * from mobile01 where board=? ;"
    cur.execute(sql, (name,))

    try:
        for idx, row in enumerate(cur):
            comment = {'url': row[0], 'title': row[1], 'author': row[2], 'tm': row[3], 'Board': row[4],
                       'content': row[5], 'reply_no': row[6], 'replies': json.loads(row[7])}
            #             print(typea(comment))
            #             print(comment['content'])
            #         print(comment['replies'])
            content = catch_allContent(comment)
            strip_con = jiebaContent(content)
            wordCount(strip_con)
            #             print(strip_con)
            printStr = 'now is going on ' + str(idx+1) + ',which is ' + str(math.floor((idx+1) / count * 100)) + str(
                '% finished')
            sys.stdout.write('\r' + printStr)
        print(wc)
        # with open('./count/{}.csv'.format(name), 'w',encoding='utf8') as fw2:
        #     for lang, counts in wc.most_common():
        #         fw2.write('{},{}\n'.format(lang, counts))
    except Exception as e:
        print("{} error in row{} , :".format(name,idx+1), e)
        conn.rollback()

    conn.commit()
    conn.close()

if __name__ == '__main__':
    for carName in carName_list:
        wc = Counter()

        connMobile01(carName)
