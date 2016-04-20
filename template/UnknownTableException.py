# coding=gbk
from DBClient import *
from logger import *
import SysConfig


class UnknownTableException(Exception):
    def __init__(self, code, table_name):
        self.unknown_table = table_name
        sql = u"insert into UnknownTable values ('%s','%s','%s',getDate(),-1)" % (SysConfig.province, code, table_name)
        database_client_cursor.execute(sql)
        database_client_connection.commit()
        logging.info(u'未知表名：%s' % self.unknown_table)
        logging.shutdown()

    def __str__(self):
        return u'未知表名：%s' % self.unknown_table
