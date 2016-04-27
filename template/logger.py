# coding=gbk
import logging
import time


def set_logger_name(file_name):
    print u'日志名称:%s' % file_name
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %X',
                        filename=file_name,
                        filemode='w')

if __name__ == '__main__':
    set_logger_name(r'D:\\blacksistins.txt')
    for i in range(5):
        logging.info('blacksisters%d' %i)


