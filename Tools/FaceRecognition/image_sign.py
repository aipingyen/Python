"""
purpose:臉部辨識認證登入

input:存放資料夾路徑(要存在),存放辨識用圖片名稱(隨便取個),登入用暫存圖片名稱 (隨便取個) 

output:回傳一個符合指數告知相似度


自訂方法:makeFace()

ex:face_id("floder","recogface","logingace")

"""

def face_id(save_path,recogface,logingace):
    
    import cv2,os,math,operator
    from PIL import Image
    from functools import reduce

    casc_path = "C:\\Users\\abcdq\\Anaconda3\\pkgs\\opencv3-3.1.0-py35_0\\Library\\etc\\haarcascades\\haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(casc_path) #連線演算法,建立辨識物件
    recogname = save_path+"\\"+recogface+".jpg" # 使用者臉部檔案
    loginname = save_path+"\\"+logingace+".jpg" #登入者臉部檔案
    os.system("cls")#清除螢幕
    if(os.path.exists(recogname)): #如果使用者臉部檔案已經存在
        msg = "按下任意健建立登入者臉譜。\n 攝影機開啟後按「z」拍照比對!"
        makeFace(loginname,msg,"") #建立登入者臉部檔案

        #以下段落為開啟兩張圖片並比對相似度
        pic1 = Image.open(recogname) #開啟使用者臉部檔案
        pic2 = Image.open(loginname) #開啟登入者臉部檔案
        h1 = pic1.histogram() #計算差異程度
        h2 = pic2.histogram()
        diff = math.sqrt(reduce(operator.add,list(map(lambda a,b:(a-b)**2,h1,h2)))/len(h1)) #產出diff差異性
        if(diff<=100): #若差異在100內視為通過驗證 , 此為作者找多朋友測試後設定的數值，可照需求再做調整
            print("通過驗證，歡迎使用本系統！ 符合指數=%4.2f"%diff)
        else:
            print("臉譜不正確，無法使用本系統！ 符合指數=%4.2f"%diff)

    else: #如果使用者臉部檔案不存在
        msg = "案任意鍵建立使用者臉譜。\n 攝影機開啟後按「z」拍照！\n"
        endstr = "使用者臉譜建立完成！"
        makeFace(recogname,msg,endstr) #建立使用者臉部檔案
        
        
        
"""
purpose:開啟攝影機並擷取畫面一張臉孔並存進路徑檔案          @支援face_id()

input:欲新增檔案之路徑,程式碼開跑前訊息,程式碼結束後訊息

output:存圖片進指定路徑,打印出開始與成功訊息

faceCascade.detectMultiScale()演算法擷取畫面的臉孔照片 但這裡只取(第)一張

"""

def makeFace(facename,msg,endstr):
    
    import numpy
    import cv2
    from PIL import Image
    
    casc_path = "C:\\Users\\abcdq\\Anaconda3\\pkgs\\opencv3-3.1.0-py35_0\\Library\\etc\\haarcascades\\haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(casc_path) #連線演算法,建立辨識物件
    
    print(msg) #顯示提示訊息  → "按下任意健建立登入者臉譜...
    cv2.namedWindow("frame")
    cv2.waitKey(0)
    cap = cv2.VideoCapture(0) #開啟攝影機
    while(cap.isOpened()): #攝影機為開啟狀態
        ret,img = cap.read() #回傳兩個參數 前者結果碼(成功or失敗) 後者圖片檔
        if ret == True:  # 讀取成功
            cv2.imshow("frame",img) #顯示影像
            k = cv2.waitKey(100) #每0.1秒讀一次鍵盤 看有無按下鍵 k 
            
            
            if k == ord("z") or k == ord("Z"): #使用z or Z
                
                cv2.imwrite(facename,img) #存檔
                image = cv2.imread(facename) #讀取做臉部辨識
                faces = faceCascade.detectMultiScale(image,scaleFactor=1.1,minNeighbors=5,minSize=(30,30),flags= cv2.CASCADE_SCALE_IMAGE)
                (x, y, w, h) =(faces[0][0], faces[0][1], faces[0][2], faces[0][3]) #只取第一張臉部

                image1 = Image.open(facename).crop((x,y,x+w,y+h)) #擷取臉部
                image1 = image1.resize((200,200),Image.ANTIALIAS) #轉為解析度 200x200
                image1.save(facename) #存檔
                break
            
    cap.release() #關閉式影機,釋放資源
    cv2.destroyAllWindows()
    print(endstr) #顯示結束字串
    return