from dbconfig import Redisdb, mySQL_project
import requests
import requests.exceptions
from datetime import datetime
import pymysql
from bs4 import BeautifulSoup
import re
import redis
from random import randint
import sys
import time

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# def gen_proxies():
#     proxy_url = que.blpop('proxy_list')[1].decode('utf8')
#     proxy_gen = {'http': proxy_url, 'https': proxy_url}
#     return proxy_gen

def connect_until_success(url):
    # startTime = time.time()
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

    header['User-Agent'] = user_agents[randint(0, len(user_agents) - 1)]
    header['Referer'] = referers[randint(0, len(referers) - 1)]
    count = 0
    while count < 50:
        try:
            # proxies = gen_proxies()
            res = requests.post(url, headers=header, timeout=3)
            while res.status_code == 502 or res.status_code == 403 or ('SUM賞車網' not in res.text) and count < 50:
                # print('\n' + 'res.status_code == 502 or res.status_code == 403 or indexoutofbund')
                # proxies = gen_proxies()
                res = requests.post(url, headers=header, timeout=3)
                count += 1
                if count == 50:
                    logger.error('got event: {} cannot connect'.format(url))
                    break
            break
        except requests.exceptions.ReadTimeout:
            count += 1
            if count == 50:
                logger.error('got event: {} cannot connect'.format(url))
            time.sleep(count * 0.1)
        except requests.exceptions.ConnectionError:
            count += 1
            if count == 50:
                logger.error('got event: {} cannot connect'.format(url))
            time.sleep(count * 0.1)
        except (requests.exceptions.ProxyError, ConnectionRefusedError):
            count += 1
            if count == 50:
                logger.error('got event: {} cannot connect'.format(url))
            time.sleep(count * 0.1)
            # logger.exception(e)
            # print('\n' +'requests.exceptions.ProxyError, ConnectionRefusedError')
            # proxies = gen_proxies()
    # endTime = time.time()
    # print('connection spend',endTime - startTime)
    return res


def get_content(url):
    res = connect_until_success(url)
    soup = BeautifulSoup(res.text, 'lxml')

    infoList = soup.select('.infoList > li')
    for idx in infoList:
        for strong in idx.find_all('strong'):
            strong.decompose()

    formatList = soup.select('.formatArea > .formatList > li')
    #     print(len(formatList))
    for carformat in formatList:
        for span in carformat.find_all('span'):
            span.decompose()

    outfitList = soup.select('.formatArea > .outfitList > .have')
    contents = []

    # brand
    brand = soup.select(".webSite > span")[7].text.strip()
    contents.append('廠牌：' + brand)
    # postTime
    po_time = infoList[4].text
    poTimeArray = time.strptime(po_time, "%Y.%m.%d")
    tm = time.mktime(poTimeArray)
    contents.append('時間：' + str(tm))
    # title
    title_table = soup.select_one('.gradientGray_bar > h1').text
    contents.append('標題：' + title_table)
    # Eqip
    outfits = ""
    for outfit in outfitList:
        outfits += outfit.text.strip()
        outfits += ","
    contents.append('配備：' + outfits)

    content_dict = {k.split('：')[0]: k.split('：')[1] for k in contents if len(k) > 0}

    content_dict['網站'] = 'SUM'
    content_dict['連結'] = url
    # transmission
    content_dict['排擋方式'] = formatList[0].text
    # doors
    content_dict['車門'] = formatList[3].text
    # years
    if int(infoList[1].text) < 2008:
        return
    else:
        content_dict['年份'] = int(infoList[1].text)
    # color
    content_dict['色系'] = infoList[2].text.split('色')[0]
    # location
    content_dict['所在地'] = soup.select('.lineBottom')[3].text[0:3]
    # model
    content_dict['型號'] = infoList[0].text.split('-')[1].strip()
    # cc
    content_dict['排氣量'] = int(infoList[3].text.split('c')[0])
    # mileage
    mileage = formatList[8].text.split('.')[0]
    if mileage == '':
        content_dict['行駛里程'] = None
    else:
        content_dict['行駛里程'] = int(mileage)
    # price
    # deal
    price = soup.select_one('.price > span > strong').text
    match = re.match(u'已.*', price)
    if match:
        content_dict['價格'] = int(-1)
        content_dict['是否售出'] = 1
    else:
        content_dict['價格'] = float(price.replace('萬', ''))
    content_dict['是否售出'] = 0
    # offTime   如果價格＝已收訂  將data刪除  之後再找到價格＝已收訂  就知道是下架時間
    content_dict['下架時間'] = None
    # certificate
    match_sum = re.match('.*SUM.*', title_table)
    if match_sum:
        content_dict['認證'] = 'SUM'
    try:
        a = soup.select('.carMark.putCenter > a')[1].text
        match = re.match('關於YES認證', a)
        if match:
            content_dict['認證'] = 'YES'
    except IndexError as e:
        content_dict['認證'] = None

    # gasoline
    content_dict['燃油'] = formatList[1].text.split('車')[0]

    return content_dict


def add_to_mysql(content_dict):
    if content_dict != None:
        source = str(content_dict['網站'])
        url = str(content_dict['連結'])
        title = str(content_dict['標題'])
        brand = str(content_dict['廠牌'].upper().replace('VM','volkswagen').replace('M-BENZ','BENZ').replace('MERCEDES-BENZ','BENZ'))
        model = str(content_dict['型號'])
        doors = str(content_dict['車門'])
        doors = doors.replace('門', '')
        color = str(content_dict['色系'])
        cc = str(content_dict['排氣量'])
        transmission = str(content_dict['排擋方式'])
        equip = str(content_dict['配備'])

        aaa = equip.split("|")
        before = ['安全氣囊', '倒車影像顯示', '倒車雷達', '車前距雷達', '電動後視鏡', '免KEY', 'HID頭燈', '全景天窗', '霧燈', '衛星導航', 'TCS', '定速',
                  '恆溫空調', '電動尾門', '方向盤換檔控制', '方向盤音響控制']
        after = ['安全氣囊', '倒車影像', '倒車雷達', 'ACC主動式定速系統', '電動後視鏡', 'keyless免鑰系統', 'HID頭燈', '天窗', '霧燈', '衛星導航', 'TCS循跡系統',
                 '定速', '恆溫空調', '電動尾門', '換檔撥片', '多功能方向盤']
        aaa = "|".join(set(aaa).intersection(before))
        data_dict = list(zip(before, after))
        for each_equip in data_dict:
            aaa = aaa.replace(each_equip[0], each_equip[1])
        equip = aaa

        mileage = (content_dict['行駛里程'])
        years = str(content_dict['年份'])
        location = str(content_dict['所在地'])
        posttime = datetime.fromtimestamp(float(content_dict['時間']))
        price = str(content_dict['價格'])
        deal = str(content_dict['是否售出'])
        offTime = content_dict['下架時間']
        certificate = str(content_dict['認證'])
        gasoline = str(content_dict['燃油'])
        gasoline = gasoline.replace('車', '')

        query = (source, url, title, brand, model, doors, color, cc, transmission, equip,
                 mileage, years, location, posttime, price, certificate, gasoline, deal, offTime,)
        while True:
            try:
                conn = pymysql.connect(host=mySQL_project.IP, port=3306,
                                       user='team1', passwd=mySQL_project.passwd, db='team1', charset='utf8')
                break
            except pymysql.OperationalError:
                pass

        c = conn.cursor()
        try:
            command = 'INSERT INTO {} VALUES ' \
                      '(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'.format(
                mySQL_project.temp_table)
            c.execute(command, query)
            command = 'INSERT INTO {} VALUES ' \
                      '(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'.format(
                mySQL_project.backup_table)
            c.execute(command, query)
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error('at data {} mysql server cannot connect: {}'.format(url, e))
            conn.rollback()


def get_database_data():
    count = 0
    while count < 50:
        try:
            conn = pymysql.connect(host=mySQL_project.IP, port=3306,
                                   user='team1', passwd=mySQL_project.passwd, db='team1', charset='utf8')
            break
        except pymysql.OperationalError:
            count += 1
            if count == 50:
                logger.error('at data getting mysql server cannot connect')
    #     cur.set_character_set('utf8')
    c = conn.cursor()
    existing_data = []
    sql = "select url from {} where source ='{}' and (deal != '1' or deal is null)"
    c.execute(sql.format(mySQL_project.backup_table, 'SUM'))
    for row in c:
        existing_data.append(row)
    conn.commit()
    conn.close()
    return existing_data

def check_duplicates(url):
    if url in existing_data:
        return True
    else:
        return False

def main():
    starttime = time.time()

    # original setting
    alreadyCrawled = 0
    global existing_data
    existing_data = get_database_data()
    # carName_list = ['VOLVO','VW','SUZUKI','SUBARU','PORSCHE','AUDI','BENZ','BMW','LEXUS','FORD','TOYOTA','MAZDA','HONDA','MITSUBISHI','NISSAN']
    global que
    que = redis.StrictRedis(host=Redisdb.host, port=Redisdb.port, db=0, password=Redisdb.password)  #
    que.delete('sum_failed')
    # proxy = gen_proxies()
    while True:
        logger = logging.getLogger(__name__)
        count = 3
        url = que.blpop('sum_url')[1].decode('utf8')
        if url == 'end':
            break
        printstring = ('*****we have crawled ' + str(alreadyCrawled) + ' pages *****')
        sys.stdout.write('\r' + printstring)
        while count:
            try:
                if not check_duplicates(url):
                    content_dict = get_content(url)
                    add_to_mysql(content_dict)
                    existing_data.append(url)
                    alreadyCrawled += 1
                    break
                else:
                    logger.info('same car exist pass')
                    break
            except IndexError as e:
                if count == 1:
                    logger.error('at url {} indexError happened: {}'.format(url, e))
                count -= 1
            endtime = time.time()
            if endtime - starttime >= 280:
                break
            else:
                pass
            if count == 0:
                que.lpush('sum_failed', url)

    print('\n' + 'crawling finished!')

if __name__ == '__main__':
    main()

