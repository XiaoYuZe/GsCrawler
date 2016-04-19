# coding=gbk

import sys
from template.UpdateJob import UpdateJob
from HebeiFirefoxSearcher import HebeiFirefoxSearcher
from template.logger import logging


class HebeiUpdateJob(UpdateJob):

    def set_config(self):
        self.process_name = 'HebeiGs'
        self.province = u'�ӱ�ʡ'
        self.searcher = HebeiFirefoxSearcher()

if __name__ == "__main__":
    
    job = HebeiUpdateJob()
    job.run()


