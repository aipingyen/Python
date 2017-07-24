from selenium import webdriver
import time
import datetime
from dateutil import parser
import os
from selenium.common.exceptions import WebDriverException
import getpass
user = getpass.getuser()

ssday = '2010-01-01'
sday = parser.parse(ssday)
today = datetime.datetime.now()
delta = datetime.timedelta(days=1)
eday = today - 4*delta
from_path = "/home/"+user+"/Downloads/relatedQueries.csv"
to_path = "google_trends/"

def get_csv(driver):
    except_count = 0
    while True:
        #if page block over 60 seconds, refresh it
        if except_count > 60:
            driver.refresh()
            except_count = 0
        try:
            action = driver.find_elements_by_css_selector(".widget-actions-menu.ic_googleplus_reshare.ng-isolate-scope")
            action[1].click()
            csv = driver.find_elements_by_css_selector(".widget-actions-item.ng-scope.ng-isolate-scope")
            csv[5].click()
            break
        except IndexError:
            time.sleep(0.1)
            except_count += 0.1

def rename(tA):
    while True:
        try:
            if os.path.exists(from_path):
                os.rename(from_path, to_path + tA + ".csv")
                break
            else:
                time.sleep(0.1)
        except FileNotFoundError:
            #save path may not exists
            if not os.path.exists(to_path):
                os.mkdir("google_trends")

def csv_save(tA):
    with open("csv_save.txt", "w") as f:
        f.write(tA)

def csv_load():
    global sday
    if os.path.exists("csv_save.txt"):
        with open("csv_save.txt", "r") as f:
            ssday = f.read()
            sday = parser.parse(ssday)

def main():
    global sday
    driver = webdriver.Chrome()
    csv_load()
    try:
        while sday < eday:
            tA = sday.strftime('%Y-%m-%d')
            sday += delta
            tB = sday.strftime('%Y-%m-%d')
            url = "https://trends.google.com.tw/trends/explore?date=" + tA + "%20" + tB +"&geo=TW"
            driver.get(url)
            time.sleep(1)
            get_csv(driver)
            rename(tA)
            csv_save(tA)
    #if driver crash, restart
    except WebDriverException:
        time.sleep(10)
        main()
    driver.close()

main()



