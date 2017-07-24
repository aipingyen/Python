from pymongo import MongoClient
import time
import sys
import math
import time
import datetime
from multiprocessing import Pool,cpu_count,freeze_support
import codecs
# 處理編碼的套件
import operator
##處理字典檔排序的套件

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


def cutSentence(string, keywords):  ##放入原始文章路徑, 增加斷詞的list
    #     text = codecs.open(text_path,"r","utf-8")   #開檔 #讀取存成TXT檔的文字，讀入後統一轉成UTF-8格式
    sentence = ""
    textList = []
    with open('C:\\jupyter\\textMining\\specialSignList.txt', "r", encoding='utf-8') as fr:
        stopWd = fr.read().strip().split('\n')
        cutlist = [signal for signal in stopWd if len(stopWd) > 0]
    print('\n',type(string))
    # print(string)
    for word in string:
        # print(word)
        if word not in cutlist:  # 如果文字不是標點符號，就把字加到句子中
            sentence += word
            # print(sentence)
        else:
            textList.append(sentence)  # 如果遇到標點符號，把句子加到 text list中
            sentence = ""
            # print(textList)

    return textList  # 傳回一個文字陣列


def ngram(textLists, n, minFreq):  #處理好的文章(LIST檔，utf-8編碼);字詞的長度單位;放至少要幾次以上

    words = []  # 存放擷取出來的字詞
    words_freq = {}  # 存放字詞:計算個數
    result = []
    for textList in textLists:   #已斷句的list
        for w in range(len(textList) - (n - 1)):  # 要讀取的長度隨字詞長度改變
            words.append(textList[w:w + n])  # 抓取長度w-(n-1)的字串

    for word in words:
        if word not in words_freq:  # 如果這個字詞還沒有被放在字典檔中
            words_freq[word] = words.count(word)  # 就開一個新的字詞，裡面放入字詞計算的頻次

    words_freq = sorted(words_freq.items(), key=operator.itemgetter(1),reverse=True)  # change words_freq from dict to list

    for word in words_freq:
        if word[1] >= minFreq:
            result.append(word)

    return result  ##回傳一個陣列[詞,頻次]


def longTermPriority(string, maxTermLength, minFreq):
    longTerms = []  # 長詞
    longTermsFreq = []  # 長詞+次數分配
    text_list = cutSentence(string, longTerms)  # return 斷句的 list
    print(len(text_list))

    for i in range(maxTermLength, 1, -1):   #7次
        words_freq = ngram(text_list, i, minFreq)  #把斷句的list丟到ngram  去切大小算頻率

        for word_freq in words_freq:
            longTerms.append(word_freq[0])
            # print word_freq[0]
            longTermsFreq.append(word_freq)
            # print word_freq

    return longTermsFreq

def writeInCSV(longTermsFreq):
    with open("C:\\Users\\BIG DATA\\Desktop\\n-gram_Fo.txt", 'w', encoding='utf-8') as fw:
        for k, v in longTermsFreq:
            fw.write("{},{}".format(k, v) + '\n')


def multi(total_word, maxTermLength, minFreq):
    freeze_support()
    pool = Pool(8)
    # cpus = cpu_count()
    # for i in range(0, 8):
    pool.apply_async(longTermPriority, args=(total_word, maxTermLength, minFreq, ), callback=writeInCSV)
    pool.close()
    pool.join()


def main():
    IP = 'localhost'  # '10.120.37.11'
    client = MongoClient(IP, 27017)
    # Select database
    db = client.final_project

    # Select collection
    collection = db.mobile01_copy

    count = collection.find({"Board":"Ford"}).count()
    print("筆數 : ", count)
    comment = collection.find({"Board":"Ford"})
    # print(comment)
    start = time.time()
    total_word = ""
    i = 0
    try:
        for idx in range(count):
            i += 1
            content = catch_allContent(comment[idx])  #return allContent list
            data = content[0].replace('\r\n', '').replace('\r', '')
            total_word += data
            print("          ",i)
            printStr = 'now is going on ' + str(idx + 1) + ',which is ' + str(math.floor((idx + 1) / count * 100)) + str('% finished')
            sys.stdout.write('\r' + printStr)
        multi(total_word, 7, 2)   #丟到多進程
        # print(longTermFreq)
        end = time.time()
        elapsed = end - start
        print("Time taken :{} seconds.".format(elapsed))

    except Exception as e:
        print("mobile01 error in row{} , :".format(idx + 1), e)


if __name__ == '__main__':

    main()
