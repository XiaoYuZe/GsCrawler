# coding=gbk
from DBClient import *
from logger import *
import SysConfig


class UnknownColumnException(Exception):
    def __init__(self, code, column_name):
        self.unknown_column = column_name
        sql = u"insert into UnknownColumn values ('%s','%s','%s',getDate(),-1)" % (SysConfig.province, code, column_name)
        database_client_cursor.execute(sql)
        database_client_connection.commit()
        logging.info(u'未知列名：%s' % self.unknown_column)
        logging.shutdown()

    def __str__(self):
        return u'未知列名：%s' % self.unknown_column