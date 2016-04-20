# coding=gbk

import pyodbc

database_client_connection = pyodbc.connect('DRIVER={SQL SERVER};SERVER=114.215.140.37;DATABASE=pachong;UID=likai;PWD=$qhz,gS*Z6S#3N"*')
# database_client_connection = pyodbc.connect('DRIVER={SQL SERVER};SERVER=LENOVO-LK\MSSQL;DATABASE=pachong;UID=sa;PWD=LiKai0129')
database_client_cursor = database_client_connection.cursor()
