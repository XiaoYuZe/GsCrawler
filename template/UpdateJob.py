# coding=gbk
import time
from DBClient import *
import SysConfig
from logger import *
import sys
import os


class UpdateJob(object):

    process_name = None
    pid = None
    process_identity = None
    host = None
    searcher = None
    province = None
    batch_size = 10

    def __init__(self):
        pass

    def set_config(self):
        pass

    def build_searcher(self):
        self.searcher.set_config()
        if self.searcher.build_driver() != 0:
            logging.info(u"查询器构建失败!")
            logging.shutdown()
            self.searcher.driver.quit()
            sys.exit()

    # 获取当前主机地址
    def get_local_host(self):
        if os.path.exists(r'D:\PublishAgent\LocalIp.txt'):
            f = open(r'D:\PublishAgent\LocalIp.txt')
            self.host = f.read().strip()
            f.close()
        else:
            logging.info(u"IP配置文件不存在，自动获取主机名")
            self.host = os.getenv('computername')

    # 注册进程信息
    def register_process(self):
        self.get_local_host()
        SysConfig.province = self.province
        self.pid = os.getpid()
        cur_time = time.strftime('%Y-%m-%d %X', time.localtime())

        sql1 = "insert into ProcessStatus (processID,processName,processStatus,startTime,lastUpdateTime,totalUpdateCnt,host) " \
               "values('%s','%s',0,'%s',getDate(),0,'%s')" % (self.pid, self.process_name, cur_time, self.host)
        database_client_cursor.execute(sql1)
        sql2 = 'select SCOPE_IDENTITY()'
        database_client_cursor.execute(sql2)
        self.process_identity = int(database_client_cursor.fetchone()[0])
        database_client_connection.commit()
        file_name = SysConfig.get_log_path(self.process_identity)
        set_logger_name(file_name)
        logging.info(u"进程名称:%s" % self.process_name)
        logging.info(u"pid:%s" % self.pid)
        logging.info(u"process_identity:%s" % self.process_identity)
        logging.info(u"主机名/IP:%s" % self.host)

    def update_code(self, code):
        logging.info(u"更新代码:%s" % code)
        update_result = 1
        data_model = None
        for i in range(SysConfig.max_try_times):
            data_model = self.searcher.search(code)
            if data_model.update_status in (0, 1, 4, 8):
                break
        if data_model.update_status in (0, 1, 8):
            data_model.update_to_db()
            update_result = 0
        elif data_model.update_status == 4:
            update_result = 4
        logging.info(u"更新状态:%d" % data_model.update_status)
        return update_result

    def update_proc(self):
        process_status = 0
        total_update_cnt = 0
        for batch_idx in xrange(100000000):
            sql_1 = "update top(%d) GsSrc " \
                    "set updateStatus=-2, processIdentity='%d_%d', lastUpdateTime=GETDATE() " \
                    "where province='%s' " \
                    "and updateStatus=-1" % (self.batch_size, self.process_identity, batch_idx, self.province)
            database_client_cursor.execute(sql_1)
            database_client_connection.commit()

            sql_2 = "select orgName from GsSrc where processIdentity='%d_%d'" % (self.process_identity, batch_idx)
            database_client_cursor.execute(sql_2)
            res_2 = database_client_cursor.fetchall()
            batch_list = [row[0] for row in res_2]
            if len(batch_list) == 0:
                sql_3 = "update GsSrc set updateStatus=-1 where province='%s' and updateStatus=-2 " \
                        "and DATEDIFF(MINUTE,lastUpdateTime,GETDATE())>=10" % self.province
                database_client_cursor.execute(sql_3)
                sql_4 = "select @@rowcount"
                database_client_cursor.execute(sql_4)
                res_4 = database_client_cursor.fetchone()
                row_count = int(res_4[0])
                if row_count == 0:
                    break
            for code in batch_list:
                process_status = self.update_code(code)
                if process_status == 0:
                    total_update_cnt += 1
                sql_5 = "update ProcessStatus set processStatus=%d, totalUpdateCnt=%d, lastUpdateTime=GETDATE() where processIdentity=%d" % \
                        (process_status, total_update_cnt, self.process_identity)
                database_client_cursor.execute(sql_5)
                database_client_connection.commit()
                if process_status != 0:
                    break
            if process_status != 0:
                break
        if process_status == 0:
            logging.info(u'任务更新完成!')
        else:
            logging.info(u'任务更新失败!')
        logging.shutdown()
        self.searcher.driver.quit()

    def run(self):
        self.set_config()
        self.register_process()
        self.build_searcher()
        self.update_proc()

if __name__ == '__main__':
    job = UpdateJob()
    print time.strftime('%Y-%m-%d %X', time.localtime())
 