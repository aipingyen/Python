"""
purpose:輸入圖片路徑辨識圖片文字,並輸出文字的文件檔案  ※tesseract要先裝好,預設在Program Files(x86) ,在Popen路徑要設絕對
                                                   ※tesseract記得第三步要設置path環境變數自動設定
                                                   
input:圖片路徑,存結果的文件檔案名稱[沒指定的話就存成當下路徑result.txt檔]

output:輸出判別文字的文件

child = subprocess.Popen(tesseract):把文字給tesseract判別,再回傳出結果

open: 檔案輸出記得utf8

"""

def image_identification(image,result="result"):

    import cv2,subprocess
    tesseract= "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe "+image+" "+result 
    child = subprocess.Popen(tesseract)
    child.wait()
    load_result = result + ".txt"
    text = open(load_result,encoding="utf8").read().strip() #讀取文字結果
    print("驗證碼為"+text) #打印