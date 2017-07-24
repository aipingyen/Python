import sqlite3
import requests as r
from  bs4 import BeautifulSoup
import time
import random
from random import randint
import json
import redis
import logging
# from lib.toolbox import gen_header

# header_str = 'User-Agent:Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
# HEADER = gen_header(header_str)
#referers
referers = ['tw.yahoo.com', 'www.google.com', 'http://www.msn.com/zh-tw/', 'http://www.pchome.com.tw/']
user_agents = ['Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
             'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9',
              'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
              'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)']
cookie = 'PHPSESSID=5rvg4cdkfpbd9skuntk0ifo2r2; _gat=1; _ga=GA1.3.815060608.1496624322; _gid=GA1.3.657905158.1496852224'

carName_list = ['PORSCHE','NISSAN','TOYOTA','MITSUBISHI','HONDA','FORD','AUDI','MERCEDES BENZ','BMW','LEXUS','VOLKSWAGEN','MAZDA','SUBARU','SUZUKI','VOLVO']
contentPage = 0

class Redisdb:
    host = '192.168.114.10'
    port = '6379'
    password = 'team1'

def gen_headers():
    headers = {'User-Agent': user_agents[randint(0, len(user_agents) - 1)]}
    # ,'Referer': referers[randint(0, len(referers) - 1)]
    return headers

# Create db
def creatDB():
    db = sqlite3.connect("./Mobile01.db")
    cur = db.cursor()
    cur.execute("drop table Mobile01")
    cur.execute("CREATE TABLE Mobile01(url text,title text,author text,tm int,Board text,content text,reply_no int,replies text);")

    db.commit()
creatDB()

#pages of innerURL
def contentPage(url):
    global contentPage
    res = r.get(url, headers=gen_headers())
    soup = BeautifulSoup(res.text, 'lxml')
    contentPage = int(soup.select_one(".numbers").text.split('共')[1].split('頁')[0])
    print("page : ",contentPage)
    # return contentPage

#num of totalArticle
def reply_num(url):
    contentURL = url+"&p="+str(contentPage)
#     print(contentPage(url))
    reply_res = r.get(contentURL,headers=gen_headers())
    soup = BeautifulSoup(reply_res.text,'lxml')
    reply_no = int(len(soup.select('main > article')))
#     print(reply_no)
    reply_id = int(soup.select('.date')[reply_no-1].text.split('\xa0')[2][1:])
    return reply_id

#content to innerURL
def getSubContent(url):
    replies = []
    pages = contentPage
    print(pages)
    for page in range(1,pages+1):    #此評論的所有的內頁
        contentURL = url+"&p="+str(page)
        print(contentURL)
        time.sleep(int(random.random()*3+1))
        reply_res = r.get(contentURL,headers=gen_headers())
        reply_soup = BeautifulSoup(reply_res.text,'lxml')
        reply_no = int(len(reply_soup.select('main > article')))
        print("article_no : ",reply_no)
        while (reply_no > 0):
            reply = {}
            reply_id = int(reply_soup.select('.date')[reply_no-1].text.split('\xa0')[2][1:])
#             print(reply_id)
            if reply_id != 1:
                author_id = reply_soup.select('.fn > a')[reply_no-1].text
#                 print("author_id",author_id)

                reply_time = reply_soup.select('.date')[reply_no-1].text.split('\xa0')[0]
                poTimeArray = time.strptime(reply_time, "%Y-%m-%d %H:%M")
                tm = int(time.mktime(poTimeArray))
#                 print("tm",tm)

                content = reply_soup.select('.single-post-content')[reply_no-1]
                for blockquote in content.find_all('blockquote'):
                    blockquote.decompose()
                # print("content : \n",content.text.strip())

                reply["reply_id"] = reply_id
                reply["tm"] = tm
                reply["content"] = content.text.strip()
                reply["author_id"] = str(author_id)
                replies.append(reply)
            reply_no -= 1

    replies = json.dumps(replies)

    return replies

#add to sqlite
def add_to_sqlite(url):
    conn = sqlite3.connect('./Mobile01.db')
    cursor = conn.cursor()

    res = r.get(url, headers=gen_headers())
    soup = BeautifulSoup(res.text, 'lxml')

    title = soup.select_one('.topic').text
    print("title : ", title)

    author = soup.select_one('.fn > a').text
    print("author : ", author)

    poTime = soup.select_one('.date').text.split('\xa0')[0]
    poTimeArray = time.strptime(poTime, "%Y-%m-%d %H:%M")
    tm = int(time.mktime(poTimeArray))
    print("tm : ", tm)

    boardTag = soup.select('.nav > a')
    Board = boardTag[3].text
    print("Board : ", Board)

    content = soup.select_one('.single-post-content').text.strip()
    print("content : ", content)

    reply_no = reply_num(url)
    print("reply_no : ", reply_no)

    replies = getSubContent(url)
    print("replies : ", replies)
    try:
        cursor.execute('INSERT INTO Mobile01 VALUES (?,?,?,?,?,?,?,?)',
                       [url, title, author, tm, Board, content, reply_no, replies])
        conn.commit()
    except Exception as e:
        print(e)
        conn.rollback()

#更新到sqlite
def update_to_sqlite(url):
    conn = sqlite3.connect('./Mobile01.db')
    cursor = conn.cursor()

    reply_no = reply_num(url)
    print("reply_no : ", reply_no)

    replies = getSubContent(url)
    print("replies : ", replies)
    try:
        cursor.execute('update Mobile01 set(reply_no, replies)',    #
                       [reply_no, replies])
        conn.commit()
    except Exception as e:
        print(e)
        conn.rollback()

#檢查是否在sqlite
def check_duplicates(url):
    conn = sqlite3.connect('./Mobile01.db')
    cursor = conn.cursor()

    new_reply_no = reply_num(url)

    num = list(
        cursor.execute('SELECT * FROM Mobile01 WHERE url = ? AND reply_no = ? ',
                       (url, new_reply_no)))
    print("exist? : ",num)
    # old_reply_obj = list(
    #         cursor.execute('SELECT reply_no FROM Mobile01 WHERE url = ? ',
    #                         (url,)))
    if len(num) != 0:
        cursor.execute('SELECT reply_no FROM Mobile01 WHERE url = ? ', (url,))
        old_reply_obj = cursor.fetchall()
        print(old_reply_obj)
        old_reply_no = old_reply_obj[0][0]
        print(old_reply_no)

    if len(num) == 0:                         #篩選條件
        return 1
    elif (new_reply_no > old_reply_no) and len(num) != 0:
        return 2
    else:
        return 3

# def gen_proxies():
#     proxy_url = que.blpop('proxy_list')[1].decode('utf8')   #blpop
#     proxy_gen = {'http': proxy_url, 'https': proxy_url}     #http   https
#     print(proxy_url)
#     return proxy_gen

# with open('./Mobile01/{}.csv'.format('AUDI'), 'r') as fr:
#     urls = fr.read().strip().split()
#     for url in urls:
#         time.sleep(int(random.random()*3+1))
#         add_to_sqlite(url)

#checkData & add_to_sql
que = redis.StrictRedis(host=Redisdb.host, port=Redisdb.port, db=0, password=Redisdb.password)#
# while que.llen('mobile01_list') != 0:
#     logger = logging.getLogger(__name__)
#     count = 3
#     url = que.blpop('mobile01_list')[1].decode('utf8')
url = "https://www.mobile01.com/topicdetail.php?f=264&t=197264"
count = 3
print(url)
while count:
    try:
        if check_duplicates(url) == 1:
            contentPage(url)
            add_to_sqlite(url)
            break
        elif check_duplicates(url) == 2:
            update_to_sqlite(url)
            break
        else:
            # logger.info('same car exist pass')
            print('same car exist pass')
            break
    except IndexError as e:
        print(e)
        # logger.exception(e)
        count -= 1
    # except (r.exceptions.ProxyError, ConnectionRefusedError) as e:
    #     logger.exception(e)
    #     proxies = gen_proxies()
    except Exception as e:
        print(e)
        count -= 1
        # logger.exception('url:' + url + ' count' + str(count))
# Push to failed list
if count == 0:
    que.lpush('mobile01_failed', url)