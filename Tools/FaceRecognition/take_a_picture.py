"""
purpose:開啟內視鏡頭拍下來存成照片    ※按z or Z 拍取照片

input:要放置資料夾路徑,要命名的檔案名稱

output:拍好的jpg檔案

cv2.VideoCapture(0):開啟鏡頭 筆電內鍵鏡頭為0

k = cv2.waitKey(100):0.1檢查一次，看有無輸入進按鍵(ASCII)碼

ord("z"):轉出ASCII編碼

ex:image_save("media","catch")

"""
def image_save(floder,image_name): 

    import cv2
    cv2.namedWindow("save_image")
    cap = cv2.VideoCapture(0)  #開啟攝影機，通常內部數值是0 其他依次為1、2
    while(cap.isOpened()):  #只要攝影機為開啟狀態就執行此無窮迴圈，通常等待案件須以無窮迴圈簡直使用者是否按鍵
        ret ,img = cap.read() #讀取影像
        if ret == True:  #如果讀取成功就在視窗顯示
            cv2.imshow("save_image",img)
            k = cv2.waitKey(100) #每隔0.1秒檢查一次是否按鍵,並回傳按鍵的ASCII碼
            if k == ord("z") or k == ord("Z"): #使用者可能輸入z或是Z 都要檢查
                path = floder + "\\" +image_name +".jpg"
                cv2.imwrite(path,img)
                break  #有輸入zZ就儲存
    cap.release() #關閉攝影機,釋放資源
    cv2.waitKey(0)
    cv2.destroyWindow("save_image")