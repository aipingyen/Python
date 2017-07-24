import os
import re

#存檔資料夾
folder = "google_trends"

#寫入流行csv
def write_pop(day, pop):
    #去除多餘字
    pop = pop.replace("類別：所有類別\nTOP\n","")
    #處理後的字串
    pop_re = ""
    #每項資料以空行做分隔
    for c in pop.split("\n"):
        #每項資料加入日期
        pop_re += day + "," + c + "\n"
    with open("pop_save.csv", "a") as f:
        #寫入存檔
        f.write(pop_re)

#寫入關鍵字csv
def write_up(day, up):
    #去除多餘字
    up = up.replace("RISING\n", "")
    up = up.replace("%", "")
    up = up.replace("\"", "")
    #處理後的字串
    up_re = ""
    # 每項資料以空行做分隔
    for c in up.split("\n"):
        #match資料格式
        match = re.match("(.*),飆升", c)
        match2 = re.match("(.*),\+(\d+),(\d{3})", c)
        #如果比對match成功
        if match:
            #加入日期並重組
            up_re += day + "," + match.group(1) + ",5000" + "\n"
        #如果比對match2成功
        elif match2:
            # 加入日期並重組
            up_re += day + "," + match2.group(1) + "," + match2.group(2) + match2.group(3) + "\n"
        else:
            match3 = re.match("(.*),\+(\d{3})", c)
            # 如果比對match3成功
            if match3:
                # 加入日期並重組
                up_re += day + "," + match3.group(1) + "," + match3.group(2) + "\n"
    with open("up_save.csv", "a") as f:
        # 寫入存檔
        f.write(up_re)

#確認檔案名稱
def filenames():
    #檔名陣列
    filenames = []
    #指定資料夾內的每個檔名
    for filename in os.listdir(folder):
        #加入檔名陣列
        filenames.append(filename)
    #排序檔名陣列
    filenames.sort()
    #回傳檔名陣列
    return filenames

#轉檔
def transform_file(filename):
    #路徑與檔名
    file_path = folder + "/" + filename
    with open(file_path, "r") as f:
        #日期就是檔名
        day = filename.split(".csv")[0]
        #檔案前半是流行，後半是關鍵字，以兩個空行分隔
        csvs = f.read().split("\n\n")
        #前半
        pop = csvs[0]
        #後半
        up = csvs[1]
        #寫入流行csv
        write_pop(day,pop)
        #寫入關鍵字csv
        write_up(day,up)

#執行用的main方法
def main():
    #取出檔名陣列的每個檔名
    for filename in filenames():
        #轉檔
        transform_file(filename)

#執行main方法
main()