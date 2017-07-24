import requests as r
from  bs4 import BeautifulSoup
import math
import threading
import time
import re
import logging
from random import randint
import random
import redis

referers = ['tw.yahoo.com', 'www.google.com', 'http://www.msn.com/zh-tw/', 'http://www.pchome.com.tw/']
user_agents = ['Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
             'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9',
              'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
              'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)']
cookie = 'PHPSESSID=5rvg4cdkfpbd9skuntk0ifo2r2; _gat=1; _ga=GA1.3.815060608.1496624322; _gid=GA1.3.657905158.1496852224'

host = 'http://www.sum.com.tw/'
carName_list = ['VOLVO','VW','SUZUKI','SUBARU','PORSCHE','AUDI','BENZ','BMW','LEXUS','FORD','TOYOTA','MAZDA','HONDA','MITSUBISHI','NISSAN']
#,'VW','SUZUKI','SUBARU','PORSCHE','AUDI','BENZ','BMW','LEXUS','FORD','TOYOTA','MAZDA','HONDA','MITSUBISHI','NISSAN'
logger = logging.getLogger(__name__)

class Redisdb:
    host = '192.168.196.172'
    port = '6379'
    password = 'team1'

def gen_headers():
    headers = {'User-Agent': user_agents[randint(0, len(user_agents) - 1)],
               'Referer': referers[randint(0, len(referers) - 1)]}
    return headers

def car_url(carName, pages):
    href_list = []
    count = 5
    for page in range(1, pages + 1):
        try:
            while count:
                url = 'http://www.sum.com.tw/result1_all.php?sn=&page={}&brand={} &year=2000&year1=2017'.format(page,carName)
                res = r.get(url,headers=gen_headers())
                soup = BeautifulSoup(res.text,'lxml')
                car_href = soup.select('li.carInfo > strong > a')
                for idx in car_href:
                    href_list += re.findall('.+\?.*', host+idx['href'])
                print(carName,len(href_list))
                # with open('./SUM/{}.csv'.format(carName), 'a') as fw:
                #     fw.write('\n'.join(href_list))
                #     fw.write('\n')
                break
        except Exception as e:
            time.sleep(int(random.random() * 3 + 1))
            count -= 1
            logger.exception(url + 'count=' + str(count))
    return href_list

def get_pages(carName):
    page_list = []
    # for carName in carName_list:
    url = 'http://www.sum.com.tw/result1_all.php?brand='+carName+'&year=2000&year1=2017'
    res = r.get(url,headers=gen_headers())
    soup = BeautifulSoup(res.text,'lxml')
    pages = int(soup.select_one('.goTo > b').text)
    href_list = car_url(carName, pages)
    page_list.append(pages)

    print(page_list)
    return href_list

def push_url(carName):
    urls = get_pages(carName)
    print("url_no :",len(urls))

    count = 5
    for url in urls:
        try:
            while count:
                print("url = ",url)
                que = redis.StrictRedis(host=Redisdb.host, port=Redisdb.port, db=0, password=Redisdb.password)#
                que.lpush('SUM_list', url)
                print("lpush ok")
                break
        except Exception as e:
            time.sleep(int(random.random() * 3 + 1))
            count -= 1
            logger.exception(url + 'count=' + str(count))

for carName in carName_list:
    push_url(carName)