# coding=gbk

import SysConfig
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import subprocess
import sys
import os
import xml.dom.minidom
import Tables
from logger import *


class Searcher(object):

    driver = None
    start_url = None
    exist_iframe = False
    code_input_box = None
    code_input_box_xpath = None
    code_submit_button = None
    code_submit_button_xpath = None
    validate_image = None
    validate_image_xpath = None
    validate_input_box = None
    validate_input_box_xpath = None
    validate_submit_button = None
    validate_submit_button_xpath = None
    tab_list = None
    tab_list_xpath = None
    plugin_path = None
    cur_name = None
    cur_code = None
    start_page_handle = None
    load_func_dict = {}
    table_dict = {}
    table_config_file = os.path.join(sys.path[0], '../conf/GsTables.xml')
    province = None

    def __init__(self):
        self.load_func_dict[u'登记信息'] = self.load_dengji
        self.load_func_dict[u'备案信息'] = self.load_beian
        self.load_func_dict[u'动产抵押登记信息'] = self.load_dongchandiyadengji
        self.load_func_dict[u'动产抵押信息'] = self.load_dongchandiyadengji
        self.load_func_dict[u'股权出质登记信息'] = self.load_guquanchuzhidengji
        self.load_func_dict[u'行政处罚信息'] = self.load_xingzhengchufa
        self.load_func_dict[u'经营异常信息'] = self.load_jingyingyichang
        self.load_func_dict[u'严重违法信息'] = self.load_yanzhongweifa
        self.load_func_dict[u'抽查检查信息'] = self.load_chouchajiancha
        self.load_func_dict[u'基本信息'] = self.load_jiben
        self.load_func_dict[u'股东信息'] = self.load_gudong
        self.load_func_dict[u'变更信息'] = self.load_biangeng
        self.load_func_dict[u'主要人员信息'] = self.load_zhuyaorenyuan
        self.load_func_dict[u'分支机构信息'] = self.load_fenzhijigou
        self.load_func_dict[u'清算信息'] = self.load_qingsuan
        self.load_func_dict[u'参加经营的家庭成员姓名'] = self.load_jiatingchengyuan     # Modified by Jing

    # 初始化浏览器
    def build_driver(self):
        """

        :rtype: int
        """
        pass

    def set_config(self):
        """
        设置查询器的配置信息，包括主要的xpath、验证码识别插件
        """
        pass

    # 等待主页加载完成
    def wait_for_load_start_url(self):
        """

        :rtype: int
        """
        pass

    # 输入工商注册码，返回查询状态结果，各分表数据插入在此方法中完成
    def search(self, name):
        self.cur_name = name
        self.submit_search_request()
        self.enter_detail_page()
        self.parse_detail_page()
        self.driver.close()
        self.driver.switch_to.window(self.start_page_handle)


    # 识别验证码
    def recognize_validate_code(self, validate_path):
        print '>>>>>>>>'
        cmd = self.plugin_path + " " + validate_path
        print cmd
        process = subprocess.Popen(cmd.encode('GBK', 'ignore'), stdout=subprocess.PIPE)
        process_out = process.stdout.read()
        #print [process_out]
        answer = process_out.split('\r\n')[6].strip()
        print 'answer: '+answer
        os.remove(validate_path)
        return answer

    def submit_search_request(self):
        self.code_input_box.clear()  # 清空输入框
        self.code_input_box.send_keys(self.cur_name)  # 输入查询代码
        self.code_submit_button.click()  # 点击搜索按钮
        self.validate_image = self.driver.find_element_by_xpath(self.validate_image_xpath)  # 定位验证码图片
        self.validate_input_box = self.driver.find_element_by_xpath(self.validate_input_box_xpath)  # 定位验证码输入框
        self.validate_submit_button = self.driver.find_element_by_xpath(self.validate_submit_button_xpath)  # 定位验证码提交按钮
        validate_image_save_path = SysConfig.get_validate_image_save_path()  # 获取验证码保存路径
        self.download_validate_image(self.validate_image, validate_image_save_path)  # 截图获取验证码
        validate_code = self.recognize_validate_code(validate_image_save_path)  # 识别验证码
        self.validate_input_box.clear()  # 清空验证码输入框
        self.validate_input_box.send_keys(validate_code)  # 输入验证码
        self.validate_submit_button.click()  # 点击搜索（验证码弹窗）

    def enter_detail_page(self):
        pass

    def parse_detail_page(self):
        self.tab_list = self.driver.find_elements_by_xpath(self.tab_list_xpath)
        for tab in self.tab_list:
            tab_text = tab.text
            logging.info(u"解析%s ..." % tab_text)
            if tab.get_attribute('class') != 'current':
                tab.click()
            self.load_func_dict[tab_text]()
            logging.info(u"解析%s成功" % tab_text)

    # 下载验证码到本地
    def download_validate_image(self):
        pass

    # 设置页面最大加载时间，如果超过此时间，页面仍然未加载完成，报超时错误
    def set_timeout_config(self):
        # pass
        self.driver.set_page_load_timeout(SysConfig.page_load_timeout)
        self.driver.implicitly_wait(SysConfig.implicitly_wait_timeout)

    def wait_for_element(self, xpath, seconds):
        return WebDriverWait(self.driver, seconds).\
            until(expected_conditions.presence_of_element_located((By.XPATH, xpath)))

    def find_element(self, xpath,  time_out=SysConfig.element_locate_timeout):
        return WebDriverWait(self.driver, time_out).\
            until(expected_conditions.presence_of_element_located((By.XPATH, xpath)))
    def find_elements(self,  xpath,  time_out=SysConfig.element_locate_timeout):
        """
        :param xpath: xpath字符串
        :param seconds: 最大等待时长，整型
        :return: 定位到的web_element列表，List
        """
        self.find_element(xpath,  time_out)
        return self.driver.find_elements_by_xpath(xpath)

    # 下载登记信息
    def load_dengji(self):
        pass

    # 下载备案信息
    def load_beian(self):
        pass

    # 下载动产抵押登记信息
    def load_dongchandiyadengji(self):
        pass

    # 下载股权出质登记信息
    def load_guquanchuzhidengji(self):
        pass

    # 下载行政处罚信息
    def load_xingzhengchufa(self):
        pass

    # 下载经营异常信息
    def load_jingyingyichang(self):
        pass

    # 下载严重违法信息
    def load_yanzhongweifa(self):
        pass

    # 下载抽查检查信息
    def load_chouchajiancha(self):
        pass

    # 下载基本信息
    def load_jiben(self, table_element):
        pass

    # 下载股东信息
    def load_gudong(self, table_element):
        pass

    # 下载变更信息
    def load_biangeng(self, table_element):
        pass

    # 下载主要人员信息
    def load_zhuyaorenyuan(self, table_element):
        pass

    # 下载参加经营的家庭成员姓名
    def load_jiatingchengyuan(self, table_element):      # Modified by Jing
        pass
    
    # 下载分支机构信息
    def load_fenzhijigou(self, table_element):
        pass

    # 下载清算信息
    def load_qingsuan(self):
        pass

if __name__ == '__main__':
    s = Searcher()
    s.load_table_config()
