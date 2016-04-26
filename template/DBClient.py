# coding=gbk

import pyodbc

database_client_connection = pyodbc.connect('DRIVER={SQL SERVER};SERVER=180.153.243.118;DATABASE=pachong;UID=zhangxiaogang;PWD=29*YIH&Osajf>')
# database_client_connection = pyodbc.connect('DRIVER={SQL SERVER};SERVER=LENOVO-LK\MSSQL;DATABASE=pachong;UID=sa;PWD=LiKai0129')
database_client_cursor = database_client_connection.cursor()
