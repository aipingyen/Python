"""
purpose:放進圖片進行臉部辨識,並擷取所有辨識到的臉部存進指定資料夾,辨識建立圖片視窗並在右下註記抓取數

input:欲辨識圖片之路徑,存放擷取辨識臉部圖之資料夾路徑,[臉部辨識指定演算法]

output:彈出有抓取臉部之圖之視窗,並標記抓取數量；存放擷取臉部圖至指定資料夾


casc_path為演算法指定預設路徑,如需要更改可在第三格寫入欲使用演算法之路徑

casc_path = "C:\\Users\\abcdq\\Anaconda3\\pkgs\\opencv3-3.1.0-py35_0
\\Library\\etc\\haarcascades\\haarcascade_frontalface_default.xml"

cv2.rectangle:左下角文字區塊背景

cv2.putText:左下角顯示抓到多少臉部之文字

自訂方法:save_faces()

ex:catch_face("test01.jpg","media")

"""
def catch_face(picture_path,folder_name,casc_path = "C:\\Users\\abcdq\\Anaconda3\\pkgs\\opencv3-3.1.0-py35_0\\Library\\etc\\haarcascades\\haarcascade_frontalface_default.xml"):
    
    import cv2
    import numpy
    from PIL import Image
    
    #路徑取得演算法
    faceCascade = cv2.CascadeClassifier(casc_path) #建立辨識物件-演算法
    imagename = cv2.imread(picture_path) #圖片路徑

    faces = faceCascade.detectMultiScale(imagename,scaleFactor=1.1,minNeighbors=9,minSize=(30,30),flags =cv2.CASCADE_SCALE_IMAGE)
    #faces 辨識結果，臉部位置的array
    """
    scaleFactor 辨識原理是系統已不同區塊大小對圖片掃描進行特徵對，此參數設定區塊的改變倍數，如無特別需求一般設1.1
    ninNeighbors 此為控制誤檢率參數 系統已不同區塊進行特徵比對時，在不同區塊可能會多次成功取得特徵，成功取得
                成功取得特徵須達到此參數設地值才算辨識成功，預設值為3           
    minSize,maxSize 為參數設定最小,最大辨識區塊

    flags 此參數設定檢定模式，可能值有:
    1.cv2.CV_HAAR_SCALE_IMAGE :按比例正常檢測
    2.cv2.CV_HAAR_DO_CANNY_PRUNING :利用Canny 邊緣檢測器來排除依些邊緣很少或很多的圖像區塊
    3.cv2.CV_HAAR_FIND_BIGGEST_OBJECT:只檢定最大的物體
    4.cv2.CV_HARR_DO_ROUGH_SEARCH:只做粗略檢測
    """
    cv2.rectangle(imagename, (10,imagename.shape[0]-20),(110,imagename.shape[0]),(0,0,0),-1)
    #文字背景區塊
    cv2.putText(imagename,"Find"+str(len(faces))+"faces!",(10,imagename.shape[0]-5),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),2)
    #文字顯示有多少臉辨識出來

    save_faces(faces,imagename,picture_path,folder_name) #1臉位置判別array 2圖片讀取檔案 3檔名路徑 4存取資料夾
    #自訂方法,把辨識出臉來的區塊擷取成圖片存進資料夾

    cv2.namedWindow("facedetect") #開啟視窗
    cv2.imshow("facedetect",imagename) #繪製好的圖片放進視窗
    cv2.waitKey(0) #等待0秒
    cv2.destroyWindow("facedetect") #關閉視窗
    
"""
purpose:抓出辨識臉孔並存進資料夾 & 為照片上每張抓出辨識臉孔繪製矩陣      @支援catch_face()

input:辨識出臉孔的位置群,正繪製的圖片檔案,欲辨識圖片的路徑,要存放擷取圖的資料夾路徑

ouput:圖片繪製出辨識出的框,並擷取存放進指定資料夾

image1.crop:擷取辨識出的臉孔

image2.resize:限制繪製框的大小

rectangle:繪製綠色的矩陣在圖片上

"""
def save_faces(faces,imagename,picture_path,folder_name):
    
    import cv2
    import numpy
    from PIL import Image
    count = 1
    for (x,y,w,h) in faces: 
        cv2.rectangle(imagename,(x,y),(x+w,y+h),(128,255,0),2)#繪製矩陣,綠色
        filename = folder_name+"\\face" +str(count)+".jpg" #指定資料夾的圖片路徑
        image1 = Image.open(picture_path)
        image2 = image1.crop((x,y,x+w,y+h))#左上角xy座標,右下角座標wh座標
        image3 = image2.resize((200,200), Image.ANTIALIAS)
        """
        resize 不同圖片擷取大小不一，為了方便比對把圖形調整為固定大小 200x200
        參數二維控制圖形品質：
        lmage.NEAREST(最低品質,預設),lmage.BILINEAR(雙線性取樣算法)
        ,lmage.BICUBIC(三次樣條取樣算法),lmage.ANTIALIAS(最高品質)
        
        """
        image3.save(filename) #(存進資料夾)
        count += 1 #每辨識一張的結束加一