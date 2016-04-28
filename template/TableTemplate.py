# coding=gbk
from DBClient import *
from UnknownColumnException import UnknownColumnException


class TableTemplate(object):

    table_name = None
    table_desc = None
    column_list = None
    column_dict = None

    def __init__(self, table_name, table_desc):
        self.table_name = table_name
        self.table_desc = table_desc

    def set_column_list(self, column_list):
        self.column_list = column_list

    def set_column_dict(self, column_dict):
        self.column_dict = column_dict

    def delete_from_database(self, code):
        sql = u"delete from %s where RegistrationNo='%s'" % (self.table_name, code)
        # print sql
        database_client_cursor.execute(sql)

    def insert_into_database(self, code, values):
        if type(values) == list:
            col_str = ','.join(self.column_list)
            val_str = "','".join(values)
            sql = u"insert into %s(%s,RegistrationNo,lastUpdateTime) values('%s','%s',getDate())" % (self.table_name, col_str, val_str, code)

        elif type(values) == dict:
            col_str = 'lastUpdateTime'
            val_str = 'getDate()'
            for col_desc in values:
                if col_desc not in self.column_dict:
                    raise UnknownColumnException(code, col_desc)
                col_str += (","+self.column_dict[col_desc])
                val_str += (",'"+values[col_desc]+"'")
            sql = u"insert into %s(%s) values(%s)" % (self.table_name, col_str, val_str)
        # print sql
        database_client_cursor.execute(sql)



