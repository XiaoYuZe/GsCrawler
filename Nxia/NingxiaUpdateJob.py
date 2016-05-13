# coding=gbk
import PackageTool
import sys
from template.UpdateJob import UpdateJob
from NingxiaFirefoxSearcher import NingXiaFirefoxSearcher
from template.logger import logging


class NingxiaUpdateJob(UpdateJob):

    def set_config(self):
        self.process_name = 'NingxiaGs'
        self.province = u'宁夏回族自治区'
        self.searcher = NingXiaFirefoxSearcher()

if __name__ == "__main__":
    
    job = NingxiaUpdateJob()
    job.run()


