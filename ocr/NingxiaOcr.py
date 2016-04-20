import cv2
import numpy as np
import tesseract
import os
import os.path
import sys
api = tesseract.TessBaseAPI()
api.Init('.', 'eng', tesseract.OEM_DEFAULT)
api.SetVariable('tesseract_char_whitelist', '1234567890+')
api.SetVariable('tesseract_char_blacklist', 'abcdefghijklmnopqrstuvwxtzABCDEFGHIJKLMNOPQRSTUVWXYZ')

img = cv2.imread(sys.argv[1],1)
# img = cv2.imread(r"C:\Users\kai.li\pycharmprojects\GsCrawler\data\ning_30.jpg",1)
b,g,r = cv2.split(img)
for i in range(8, 26):
    for j in range(20, 85):
        if g[i][j] > 100 and r[i][j] > 100:
            b[i][j] = 255
            g[i][j] = 255
            r[i][j] = 255

merged = cv2.merge([b,g,r])
img_1 = merged[8:26,21:34]  # first number
img_2 = merged[12:26,47:61]  # operator
img_3 = merged[8:26,71:84]  # second number


list = [img_1, img_2, img_3]
def img_denoise(src):
    gray = cv2.cvtColor(src,cv2.COLOR_BGR2GRAY)
    (T,thresh) = cv2.threshold(gray,200,255,cv2.THRESH_BINARY)
    #cv2.imshow("0",thresh)
    #cv2.waitKey(0)
    return thresh
   
numbers = []
for i in range (0,3):
    im = img_denoise(list[i])
    cv2.imwrite("1.jpg",im)
    mImgFile = "1.jpg"
    mBuffer = open(mImgFile,"rb").read()      
    result = tesseract.ProcessPagesBuffer(mBuffer,len(mBuffer),api) 
    result = result.decode("UTF-8",'ignore')
    result = result.encode("GBK", "ignore")
    # res = result.rstrip()
    res = result.split('\n')[0].strip()
    numbers.append(res)
        

str1 = ['-','+','-+','+-']
str2 = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
if numbers[1] == 'X': 
    if numbers[0] in str2 or numbers[2] in str2:
      print "can't compute numbers"
    else:
      # print numbers
      re = int(numbers[0])*int(numbers[2])
    print re
if numbers[1] in str1 :
    if numbers[0] in str2 or numbers[2] in str2:
        print "can't compute numbers"
    else:
        re = int(numbers[0]) + int(numbers[2])
        print re


mImgFile = '1.jpg'
if os.path.exists(mImgFile):
        os.remove(mImgFile)
else:
    print 'no such file:%s' %mImgFile

#root = "D:\python\NingXia\images"
#for parent,dirnames,filenames in os.walk(root):
#    for filename in filenames:
#        pa = os.path.join(parent,filename)
#        print filename
#        compute(pa)