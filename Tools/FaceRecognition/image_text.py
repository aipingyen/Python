"""
purpose:輸入圖片並在上面寫字

input:圖片路徑,寫上文字

output:一張寫上字的圖片

ex:text_image("test01.jpg","AAAA")


"""

def text_image(image_path,text):
    
    import cv2
    import numpy
    image = cv2.imread(image_path,1)
    pts = numpy.array([[20,60],[300,280],[150,200]],numpy.int32)
    cv2.putText(image,text,(350,300),cv2.FONT_HERSHEY_SIMPLEX,4,(255,0,0),2)
    cv2.namedWindow("Image",cv2.WINDOW_AUTOSIZE)

    cv2.imshow("Image",image)
    cv2.waitKey(3000)
    #cv2.imwrite("test01.jpg",image,[int(cv2.IMWRITE_PNG_COMPRESSION),3])#[int(cv2.IMWRITE_JPEG_QUALITY),70]
    cv2.destroyWindow("Image") #記得刪除