import requests as r
from  bs4 import BeautifulSoup
import re
import logging
import sqlite3
import time
import redis
from random import randint

host = 'http://www.sum.com.tw/'
carName_list = ['VOLVO','VW','SUZUKI','SUBARU','PORSCHE','AUDI','BENZ','BMW','LEXUS','FORD','TOYOTA','MAZDA','HONDA','MITSUBISHI','NISSAN']

class Redisdb:
    host = '192.168.196.172'
    port = '6379'
    password = 'team1'

def creatTB():
    db = sqlite3.connect("./SUM.db")
    cur = db.cursor()
    cur.execute("drop table SUM")
    cur.execute('''CREATE TABLE SUM
             (source text, url text, title text, brand text, model text, doors text, color text,
             cc int, transmission text, equip text, mileage int, years int, location text, posttime text, price int,
             certificate text, deal int, offTime text, gasoline text)''')
    db.commit()
# creatTB()

def gen_headers():
    referers = ['tw.yahoo.com', 'www.google.com', 'http://www.msn.com/zh-tw/', 'http://www.pchome.com.tw/']
    user_agents = [
        'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
        'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)']
    headers = {'User-Agent': user_agents[randint(0, len(user_agents) - 1)],
               'Remferer': referers[randint(0, len(referers) - 1)]}
    return headers

def get_content(url):
    res = r.get(url, headers=gen_headers())
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
    #cc
    content_dict['排氣量'] = int(infoList[3].text.split('c')[0])
    #gasoline
    content_dict['汽柴油'] = formatList[1].text
    # mileage
    mileage = formatList[8].text.split('.')[0]
    if mileage == '':
        content_dict['行駛里程'] = ''
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
    #offTime   如果價格＝已收訂  將data刪除  之後再找到價格＝已收訂  就知道是下架時間
    content_dict['下架時間'] = ""
    #certificate
    match_sum = re.match('.*SUM.*', title_table)
    if match_sum:
        content_dict['認證'] = 'SUM'
    try:
        a = soup.select('.carMark.putCenter > a')[1].text
        match = re.match('關於YES認證', a)
        if match:
            content_dict['認證'] = 'YES'
    except IndexError as e:
        content_dict['認證'] = ''

    return content_dict

def add_to_sqlite(content_dict):
    conn = sqlite3.connect('./SUM.db')
    cursor = conn.cursor()
    print(content_dict)
    source = content_dict['網站']   #
    url = content_dict['連結']      #
    title = content_dict['標題']    #
    brand = content_dict['廠牌']    #
    model = content_dict['型號']    #
    doors = content_dict['車門']    #
    color = content_dict['色系']    #
    cc = content_dict['排氣量']     #
    transmission = content_dict['排擋方式']   #
    equip = content_dict['配備']             #
    mileage = content_dict['行駛里程']       #
    years = content_dict['年份']           #
    location = content_dict['所在地']      #
    posttime = content_dict['時間']       #
    price = content_dict['價格']         #
    deal = content_dict['是否售出']      #
    offTime = content_dict['下架時間']   #
    certificate = content_dict['認證']  #
    gasoline = content_dict['汽柴油']
    try:
        cursor.execute('INSERT INTO SUM VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                       (source, url, title, brand, model, doors, color, cc, transmission, equip,
                        mileage, years, location, posttime, price, certificate, deal, offTime, gasoline))
        conn.commit()
        conn.close()
    except Exception as e:
        print("add_to_sqlite : ",e)
        conn.rollback()

def check_duplicates(url):
    conn = sqlite3.connect('./SUM.db')
    cursor = conn.cursor()

    # url = content_dict['連結']

    num = list(cursor.execute('SELECT * FROM SUM WHERE url = ? ', (url,)))

    if len(num) == 0:
        return False
    else:
        return True

# def main():
#     for carName in carName_list:
#         with open('./SUM/{}.csv'.format(carName), 'r') as fr:
#             urls = fr.read().strip().split()
#             for url in urls:
#                 content_dict = get_content(url)
#                 add_to_sqlite(content_dict)

def gen_proxies():
    proxy_url = que.blpop('proxy_list')[1].decode('utf8')  # blpop
    proxy_gen = {'http': proxy_url, 'https': proxy_url}  # http   https
    print(proxy_url)
    return proxy_gen

#checkData & add_to_sql
que = redis.StrictRedis(host=Redisdb.host, port=Redisdb.port, db=0, password=Redisdb.password)#
while que.llen('SUM_list') != 0:

    logger = logging.getLogger(__name__)
    count = 3
    url = que.blpop('SUM_list')[1].decode('utf8')
    while count:
        try:
            content_dict = get_content(url)
            if not check_duplicates(url):
                add_to_sqlite(content_dict)
                break
            else:
                logger.info('same car exist pass')             #
                print('same car exist pass')
                break
        except IndexError as e:
            print(e)
            count -= 1
        except (r.exceptions.ProxyError, ConnectionRefusedError) as e:
            print(e)
            proxies = gen_proxies()
        except Exception as e:
            count -= 1
            print('url:' + url + ' count' + str(count))
    # Push to failed list
    if count == 0:
        que.lpush('mobile01_failed', url)


#query     'http://www.sum.com.tw/carinfo.php?id=403041'