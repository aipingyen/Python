import requests as r
from  bs4 import BeautifulSoup
import math
import re
import random
import time
import redis
from random import randint
import logging

from lib.toolbox import gen_header
header_str = 'User-Agent:Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
HEADER = gen_header(header_str)

referers = ['tw.yahoo.com', 'www.google.com', 'http://www.msn.com/zh-tw/', 'http://www.pchome.com.tw/']
user_agents = [
    'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
    'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)']

carName_list = ['NISSAN','TOYOTA','MITSUBISHI','HONDA','FORD','MERCEDES BENZ','BMW','LEXUS','VOLKSWAGEN','MAZDA']
host = 'https://www.mobile01.com/'

class Redisdb:
    host = '192.168.196.172'
    port = '6379'
    password = 'team1'

# def gen_headers():
#     headers = {'User-Agent': user_agents[randint(0, len(user_agents) - 1)],
#                'Referer': referers[randint(0, len(referers) - 1)]}
#     return headers

def carName_url():   #外網所有連結
    root_url = 'https://www.mobile01.com/forumlist.php?f=21'
    res = r.get(root_url,headers=HEADER)
    soup = BeautifulSoup(res.text,'lxml')
    name = soup.select('.subject-text > a')
    car_url = []
    for idx in name:
        if idx.text.upper() in carName_list:
            car_url.append(host+idx['href'])
    print("car_url : ", len(car_url), car_url)
    return car_url

def getPages(url):  #外網的url  共15個url

    count = 5       # retry 5 times
    while count:
        res = r.get(url, headers=HEADER)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'lxml')
            pageTag = soup.select('.pagination > a ')
            carName = soup.select(".main > h2")[1].text.upper()  # 此車種名稱
            idx = len(pageTag)
            pages = int(pageTag[(idx - 1)].text)               # 此車種的頁數
            print(carName + " , carPage: ", pages)
            time.sleep(int(random.random() * 3 + 1))
            break
        else:
            print('Cannot retrieve links Retry: {} '.format(6 - count))
            count -= 1
            time.sleep(int(random.random() * 3 + 1))

    return pages

def getURL(url, page):  #用range(pages) 將內頁網址擷取  並使用re.match篩選
    count = 5                # retry 5 times
    total_url = []
    while count:
        try:
            carURL = url+'&p='+'{}'.format(page)
            # print("carURL : ",carURL)
            res = r.get(carURL,headers=HEADER)
            if res.status_code == 200:
                soup2 = BeautifulSoup(res.text,'lxml')
                table = soup2.select('tbody > tr')
                # print("innerURL_no_from : ",len(table))           #此頁的內網有幾個
                innerURLCount = 0
                for idx in range(len(table)):                   #從每個主題抓取內頁網址
                    innerURLCount += 1
                    href = table[idx-1].select('.subject > span > a')
                    url = [host+idx["href"] for idx in href]
                    total_url += url
                time.sleep(int(random.random()*3+1))
                # print("innerURL_no_to : ",innerURLCount)
                break
            else:
                print('Cannot retrieve links from page {} Retry: {} '.format(page, 6 - count))
                count -= 1
                time.sleep(int(random.random() * 3 + 1))
        except Exception as e:
            print(
                'Cannot retrieve links from page {} Retry: {} Error: {}'.format(page, 6 - count, e))
            count -= 1
            time.sleep(int(random.random() * 3 + 1))
    if count == 0:
        print('[Error] Page {:2} failed'.format(page))
    return total_url

def push_url(url):
    pageCount = 0
    page_list = []
    pages = getPages(url)
    page_list.append(pages)
    for page in range(1, pages + 1):
        total_url = getURL(url, page)                 #catch total_url
        pageCount += 1                              # 計算此車種的頁數
        # logger = logging.getLogger(__name__)
        count = 5
        try:
            while count:
                for inner_url in total_url:  #for idx, url in enumerate(urls):
                    # print(inner_url)
                    que = redis.StrictRedis(host=Redisdb.host, port=Redisdb.port, db=0, password=Redisdb.password)#
                    que.lpush('mobile01_list', inner_url)
                break
        except Exception as e:
            time.sleep(int(random.random() * 3 + 1))
            count -= 1
            # logger.exception(url + 'count=' + str(count))
            print(url + 'count=' + str(count))
    print("TotalPage_to : ", pageCount)
    print(page_list)
    print(len(page_list))

import multiprocessing

url_list = []

if __name__ == "__main__":
    for url in carName_url():
        url_list.append(url)
        if len(url_list) == 1:
            pool = multiprocessing.Pool(processes=8)
            res = pool.map(push_url,url_list)
            pool.close()
            url_list = []
        else:
            print(len(url_list))

    # pool = multiprocessing.Pool(processes=8)
    # res = pool.map(push_url,carName_url())
    # pool.close()
