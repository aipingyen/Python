import requests
from bs4 import BeautifulSoup
from collections import Counter
import re
import threading
import time

counter = Counter()

https = 'https:'
url = "https://www.1111.com.tw/job-bank/job-index.asp?si=1&ks=程式&fs=0&page="

lans = ['R','C','C++','C#', 'JAVA', 'JAVASCRIPT', 'PHP', 'PYTHON', 'RUBY', 'GO', 'VISUAL BASIC .NET', 'DELPHI/OBJECT PASCAL',
        'PERL', 'SWIFT', 'ASSEMBLY LANGUAGE', 'VISUAL BASIC', 'MATLAB', 'PL/SQL', 'OBJECTIVE-C', 'SCRATCH']

url1 = url + '1'
r1 = requests.get(url1)
soup = BeautifulSoup(r1.text, 'lxml')
pstring = soup.select_one('.pagedata')
match = re.match('.*/\s(\d+)\s.*', pstring.text)
total = int(match.group(1))

#get job's links on every page
def getLinks(n):
    numUrl = url+str(n)
    r = requests.get(numUrl)
    soup = BeautifulSoup(r.text, 'lxml')
    joblinks = soup.select('.jbInfoin > h3 > a')
    links = []
    for joblink in joblinks:
        link = https+joblink['href']
        links.append(link)
    return links

def getContent(jobUrl):
    list = []
    r = requests.get(jobUrl)
    soup = BeautifulSoup(r.text, 'lxml')

    #find need numbers
    mans = 1
    tcontent = soup.select('dl.dataList > dd')
    for tag in tcontent:
        match = re.match(r'(\d+)~?(\d+)?人', tag.text)
        if match:
            n1 = match.group(1)
            n2 = match.group(2)
            if n2 == None:
                mans = int(n1)
            else:
                mans = (int(n1) + int(n2)) // 2
    list.append(mans)
    #find need numbers end

    #get every string on job's page
    content = soup.select('dl.dataList > dd')
    for tag in content:
        finds = re.findall(r'[a-z|A-Z]+#?\+?\+?', tag.text)
        if finds:
            for find in finds:
                if find in lans and find not in list:
                    find = find.upper()
                    list.append(find)
    return list

#set thread for every search page
class mythread(threading.Thread):
    def __init__(self, links, lock):
        threading.Thread.__init__(self)
        self.links = links
        self.lock = lock
    def run(self):
        global counter
        for link in self.links:
            list = getContent(link)
            self.lock.acquire()
            for l in range(1, len(list)):
                if list[l] in counter:
                    #list[0] is need numbers
                    counter[list[l]] += list[0]
                else:
                    counter[list[l]] = list[0]
            self.lock.release()

#counting in main method
def main():
    stime = time.time()
    global total
    threads = []
    lock = threading.Lock()
    for page in range(1,total+1):
        links = getLinks(page)
        thread = mythread(links, lock)
        threads.append(thread)
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(counter)
    etime = time.time()
    print("usetime = %.1f min" % ((etime - stime)/60))

#start
main()

#20170502 result:Counter({'Java': 706, 'C#': 490, 'JavaScript': 377, 'PHP': 318, 'C': 267, 'C++': 215, 'JPython': 100, 'Ruby': 25, 'R': 14, 'Go': 3})
#20170503 result:Counter({'Java': 1437, 'C#': 944, 'JavaScript': 745, 'PHP': 623, 'C': 567, 'C++': 501, 'JPython': 183, 'Ruby': 46, 'R': 28, 'Go': 4})
#20170508 result:Counter({'C#': 932, 'JAVA': 723, 'C': 581, 'PHP': 579, 'C++': 502, 'R': 27, 'JAVASCRIPT': 10, 'SWIFT': 3, 'MATLAB': 2, 'GO': 2})
