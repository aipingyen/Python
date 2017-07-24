import requests as r
from bs4 import BeautifulSoup
import time
from  collections import Counter
import re


#get all innerLinks
def get_innerLinks(url, HEADER, lock, i, link_path):
    count = 5
    while count:
        try:
            res = r.get(url, headers=HEADER)
            soup = BeautifulSoup(res.text,'lxml')
            page_links = soup.select('li.title > a')
            if res.status_code == 200 and len(page_links):
                link_list = [link['href'] for link in page_links]
                print('Get {} links from page {}'.format(len(link_list), i))
                with lock:
                    with open(link_path,'a') as fa:
                        fa.write('\n'.join(link_list))
                        fa.write('\n')
                break
            else:
                print('Cannot retrieve links from page {}'.format(i))
                count -= 1
                time.sleep(0.87)
        except Exception as e:
            print('Cannot retrieve innerlink from page{} Retry: {} Error: {}'.format(i, 6-count, e))
            count -= 1
            time.sleep(0.87)

    if count == 0:
        print('[Error] Page {} failed'.format(i))

#grab content and wordCounter
def grab_content(link, HEADER, lock, idx):
    global wc
    count = 5

    while count:
        try:
            res2 = r.get(link, headers=HEADER)
            if res2.status_code == 200:
                soup2 = BeautifulSoup(res2.text,'lxml')
                content = soup2.select_one('div.job-detail-box > dl')
                text = content.text.replace('\n', '')

                content2 = soup2.select_one('div.JobDescription > p')
                text2 = content2.text.replace('\n', '')

                word = re.findall('objective c|visual basic|[A-Za-z]+[+#]*', text, re.IGNORECASE)
                word2 = re.findall('objective c|visual basic|[A-Za-z]+[+#]*', text2, re.IGNORECASE)
                word_count = word + word2
                pure_word = list(set(word_count))
                print(pure_word)
                with lock:
                    for lan in pure_word:
                        if lan in wc:
                            wc[lan] += 1
                        else:
                            wc[lan] = 1
                print(wc.most_common())
                print(idx)

                if idx % 200 == 0:
                    print('{} have been completed'.format(idx))
                break
            else:
                print('Cannot retrieve No:{} content Retry: {}'.format(idx, 6-count))
                time.sleep(1)
                count -= 1
        except Exception as e:
            print('Cannot retrieve No:{} content Retry: {} Error:{}'.format(idx, 6 - count, e))
            time.sleep(1)
            count -= 1
    if count == 0:
        print('Retrieve contetn failed No: {} '.format(idx))

import requests as r
from bs4 import BeautifulSoup
from lib.toolbox import gen_header
import threading
import time

Host = 'https://www.518.com.tw'
link_path = './518_links.csv'
thread_list = []
thread_list2 = []
alinks = []
wc = Counter()
lock = threading.Lock()

#get HEADER
header_str = 'User-Agent:Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
HEADER = gen_header(header_str)
# print(HEADER)

#get pages
url = Host+'/job-index.html?ad=&aa=&ab=2032001%2C2032002%2C&ac=&am=1&i=1&ae=&af=&ag=&ah=&ai=&aj=&ak=&ak_min=&ak_max=&al=&an=&ao=&ap=&aq=&ar=&as=&at=&au='
res = r.get(url,headers=HEADER)
soup = BeautifulSoup(res.text,'lxml')
pages = int(soup.select_one('.pagecountnum > span').text.split('/')[1])+1
# print(pages)

#
"""
for i in range(1,pages):
    url = Host + '/job-index-P-{}.html?i=1&am=1&ab=2032001,2032002,'.format(i)
    th = threading.Thread(target=get_innerLinks, args=(url, HEADER, lock, i, link_path))
    th.start()
    time.sleep(0.2)
    thread_list.append(th)
else:
    print('[Debug] All links are saved')
for thread in thread_list:
    thread.join()
"""
#
with open('518_links.csv', 'r') as fr:
    alinks = fr.read().strip().split('\n')
print(len(alinks))
print(alinks)

for idx, link in enumerate(alinks):
    th2 = threading.Thread(target=grab_content, args=(link, HEADER, lock, idx))
    th2.start()
    time.sleep(1)
    thread_list2.append(th2)
for thread2 in thread_list2:
    thread2.join()

with open('./518.csv', 'w') as fw2:
    for lang, counts in wc.most_common():
        fw2.write('{},{}\n'.format(lang,counts))