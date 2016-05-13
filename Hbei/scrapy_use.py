#!/usr/bin/python
# coding:gbk
import os
import sys
from selenium import webdriver
import time

print 'startTIME: '+str(time.ctime())

driver = webdriver.PhantomJS(executable_path="D:\\phantomjs-2.0.0-windows\\bin\\phantomjs.exe")
driver.get('http://www.baidu.com')
driver.find_element_by_id("kw").send_keys(u"程序猿")
print driver.find_element_by_id('su').get_attribute('value')
driver.find_element_by_id('su').click()
time.sleep(0.5)
print os.getcwd()
print sys.path[0]
for i in range(100):
    i += 1
    a = driver.find_element_by_xpath('html/body').text.encode('gbk', 'ignore')
    c = int(driver.find_element_by_xpath("//div[@id = 'page']/strong").text)
    f = open('D://testjbbs.txt','a')
    f.write('\n'+'The '+str(c)+' Page'+'\n'+a)
    f.close()

    print i, c
    driver.get_screenshot_as_file('D://'+'ta'+str(i)+'.png')
    driver.find_elements_by_xpath("//div[@id = 'page']/a")[-1].click()
    time.sleep(1)
    if i != c:
        print 'asyn or the max content'
        break

print 'overTIME: '+str(time.ctime())
driver.close()