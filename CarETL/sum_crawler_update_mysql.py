from dbconfig import Redisdb, mySQL_project
import requests
import requests.exceptions
import pymysql
from datetime import datetime
import redis
import sys
import time

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

    
def connect_until_success(url):
    header = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch, br",
            "Accept-Language": "zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Cookie": "__gads=ID=6dd06a6928bab430:T=1496776174:S=ALNI_MZw1RvLJ_ezD18iQcnLFUA0LsYbNQ; __RequestVerificationToken=oMBYkFk0gEocJ5npv8uUasjwq3v5YPCz5DB41DTuYdTP5P5feuleW8a7zBNYlUdZPxzPOBn4RRaktD4xSj1i-oMxRpg1;_gat=1; __asc=ec81b66215c834b6738ccfdfa0b; __auc=b3e83d1315c7ecf1e1aed870d7a; _ga=GA1.3.231933620.1496776122; _gid=GA1.3.1394749181.1496776122",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }
    
    count = 0
    while count < 50:
        try:
            res = requests.post(url, headers = header, timeout = 3)
            while res.status_code==502 or res.status_code==403 or ('SUM賞車網' not in res.text):
#                 proxies = gen_proxies()
                res = requests.post(url, headers = header, timeout = 3)
                count += 1
                if count == 50:
                    logger.error('got event: {} cannot connect'.format(url))
                    break
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
        except (requests.exceptions.ProxyError, ConnectionRefusedError) as e:
            count += 1
            if count == 50:
                logger.error('got event: {} cannot connect'.format(url))
            time.sleep(count * 0.1)
    return res

def update_to_mysql(url):
    today = datetime.today()
    sql = 'UPDATE {} SET oostock = 1, oostock_time = "{}" where url = "{}"'
    while True:
        try:
            conn = pymysql.connect(host=mySQL_project.IP, port=3306,
                                   user='team1', passwd=mySQL_project.passwd, db='team1', charset='utf8')
            break
        except pymysql.OperationalError:
            pass
    c = conn.cursor()
    try:
        c.execute(sql.format(mySQL_project.final_table, today, url))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error('at data {} mysql server cannot connect: {}'.format(url, e))
        conn.rollback()
        conn.close


def main():
    starttime = time.time()
    que = redis.StrictRedis(host=Redisdb.host, port=Redisdb.port, db=0, password=Redisdb.password)
    alreadyCrawled = 0
    while True:
        url = que.blpop('sum_update_url')[1].decode('utf8').strip('(').strip(')').strip(",").strip("'")
        if url == 'e':
            print('update finished')
            break
        res = connect_until_success(url)
        alreadyCrawled+=1
        printstring = ('*****we have crawled ' + str(alreadyCrawled) + ' pages *****')
        sys.stdout.write('\r' + printstring )
        if "已收訂" in res.text:
            update_to_mysql(url)
        endtime = time.time()
        if endtime - starttime >= 280:
            break
        else:
            pass

if __name__=='__main__':
    main()
    
        

