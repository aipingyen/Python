import requests
from bs4 import BeautifulSoup
import re
from collections import Counter

counter = Counter()

lans = ['R','C','C＋＋','C#', 'JAVA', 'JAVASCRIPT', 'PHP', 'PYTHON', 'RUBY', 'GO', 'VISUAL BASIC .NET', 'DELPHI/OBJECT PASCAL',
        'PERL', 'SWIFT', 'ASSEMBLY LANGUAGE', 'VISUAL BASIC', 'MATLAB', 'PL/SQL', 'OBJECTIVE-C', 'SCRATCH']

def getPages():
    pages = []
    n = 1
    while True:
        url = "https://learn.104.com.tw/learning/course/classlist.action?page=" + str(n) + "&key=%E7%A8%8B%E5%BC%8F&cate=&area=&days=&timeslot=&period=&ctype=&sortType=0"
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'lxml')
        lessons = soup.select('div.classlist_cont.line_bottom.focus')
        if lessons == []:
            break
        pages.append(url)
        n += 1
    return pages

def getContent(url):
    global counter
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    lessons = soup.select('div.classlist_cont.line_bottom.focus')
    for lesson in lessons:
        types = []
        titles = lesson.select('a.classname')
        for title in titles:
            finds = re.findall(r'[a-z|A-Z]+#?＋?＋?', title.text)
            if finds:
                for find in finds:
                    find = find.upper()
                    if find in lans:
                        types.append(find)

        info = lesson.select_one('div.coursetype')
        match = re.match(r'.*時數：(\d+)小時.*', info.text)
        if match:
            hour = int(match.group(1))
            if types != []:
                for type in types:
                    if type in counter:
                        counter[type] += hour
                    else:
                        counter[type] = hour

def main():
    global counter
    for page in getPages():
        getContent(page)
    counter = counter.most_common()
    print(counter)

main()

#20170508 result:[('JAVA', 93043), ('C', 1616), ('C＋＋', 1067), ('JAVASCRIPT', 402), ('C#', 306), ('SWIFT', 285), ('PYTHON', 272), ('R', 90), ('PHP', 30), ('MATLAB', 30), ('SCRATCH', 10)]