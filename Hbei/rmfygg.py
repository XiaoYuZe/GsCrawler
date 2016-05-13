#!/usr/bin/env python
# -*- coding='utf-8' -*-
import sys
import requests
import selenium
import json
import os
import pyodbc
from bs4 import BeautifulSoup
import threading
import datetime
import MySQLdb

reload(sys)
sys.setdefaultencoding('utf8')
# target page   http://rmfygg.court.gov.cn/
#--server connect ,Database table has established
cnnt = MySQLdb.connect(host='210.16.191.150',port=3306,user='zhangxiaogang',passwd='gangxiaozhang',db='court_notice',)
cursor = cnnt.cursor()

f = open('D:\zhangxig\python_spider\log\\'+datetime.datetime.now().strftime('%Y-%m-%d %H%M%S')+'.txt','w')
headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.82 Safari/537.36"}

def fygg_func(b_n,e_n):

    #error count for ValueError:'No JSON object could be decoded'
    err_count = 0

    # start spidering in the range loops
    for n in range(b_n,e_n):
		params={
				"start":n,
				"limit":16,
				"wd":"rmfybulletin",
				"list[0]":"bltntype:"+''
				}
		r = requests.post("http://rmfygg.court.gov.cn/psca/lgnot/solr/searchBulletinInterface.do?callback=?", data=params)


		# ValueError status release try
		try:
			content_dict = json.loads(r.content[2:-1])['objs']
			#print content_dict
			#--break condition!
			if content_dict != []:
				for k in range(len(content_dict)):
				    #print k
					content_fin = json.loads(r.content[2:-1])['objs'][k]#.encode('utf8')
					link_id = content_fin['id']
					crt_name = content_fin['courtcode']
					rel_prn = content_fin['party2']
					pub_date = content_fin['publishdate']
					blt_type = content_fin['bltntypename']
					blt_content = content_fin['content']
					sql = "INSERT INTO bltin VALUES ('%s','%s','%s','%s','%s','%s')" %(link_id, crt_name, rel_prn, pub_date, blt_type, blt_content)
					# try for if double data
					try:
						cnnt.execute(sql)
						cnnt.commit()
						f.write('~~'+'NEW'+'~~This is '+str(n)+' page~~'+str(k+1)+' line'+'link'+str(link_id)+"is NEW!"+' Saved '+'~~~~~~~~~~')
						print '~~'+'NEW'+'~~This is '+str(n)+' page~~'+str(k+1)+' line'+'link'+str(link_id)+"is NEW!"+' Saved '+'~~~~~~~~~~'
					except:
						f.write('~~'+'OLD'+'~~This is '+str(n)+' page~~'+str(k+1)+'~~~'+str(link_id)+' already exist'+'~~~~~~')
						print '~~'+'OLD'+'~~This is '+str(n)+' page~~'+str(k+1)+'~~~'+str(link_id)+' already exist'+'~~~~~~~~~'
						continue
					# print k+1,crt_name,rel_prn,pub_date,blt_type,blt_content
					# print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~This is '+ str(n) + ' page~~~~~~~~~~~' +str(k+1)+ '~~~~~~~~~~~~'+str(link_id)+'already exist'+'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
			else:
				f.write('Home Total is '+str(n)+ ' page')
				print 'Home Total is '+str(n)+ ' page'
				break
		except:
			err_count +=1
			f.write('Error Unexpected times? '+str(err_count))
			print 'Error Unexpected times? '+str(err_count)
			continue

tlist = []
t1 = threading.Thread(target=fygg_func,args=(1,5000))
tlist.append(t1)
t2 = threading.Thread(target=fygg_func,args=(5001,10000))
tlist.append(t2)
t3 = threading.Thread(target=fygg_func,args=(10001,15000))
tlist.append(t3)
t4 = threading.Thread(target=fygg_func,args=(15001,99999))
tlist.append(t4)

for i in tlist:
    i.setDaemon(True)
    i.start()
i.join()
f.write('Now is %s' %datetime.datetime.now())
print 'Now is %s' %datetime.datetime.now()
f.close()




