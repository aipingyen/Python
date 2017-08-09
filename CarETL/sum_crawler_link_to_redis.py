from dbconfig import Redisdb, mySQL_project
import requests.exceptions
from random import randint
from bs4 import BeautifulSoup
import sys
import redis
import time
import pymysql
import logging

#download urls
def push_to_redis(links):              #接收list  以element push to redis list
    for link in links:
        que.rpush('sum_url', link)     #push list to redis

def check_data_in_mysql(url):
    if url in existing_data:
        return True
    else:
        return False

#將所有的request請求放到同一的fun處理Exception
def connect_until_success(url):
    header['User-Agent'] = user_agents[randint(0, len(user_agents) - 1)]
    header['Referer'] = referers[randint(0, len(referers) - 1)]
    count = 0
    while count < 50:
        try:
            res = requests.post(url, headers=header, timeout=2)
            break
        except requests.exceptions.ReadTimeout:
            count += 1
            if count == 50:
                logger.info('got event: {} cannot connect'.format(url))
            time.sleep(count * 0.1)
        except requests.exceptions.ConnectionError:
            count += 1
            if count == 50:
                logger.info('got event: {} cannot connect'.format(url))
            time.sleep(count * 0.1)
    return res

def get_pages(carName):
    page_list = []
    url = 'http://www.sum.com.tw/result1_all.php?brand='+carName+'&year=2000&year1=2017'
    res = connect_until_success(url)
    soup = BeautifulSoup(res.text,'lxml')
    pages = int(soup.select_one('.goTo > b').text)
    href_list = car_url(carName, pages)
    page_list.append(pages)
    return href_list

def car_url(carName, pages):
    href_list = []
    host = 'http://www.sum.com.tw/'
    for page in range(1, pages + 1):
        printstring = ('*****now is crawling ' + carName + ' at page: ' + str(page) + '*****')
        sys.stdout.write('\r' + printstring )
        url = 'http://www.sum.com.tw/result1_all.php?sn=&page={}&brand={} &year=2000&year1=2017'.format(page,carName)
        res =  connect_until_success(url)
        soup = BeautifulSoup(res.text,'lxml')
        car_href = soup.select('li.carInfo > strong > a')
        for i, idx in enumerate(car_href):
            if i %2 ==1:  #網站架構問題  挑出奇數個的id
                if not check_data_in_mysql(host+idx['href']):    #將url丟到此fun檢查是否與相同  有就是false
                    href_list.append(host+idx['href'])

    return href_list

def main():
    count = 0
    while count < 50:
        try:
            conn = pymysql.connect(host=mySQL_project.IP, port=3306,
                                   user='team1', passwd=mySQL_project.passwd, db='team1', charset='utf8')    #連線到mysql取出已在資料庫的url
            break
        except pymysql.OperationalError:
            count += 1
            if count == 50:
                logger.error('at data getting mysql server cannot connect')
    c = conn.cursor()
    global existing_data
    existing_data = []
    sql = "select url from {} where source ='{}' and (deal != '1' or deal is null)"
    c.execute(sql.format(mySQL_project.backup_table, 'SUM'))         #找出未成交的url
    for row in c:
        existing_data.append(row)
    conn.commit()
    conn.close()

    carName_list = ['VOLVO', 'VW', 'SUZUKI', 'SUBARU', 'PORSCHE', 'AUDI', 'BENZ', 'BMW', 'LEXUS', 'FORD', 'TOYOTA',
                    'MAZDA', 'HONDA', 'MITSUBISHI', 'NISSAN']
    que.delete('sum_url')                                           #將舊的list of redis清空
    for carName in carName_list:
        href_list = get_pages(carName)
        push_to_redis(href_list)
    end = ['end'] * 1000
    push_to_redis(end)
    print("\n" + 'crawling finished')


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    que = redis.StrictRedis(host=Redisdb.host, port=Redisdb.port, db=0, password=Redisdb.password)

    referers = ['tw.yahoo.com', 'www.google.com', 'http://www.msn.com/zh-tw/', 'http://www.pchome.com.tw/']
    user_agents = [
        'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
        'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)']
    header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': 'PHPSESSID=9d14keg2t9rr1cmovr3p6k63k3; _gat_UA-1515188-3=1; _dc_gtm_UA-34980571-20=1; __asc=c661c32d15cd4d990e10bbd0037; __auc=c661c32d15cd4d990e10bbd0037; _ga=GA1.3.325420990.1498219648; _gid=GA1.3.1025657883.1498219648; _TUCI=sessionNumber+1000&ECId+155&hostname+www.sum.com.tw&pageView+4000; _TUCI_T=sessionNumber+17340&pageView+17340; _TUCS=1',
        'Host': 'www.sum.com.tw',
        'Upgrade-Insecure-Requests': '1'
    }

    main()