# coding=gbk
import PackageTool
import sys
from template.UpdateJob import UpdateJob
from QinghaiFirefoxSearcher import QingHaiFirefoxSearcher
from template.logger import logging


class QinghaiUpdateJob(UpdateJob):

    def set_config(self):
        self.process_name = 'QinghaiGs'
        self.province = u'青海省'
        self.searcher = QingHaiFirefoxSearcher()

if __name__ == "__main__":
    
    job = QinghaiUpdateJob()
    job.run()


