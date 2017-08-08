import requests as r
from bs4 import BeautifulSoup
import time
import random
from random import randint
import json
import redis
import multiprocessing
from pymongo import MongoClient
from datetime import datetime
import math
from dbconfig import Redisdb, mySQL_project, mongodb

def gen_proxies():
    proxy_url = que.blpop('proxy_list')[1].decode('utf8')
    proxy_gen = {'http': proxy_url, 'https': proxy_url}
    print(proxy_url)
    return proxy_gen

#將所有的request請求放到同一的fun處理Exception
def connect_until_success(url):
    import requests.exceptions
    # count = 0
    while True:  #count < 100
        try:
            res = r.get(url, headers=gen_headers(), timeout=2)
            break
        except requests.exceptions.ReadTimeout:
            # count += 1
            pass
        except requests.exceptions.ConnectionError:
            # count += 1
            pass
        except IndexError as e:
            print(e)
            pass
        except (requests.exceptions.ProxyError, ConnectionRefusedError) as e:
            print(e)
            proxies = gen_proxies()
            pass
        except Exception as e:
            pass
            print('url:' + url )
    return res

def gen_headers():
    headers = {'User-Agent': user_agents[randint(0, len(user_agents) - 1)]}
    return headers

# Create db
# def creatDB():
#     db = sqlite3.connect("./Mobile01.db")
#     cur = db.cursor()
#     cur.execute("drop table Mobile01")
#     cur.execute("CREATE TABLE Mobile01(url text,title text,author text,tm int,Board text,content text,reply_no int,replies text);")
#     db.commit()
# # creatDB()

#num of totalArticle
def reply_num(url):
    contentURL = url+"&p="+str(contentPage(url))
    # print(contentPage(url))
    reply_res = connect_until_success(contentURL)
    soup = BeautifulSoup(reply_res.text,'lxml')
    reply_no = int(len(soup.select('main > article')))
    # print(reply_no)
    reply_id = int(soup.select('.date')[reply_no-1].text.split('\xa0')[2][1:])-1
    return reply_id

#pages of innerURL
def contentPage(url):
    res = connect_until_success(url)
    soup = BeautifulSoup(res.text, 'lxml')
    contentPage = int(soup.select_one(".numbers").text.split('共')[1].split('頁')[0])
    # print("page : ",contentPage)
    return contentPage

#content to innerURL
def getSubContent(url):
    replies = []
    pages = contentPage(url)
    # print(pages)
    for page in range(1,pages+1):    #此評論的所有的內頁
        try:
            contentURL = url+"&p="+str(page)
            # print(contentURL)
            time.sleep(int(random.random()*3+1))
            reply_res = connect_until_success(contentURL)
            reply_soup = BeautifulSoup(reply_res.text,'lxml')
            reply_no = int(len(reply_soup.select('main > article')))
            # print("article_no : ",reply_no)
            while (reply_no > 0):
                try:
                    reply = {}
                    reply_id = int(reply_soup.select('.date')[reply_no-1].text.split('\xa0')[2][1:])
        #             print(reply_id)
                    if reply_id != 1:
                        author_id = reply_soup.select('.fn > a')[reply_no-1].text
                        # print("author_id",author_id)

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
                        reply["content"] = content.text.strip().encode('utf8').decode('utf8')
                        reply["author_id"] = str(author_id)
                        replies.append(reply)

                    reply_no -= 1
                except Exception as e:
                    print("getSubContent err message : ", e)
                    reply_no -= 1
                    pass
            # print("real article_no : ",len(replies) + 1)
            # print("repliesOfPage",replies)
        except Exception as e:
            print("getSubContent err message : ",e)
            pass
    reply_json = json.dumps(replies)
    return reply_json

#add to sqlite/mongodb
def add_to_mongodb(collection, url, reply_no):

    res = connect_until_success(url)
    soup = BeautifulSoup(res.text, 'lxml')

    title = soup.select_one('.topic').text
    # print("title : ", title)

    author = soup.select_one('.fn > a').text
    # print("author : ", author)

    poTime = soup.select_one('.date').text.split('\xa0')[0]
    poTimeArray = time.strptime(poTime, "%Y-%m-%d %H:%M")
    tm = int(time.mktime(poTimeArray))
    # print("tm : ", tm)

    boardTag = soup.select('.nav > a')
    Board = boardTag[3].text
    # print("Board : ", Board)

    content = soup.select_one('.single-post-content').text.strip()
    # print("content : ", content)

    # reply_no = reply_num(url)
    # print("reply_no : ", reply_no)

    replies = getSubContent(url)
    # print("replies : ", replies)

    comment = {'url': url, 'title': title, 'author': author,
               'tm': datetime.fromtimestamp(math.floor(float(tm))), 'Board': Board, 'content': content,
               'reply_no': reply_no, 'replies': json.loads(replies)}
    try:
        #Insert to mongodb
        collection.insert_one(comment)

        #Insert to sqlite
        # cursor.execute('INSERT INTO Mobile01 VALUES (?,?,?,?,?,?,?,?)',
        #                [url, title, author, tm, Board, content, reply_no, replies])

        # print(comment)
    except Exception as e:
        print("add_to_mongodb : ", e)

#更新到sqlite/mongodb
def update_to_mongodb(collection,url, reply_no):
    replies = getSubContent(url)
    # print("replies : ", replies)
    try:
        collection.find_one_and_update({'url':url},{'$set': {'reply_no': reply_no, 'replies': replies}})
        
        # cursor.execute('update Mobile01 set reply_no = ? , replies = ? where url = ?',
        #                [reply_no, replies, url])

        # conn.commit()
        # conn.close()
    except Exception as e:
        print("failed: update_to_mongodb : ", e)
        # conn.rollback()

#檢查是否在sqlite
def check_duplicates(collection,url):
    new_reply_no = reply_num(url)
    old_article = collection.find_one({'url': 'url'})

    if old_article:
        old_reply_no = old_article['reply_no']
        if new_reply_no != old_reply_no :
            return (2, new_reply_no)        #比較回文數是否有更新
        else:
            return (3, new_reply_no)
    else:
        return (1, new_reply_no)            #新增評論jsonObj

def main():
    client = MongoClient(mongodb.host, mongodb.port)
    collection = client.final_project.mobile01
    while que.llen('mobile01_list') != 0:
        url = que.blpop('mobile01_list')[1].decode('utf8')
        count = 2
        # print(url)
        while count:
            try:
                is_dulicate, reply_no = check_duplicates(collection, url)

                if is_dulicate == 1:
                    add_to_mongodb(collection, url, reply_no)
                    break
                elif is_dulicate == 2:
                    update_to_mongodb(collection,url, reply_no)
                    break
                else:
                    print('same car exist pass')
                    break
            except Exception as e:
                print("main : ",e)
                count -= 1

if __name__ == "__main__":
    referers = ['tw.yahoo.com', 'www.google.com', 'http://www.msn.com/zh-tw/', 'http://www.pchome.com.tw/']
    user_agents = [
        'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
        'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)']
    cookie = 'PHPSESSID=5rvg4cdkfpbd9skuntk0ifo2r2; _gat=1; _ga=GA1.3.815060608.1496624322; _gid=GA1.3.657905158.1496852224'

    carName_list = ['PORSCHE', 'NISSAN', 'TOYOTA', 'MITSUBISHI', 'HONDA', 'FORD', 'AUDI', 'MERCEDES BENZ', 'BMW',
                    'LEXUS', 'VOLKSWAGEN', 'MAZDA', 'SUBARU', 'SUZUKI', 'VOLVO']

    que = redis.StrictRedis(host=Redisdb.host, port=Redisdb.port, db=0, password=Redisdb.password)
    results = []
    multiprocessing.freeze_support()  # Windows 平台要加上这句，避免 RuntimeError
    pool = multiprocessing.Pool()
    cpus = multiprocessing.cpu_count()

    for i in range(0, cpus):
        result = pool.apply_async(main)
        results.append(result)
    pool.close()
    pool.join()




