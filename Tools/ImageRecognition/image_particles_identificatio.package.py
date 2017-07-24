"""
purpose:許多辨識碼會用顆粒去混淆判別,此判別方法以此為設計 ※tesseract要先裝好,預設在Program Files(x86) ,在Popen路徑要設絕對
                                                      ※tesseract記得第三步要設置path環境變數自動設定

input:輸入圖片路徑,預存結果圖片名稱-記得輸入jpg[預設有存],預存結果之文件[沒指定就存成當下目錄result.txt檔]

outpu:一個將判別圖形的視窗,一個處理過的圖片辨識,判別結果text

cv2.dilate:Opencv的方法，將圖片中的白點膨脹, iterations=膨脹次數

cv2.cvtColor() :第二參數其他旗標可再研究

cv2.threshold() :第二參數其他旗標可再研究

當下路徑會多個處理過的圖片辨識檔與判別text

※cv2.threshold() 回傳第二個值才數圖片→所以傳回值要打inv[1]才有圖,   第一個應該是回傳是否成功的參數(retval)

"""

def image_particles_identification(image,save_image="save_identification.jpg",result="result_text_id.txt"):

    import cv2,subprocess
    img = cv2.imread(image)
    cv2.namedWindow("Image")
    cv2.imshow("Image",img) #顯示圖片
    cv2.waitKey(0)
    cv2.destroyWindow("Image")
    
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY) #顏色轉程灰階
    inv = cv2.threshold(gray,150,255,cv2.THRESH_BINARY_INV) #圖型轉為黑白前輸入圖片必須為灰階

    #以下迴圈是把外圈雜點去掉,詳細請看書籍
    for i in range(len(inv[1])):
        for j in range(len(inv[1][i])):
            if inv[1][i][j] ==255:
                count = 0
                for k in range(-2,3):
                    for l in range(-2,3):
                        try:
                            if inv[1][i+k][j+l] == 255:
                                count += 1
                        except IndexError:
                            pass
                if count <= 6: #周圍少於等於六個白點
                    inv[1][i][j] = 0 #將白點去除


    dilation = cv2.dilate(inv[1],(8,8),iterations = 1 ) #圖型加粗 
    cv2.imwrite(save_image,dilation) #存檔
    
    popen_code = "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe "+save_image+" "+result
    child = subprocess.Popen(popen_code) #OCR判別
    child.wait()
    result_txt = result + ".txt"
    text = open(result_txt,encoding="utf8").read().strip()
    print("驗證碼為"+text)