#安裝selenium
#pip install selenium
#安裝chromedriver
#unzip chromedriver_linux64.zip
#sudo cp chromedriver /usr/local/bin

from selenium import webdriver
import time
import datetime
from dateutil import parser
import os
from selenium.common.exceptions import WebDriverException
import getpass

#取得使用者名稱
user = getpass.getuser()

#設定開始日期
ssday = '2010-01-01'
#轉換日期字串爲日期格式
sday = parser.parse(ssday)
#取得今天日期
today = datetime.datetime.now()
#間隔爲一天
delta = datetime.timedelta(days=1)
#結束日期
eday = today - 4*delta
#chrome driver 的默認下載資料夾
from_path = "/home/"+user+"/Downloads/relatedQueries.csv"
#最終的存檔資料夾
to_path = "google_trends/"

#下載csv
def get_csv(driver):
    #網頁延遲計時
    except_count = 0
    while True:
        #當網頁延遲超過60秒，重新整理
        if except_count > 60:
            #重新整理
            driver.refresh()
            #計時歸零
            except_count = 0
        try:
            #定位第一個按鈕
            action = driver.find_elements_by_css_selector(".widget-actions-menu.ic_googleplus_reshare.ng-isolate-scope")
            #按下第一個按鈕
            action[1].click()
            #定位下載按鈕
            csv = driver.find_elements_by_css_selector(".widget-actions-item.ng-scope.ng-isolate-scope")
            #按下下載按鈕
            csv[5].click()
            break
            #成功下載，跳出while迴圈
        #當頁面未讀取完畢時，按鈕會找不到，等待0.1秒後，重新執行while迴圈
        except IndexError:
            #等待一秒
            time.sleep(0.1)
            #延遲時間增加一秒
            except_count += 0.1

#重新命名csv檔
def rename(tA):
    while True:
        try:
            #如果csv檔案存在
            if os.path.exists(from_path):
                #重新命名，並放到最終資料夾
                os.rename(from_path, to_path + tA + ".csv")
                #成功執行，跳出迴圈
                break
            else:
                #檔案可能還沒下載完畢，等待0.1秒後，重新執行while迴圈
                time.sleep(0.1)
        except FileNotFoundError:
            #如果最終資料夾不存在的話，產生最終資料夾
            if not os.path.exists(to_path):
                os.mkdir("google_trends")

#存檔，以備重新執行時使用
def csv_save(tA):
    with open("csv_save.txt", "w") as f:
        #將目前下載的日期寫入存檔
        f.write(tA)
#讀檔
def csv_load():
    #讀檔會修改到全域變數sday，以global定義
    global sday
    #如果存檔存在
    if os.path.exists("csv_save.txt"):
        #讀取存檔
        with open("csv_save.txt", "r") as f:
            ssday = f.read()
            #將讀取的日期字串轉換爲日期格式
            sday = parser.parse(ssday)

#清理
def clean_file():
    if os.path.exists("csv_save.txt"):
        os.remove("csv_save.txt")

#執行用的main方法
def main():
    #更換日期會修改到全域變數sday，以global定義
    global sday
    #啓動 driver
    driver = webdriver.Chrome()
    #執行讀檔方法
    csv_load()
    try:
        #當目標日期小於結束日期
        while sday < eday:
            #將目標日期轉換爲字串(開始時間)
            tA = sday.strftime('%Y-%m-%d')
            #計算時間間隔
            sday += delta
            #(結束時間)
            tB = sday.strftime('%Y-%m-%d')
            #網址，每次取得一天的熱門關鍵字
            url = "https://trends.google.com.tw/trends/explore?date=" + tA + "%20" + tB +"&geo=TW"
            #連結到網址
            driver.get(url)
            time.sleep(1)
            #執行取得csv方法
            get_csv(driver)
            #執行修改名稱方法
            rename(tA)
            #執行存檔
            csv_save(tA)
    #當driver 不正常結束
    except WebDriverException:
        time.sleep(10)
        #重新執行main方法
        main()
    #關閉driver
    driver.close()
#執行main方法
main()



