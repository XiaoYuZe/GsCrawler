# coding=gbk
from template.FirefoxSearcher import FirefoxSearcher
from selenium import common
import template.SysConfig as SysConfig
import sys
import os
from template.UnknownColumnException import UnknownColumnException 
from template.UnknownTableException import UnknownTableException 
from selenium.common.exceptions import NoSuchElementException
from template.Tables import *
import time
from selenium import webdriver
from template.DataModel import DataModel
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from template.logger import *
from template.DBClient import *
from template.logger import *
import traceback
from selenium.webdriver.support.ui import WebDriverWait
from pip._vendor.colorama.win32 import handles
import subprocess

class AnhuiFirefoxSearcher(FirefoxSearcher):

    def __init__(self):
        super(AnhuiFirefoxSearcher, self).__init__()
        # 四川抽查检查信息没有备注列
        chouchajiancha_template.column_list.pop()
        gudong_template.column_list.remove('Shareholder_Details')
        self.load_func_dict[u'投资人信息'] = self.load_touziren     #Modified by Jing
#         self.load_func_dict[u'合伙人信息'] = self.load_hehuoren     #Modified by Jing    
        self.load_func_dict[u'成员名册'] = self.load_chengyuanmingce     #Modified by Jing
        self.detail_page_handle=None
        self.search_model = None
        self.result_model = None
        

#     def search(self, name):       
#         self.cur_name = name
#         self.search_model = DataModel(name, self.province)
#         try:
#             if not self.get_ip_status():
#                 # IP被禁，update_status：4
#                 self.search_model.set_update_status(4)            
#             else:
#                 self.submit_search_request()  
#                 self.get_search_result() 
#                 if self.Alert_Exist==True:
#                     data_model.set_update_status(0)
#                 else:           
#                     enter_detail_page_result = self.enter_detail_page()        
#                     if enter_detail_page_result == 0:
#                         # 查询无结果，update_status：0
#                         data_model.set_update_status(0)  
#                         self.driver.close()     
#                         self.driver.switch_to.window(self.start_page_handle)           
#                     elif enter_detail_page_result == 1:
#                         # 查询成功，update_status：1
#                         data_model.set_update_status(1)
#                         self.parse_detail_page()
#                         self.driver.close()
#                         self.driver.switch_to.window(self.start_page_handle)
#                     else:
#                         # 查询失败，update_status：3
#                         data_model.set_update_status(3)
#                         #self.driver.close()
#                         self.driver.switch_to.window(self.start_page_handle)
#         except (UnknownTableException, UnknownColumnException):
#             # 未知表名或列名，update_status：8
#             data_model.set_update_status(8)
#         except:
#             # 未知异常，update_status：3
#             traceback.print_exc()
#             data_model.set_update_status(3)
#             self.driver.close()
#             self.driver.switch_to.window(self.start_page_handle)
#         return data_model


    # 查询名称
    def search(self, name):
        self.cur_name = name
        self.search_model = DataModel(name, self.province)
        try:
            if not self.get_ip_status():
                # IP被禁，update_status：4
                self.search_model.set_update_status(4)                
            else:
                self.submit_search_request()
                if self.Alert_Exist==True:
                    self.search_model.set_update_status(0)
                else: 
                    self.get_search_result()
                    if self.search_model.update_status == 1:
                        self.get_search_result()
                        result_list = self.driver.find_elements_by_xpath("html/body/div[1]/div/div[2]/div[@class='list']")
#                         row=len(self.driver.find_elements_by_xpath("html/body/div[1]/div/div[2]/div[@class='list']"))
                        row=1                    
                        for result in result_list:
                            print row
                            result=self.driver.find_element_by_xpath("html/body/div[1]/div/div[2]/div[@class='list']["+str(row)+"]")
                            org_name = result.find_element_by_xpath("ul/li/a").text
                            self.cur_code = result.find_element_by_xpath("ul/li[2]/span[1]").text
                            # print org_name, self.cur_code
                            self.result_model = DataModel(org_name, self.province)
                            sql_1 = "select EnterpriseName from Registered_Info where RegistrationNo='%s'" % org_name
                            database_client_cursor.execute(sql_1)
                            res_1 = database_client_cursor.fetchone()
                            if res_1:
                                print u'%s已更新' % org_name
                            else:
                                self.result_model.set_update_status(1)
                                result.find_element_by_xpath("ul/li/a").click()
                                self.detail_page_handle = self.driver.window_handles[-1]
                                self.driver.switch_to.window(self.detail_page_handle)
                                try:
                                    self.parse_detail_page()
                                except (UnknownTableException, UnknownColumnException):
                                    # 未知表名或列名，update_status：8
                                    self.result_model.set_update_status(8)
                                print "*******************************************"+self.driver.current_window_handle
                                self.driver.back()
                                self.driver.switch_to.window(self.search_result_handle)
    
                                if self.search_model.name == self.result_model.name:
                                    self.search_model.set_code(self.cur_code)
                                else:
                                    sql_2 = "update GsSrc set %s where orgName='%s'" % (self.result_model, self.result_model.name)
                                    database_client_cursor.execute(sql_2)
                                    sql_3 = "select @@rowcount"
                                    database_client_cursor.execute(sql_3)
                                    res_3 = database_client_cursor.fetchone()
                                    if int(res_3[0]) == 0:
                                        sql_4 = "insert into GsSrc(%s) values(%s)" % (self.result_model.get_cols(), self.result_model.get_vals())
                                        database_client_cursor.execute(sql_4)
                            row+=1

        except Exception:
            # 未知异常，update_status：3
            traceback.print_exc()
            self.search_model.set_update_status(3)
        self.switch_to_search_page()
        return self.search_model


        
    def build_driver(self):
        build_result = 0
#         profile = webdriver.FirefoxProfile(SysConfig.get_firefox_profile_path())
#         self.driver = webdriver.Firefox(firefox_profile=profile)
        self.driver = webdriver.Firefox()
        self.set_timeout_config()
        for i in xrange(SysConfig.max_try_times):
            if self.wait_for_load_start_url():
                break
            else:
                if i == SysConfig.max_try_times:
                    build_result = 1
        return build_result

    def switch_to_search_page(self):
        for handle in self.driver.window_handles:
            if handle != self.start_page_handle:
                self.driver.switch_to.window(handle)
                self.driver.close()
                self.driver.switch_to.window(self.start_page_handle)



    def get_search_result(self):
        if not self.get_ip_status():
            return 4
        for handle in self.driver.window_handles:
            if handle != self.start_page_handle:
                self.driver.switch_to.window(handle) 
                self.search_result_handle=handle 
        search_result = self.driver.find_element_by_xpath('html/body/div[1]/div/div[2]/div')
        result_text = search_result.text.strip()
        if result_text == u'>> 您搜索的条件无查询结果。 <<':
            logging.info(u'查询结果0条')
            self.search_model.set_update_status(0)
        else:
            self.search_model.set_update_status(1)


            
    def submit_search_request(self):
        self.code_input_box = self.driver.find_element_by_xpath(self.code_input_box_xpath)
        self.code_submit_button = self.driver.find_element_by_xpath(self.code_submit_button_xpath)
        self.code_input_box.clear()  # 清空输入框
        self.code_input_box.send_keys(self.cur_name)  # 输入查询代码
        self.code_submit_button.click()
        try:
            self.Alert_Text = self.driver.switch_to_alert().text
            self.driver.switch_to_alert().accept()
            print self.Alert_Text
            self.Alert_Exist=True
        except:            
#             traceback.print_exc()   
            self.Alert_Exist=False 
            validate_image_save_path = SysConfig.get_validate_image_save_path()  # 获取验证码保存路径
            while True:
                try:
                    validate_tip=self.driver.find_element_by_xpath(self.validate_tip_xpath).text
                    if validate_tip!=u'请根据下图中的汉字，在查询框中输入首字母。':
                        self.driver.execute_script("changeVal()")
                        continue
                    self.validate_image = self.driver.find_element_by_xpath(self.validate_image_xpath)  # 定位验证码图片
                    self.validate_input_box = self.driver.find_element_by_xpath(self.validate_input_box_xpath)  # 定位验证码输入框
                    self.validate_submit_button = self.driver.find_element_by_xpath(self.validate_submit_button_xpath)  # 定位验证码提交按钮
                    self.download_validate_image(self.validate_image, validate_image_save_path)  # 截图获取验证码
                    validate_code = self.recognize_validate_code(validate_image_save_path)  # 识别验证码
                    self.validate_input_box.clear()  # 清空验证码输入框
                    self.validate_input_box.send_keys(validate_code)  # 输入验证码
                    self.validate_submit_button.click()  # 点击搜索（验证码弹窗)
                    time.sleep(0.5)
                    self.driver.switch_to_alert().accept()
                    self.driver.execute_script("changeVal()")
                    time.sleep(0.5)
                except common.exceptions.NoAlertPresentException:
                    break
        
    # 判断IP是否被禁
    def get_ip_status(self):
        body_text = self.driver.find_element_by_xpath("/html/body").text
        if body_text.startswith(u'您的访问过于频繁'):
            return False
        else:
            return True

    def set_config(self):
        self.start_url = 'http://www.ahcredit.gov.cn/search.jspx'
        self.code_input_box_xpath = "//*[@id='entName']"
        self.code_submit_button_xpath = "//*[@onclick='queryCheck()']/img"
        self.validate_image_xpath = "//*[@id='valCode']"
        self.validate_input_box_xpath = "//*[@id='checkNoShow']"
        self.validate_submit_button_xpath = "//*[@id='woaicss_con1']/ul/li[4]/a"
        self.tab_list_xpath = "//*[@id='tabs']/ul/li"
        self.validate_tip_xpath ="//*[@id='valCodeTip']"
        self.plugin_path = os.path.join(sys.path[0], r'..\ocr\pinyin\pinyin.bat')
        self.province = u'安徽省'

    # 判断搜索起始页是否加载成功 {0:成功, 1:失败}
    def wait_for_load_start_url(self):
        load_result = True
        try:
            self.driver.get(self.start_url)
            self.start_page_handle = self.driver.current_window_handle
        except common.exceptions.TimeoutException:
            pass
        return load_result

    # 进入详情页 返回int型 {0：查询无结果，1：查询有结果，进入成功，9：进入失败}
    def enter_detail_page(self):
        res = 9
        if not self.get_ip_status():
            return 4
        for handle in self.driver.window_handles:
            if handle != self.start_page_handle:
                self.driver.switch_to.window(handle)  
        search_result = self.driver.find_element_by_xpath('html/body/div[1]/div/div[2]/div')
        result_text = search_result.text.strip()
        logging.info(result_text)
        if result_text == u'>> 您搜索的条件无查询结果。 <<':
            logging.info(u'查询结果0条')
            res = 0
        else:
            print 
            info_list = result_text.split('\n')
            company_name = info_list[0]
            company_abstract = info_list[1]
            self.cur_code = self.driver.find_element_by_xpath('html/body/div[1]/div/div[2]/div/ul/li[2]/span[1]').text.strip()
            print 'cur_code:'+self.cur_code
            print 'company_name:'+company_name
            print 'company_abstract:'+company_abstract
            detail_link = self.driver.find_element_by_xpath('html/body/div[1]/div/div[2]/div/ul/li[1]/a')
            detail_link.click()
            for handle in self.driver.window_handles:
                if handle == self.driver.current_window_handle:
                    continue
                else:
                    self.driver.switch_to.window(handle)
                    self.detail_page_handle=handle
                    res = 1
                    logging.info(u"进入详情页成功")
        return res

    
    def parse_detail_page(self):
        tab_list_length = len(self.driver.find_elements_by_xpath(self.tab_list_xpath))
        for i in range(tab_list_length):
            tab = self.driver.find_element_by_xpath("//*[@id='tabs']/ul/li[%d]" % (i+1))
            tab_text = tab.text
            if tab.get_attribute('class') != 'current':
                tab.click()
            self.load_func_dict[tab_text]()

    
    def load_dengji(self):
        table_list = self.driver.find_elements_by_xpath("/html/body/div[2]/div[2]/div/div[2]/table")
        for table_element in table_list:
            row_cnt = len(table_element.find_elements_by_xpath("tbody/tr"))
            table_desc_element = table_element.find_element_by_xpath("tbody/tr/th")
            table_desc = table_desc_element.text.split('\n')[0].strip() 
            if table_desc==u'股东（发起人）信息': 
                table_desc=u'股东信息'
            logging.info(u"解析%s ..." % table_desc)
            if row_cnt > 1:
                if table_desc == u'基本信息':
                    self.load_func_dict[table_desc](table_element)            
                elif table_desc in self.load_func_dict:
                            self.load_func_dict[table_desc](table_element)
#                             print table_desc
                else:
                    raise UnknownTableException(self.cur_code, table_desc)
            self.driver.switch_to.default_content()
            logging.info(u"解析%s成功" % table_desc)
                       

    def load_jiben(self,table_element):
        jiben_template.delete_from_database(self.cur_code)
        tr_element_list = self.driver.find_elements_by_xpath("//*[@id='jibenxinxi']/table[1]/tbody/tr")
        values = {}
        for tr_element in tr_element_list[1:]:
            th_element_list = tr_element.find_elements_by_xpath('th')
            td_element_list = tr_element.find_elements_by_xpath('td')
            if len(th_element_list) == len(td_element_list):
                col_nums = len(th_element_list)
                for i in range(col_nums):
                    col = th_element_list[i].text.strip().replace('\n','')
                    val = td_element_list[i].text.strip()
                    if col != u'':
                        values[col] = val
        values[u'省份']=self.province
        jiben_template.insert_into_database(self.cur_code, values)
        
        
    def load_gudong(self,table_element):
        gudong_template.delete_from_database(self.cur_code)
        if "invPagination" in self.driver.find_element_by_xpath('/html/body/div[2]/div[2]/div/div[2]/div[2]').get_attribute("id"):
            p_index_table1 = self.driver.find_element_by_xpath('.//div[@id="invPagination"]/table')                           
            if p_index_table1.find_element_by_xpath('tbody/tr/th/a[last()]').get_attribute('href').startswith('javascript:slipFive'):
                slip_five=True
            else:
                slip_five=False
            index_element=None
            i=0
            while True:
                if i>0:
                    index_element=self.driver.find_element_by_xpath('.//div[@id="invPagination"]/table/tbody/tr/th/a[%d]' % (i+1))
                    index_element.click()
                i+=1
                time.sleep(0.5)
                tr_element_list = self.driver.find_elements_by_xpath("//*[@id='invDiv']//tbody/tr")  
                for tr_element in tr_element_list:
                    td_element_list = tr_element.find_elements_by_xpath('td')
                    values = []
                    for td in td_element_list:
                        val = td.text.strip()
                        if val == u'详情':
                            td.find_element_by_xpath('a').click()
                            for handle in self.driver.window_handles:
                                if handle != self.start_page_handle and handle!=self.detail_page_handle:
                                    self.driver.switch_to.window(handle)
                            tr_detail_list = self.driver.find_elements_by_xpath("/html/body/div[2]/table/tbody/tr")
                            for tr_ele in tr_detail_list[3:4]:
                                td_ele_list = tr_ele.find_elements_by_xpath('td')                             
                                for td in td_ele_list[1:]:
                                    va = td.text.strip()
                                    values.append(va)                                     
                            self.driver.close()
                            self.driver.switch_to.window(self.driver.window_handles[-1]) 
                        else:
                            values.append(val)
                    if len(values)<6:
                        values.extend(['','','','','','',''])  
                    print values                                                               
                    gudong_template.insert_into_database(self.cur_code, values)                   
                if i==len(self.driver.find_elements_by_xpath('.//div[@id="invPagination"]/table/tbody/tr/th/a[@id]')):
                    if slip_five:
                        self.driver.find_element_by_xpath(".//div[@id='invPagination']/table/tbody/tr/th/a[last()]").click()
                        slip_five=False
                        i=0
                    else:
                        break                          
        else:
            table_element = self.driver.find_element_by_xpath("//*[@id='invDiv']/table")
            if len(table_element.find_elements_by_xpath("tbody/tr")) > 0:
                last_index_element = self.driver.find_element_by_xpath("//*[@id='jibenxinxi']/table[3]/tbody/tr/th/a[last()]")
                index_element_list_length = int(last_index_element.text.strip())
                for i in range(index_element_list_length):          
                    if i > 0:
                        index_element = self.driver.find_element_by_xpath("//*[@id='jibenxinxi']/table[3]/tbody/tr/th/a[%d]" % (i+1))
                        index_element.click()
                        time.sleep(0.5)
                        table_element = self.driver.find_element_by_xpath("//*[@id='invDiv']")
                    tr_element_list = table_element.find_elements_by_xpath('tbody/tr')  
                    for tr_element in tr_element_list:
                        td_element_list = tr_element.find_elements_by_xpath('td')
                        values = []
                        for td in td_element_list:
                            val = td.text.strip()
                            if val == u'详情':
                                td.find_element_by_xpath('a').click()
                                for handle in self.driver.window_handles:
                                    if handle != self.start_page_handle and handle!=self.detail_page_handle:
                                        self.driver.switch_to.window(handle)
                                tr_detail_list = self.driver.find_elements_by_xpath("/html/body/div[2]/table/tbody/tr")
                                for tr_ele in tr_detail_list[3:4]:
                                    td_ele_list = tr_ele.find_elements_by_xpath('td')                             
                                    for td in td_ele_list[1:]:
                                        va = td.text.strip()
                                        values.append(va)                                    
                                self.driver.close()
                                self.driver.switch_to.window(self.driver.window_handles[-1]) 
                            else:
                                values.append(val)
                        if len(values)<6:
                            values.extend(['','','','','','',''])                                                                                         
                        gudong_template.insert_into_database(self.cur_code, values)       
            
    
    def load_touziren(self,table_element):
        touziren_template = TableTemplate('Investor_Info', u'投资人信息')      
        touziren_template.column_list = ['Investor_Name', 'investment_Method']
        touziren_template.delete_from_database(self.cur_code)
        table_text = self.driver.find_element_by_xpath("//*[@id='invDiv']/table").text.strip()
        if table_text !='':   
            if "javascript:slipFive" in self.driver.find_elements_by_xpath('//*[@id="jibenxinxi"]/table[3]'):
                slip_five=True
            else:
                slip_five=False
                index_element=None
                i=0
            while True:
                if i>0: 
                    index_element=self.driver.find_element_by_xpath('.//*[@id="jibenxinxi"]/table[3]/tbody/tr/th/a[%d]' % (i+1))
                    index_element.click()
                i+=1
                time.sleep(0.5)
                tr_element_list = self.driver.find_elements_by_xpath("//*[@id='invDiv']//tbody/tr") 
                for tr_element in tr_element_list:
                    td_element_list = tr_element.find_elements_by_xpath('td')
                    values = []       
                    for td in td_element_list:
                        val = td.text.strip()
                        values.append(val)                                                             
                    touziren_template.insert_into_database(self.cur_code, values)           
                if i==len(self.driver.find_elements_by_xpath('.//*[@id="jibenxinxi"]/table[3]/tbody/tr/th/a[@id]')):
                        if slip_five:
                            self.driver.find_element_by_xpath(".//*[@id='jibenxinxi']/table[3]/tbody/tr/th/a[last()]").click()
                            slip_five=False
                            i=0
                        else:
                            break                

#  
#     def load_hehuoren(self,table_element):
#         hehuoren_template.delete_from_database(self.cur_code)
#         tr_element_list = self.driver.find_elements_by_xpath("//*[@id='table_fr']/tbody/tr[position()<last()]")
#                   
#             td_element_list = tr_element.find_elements_by_xpath('td')
#             values = []
#             for td in td_element_list:
#                 val = td.text.strip()
#                 values.append(val)                                                             
#             hehuoren_template.insert_into_database(self.cur_code, values)                
  
   
    def load_biangeng(self, table_element):
        biangeng_template.delete_from_database(self.cur_code)
        table_text = self.driver.find_element_by_xpath("//*[@id='altTab']").text.strip()
        if table_text !='':   
            if "javascript:slipFive" in self.driver.find_elements_by_xpath('//*[@id="jibenxinxi"]/table[last()]'):
                slip_five=True
            else:
                slip_five=False
                index_element=None
                i=0
            while True:
                if i>0: 
                    index_element=self.driver.find_element_by_xpath('.//*[@id="jibenxinxi"]/table[last()]/tbody/tr/th/a[%d]' % (i+1))
                    index_element.click()
                i+=1
                time.sleep(0.5)
                row=0
                tr_element_list = self.driver.find_elements_by_xpath("//*[@id='altTab']//tbody/tr") 
                for tr_element in tr_element_list:
                    td_element_list = tr_element.find_elements_by_xpath('td')
                    values = [] 
                    col=0
                    for td in td_element_list:
                        col+=1
                        if col==2: position='before'
                        elif col==3: position='after'
                        else: position='none'
                        val = td.text.strip().replace('\n','')
                        if val.endswith(u'更多'):                            
                            self.driver.execute_script("doShow('%s','%s')" %(row,position)) 
                            val = td.text.strip().replace('\n','')
                            values.append(val[:-4].strip())
                        else:
                            values.append(val.strip())
                    row+=1
                    biangeng_template.insert_into_database(self.cur_code, values)
                if i==len(self.driver.find_elements_by_xpath('.//*[@id="jibenxinxi"]/table[last()]/tbody/tr/th/a[@id]')):
                        if slip_five:
                            self.driver.find_element_by_xpath(".//*[@id='jibenxinxi']/table[last()]/tbody/tr/th/a[last()]").click()
                            slip_five=False
                            i=0
                        else:
                            break        
 
        
    def load_beian(self):
        table_list = self.driver.find_elements_by_xpath("/html/body/div[2]/div[2]/div/div[3]/table")
        for table_element in table_list:
            row_cnt = len(table_element.find_elements_by_xpath("tbody/tr"))
            table_desc_element = table_element.find_element_by_xpath("tbody/tr/th")
            table_desc = table_desc_element.text.split('\n')[0].strip()          
            if row_cnt > 1:
                if table_desc not in self.load_func_dict:
                    raise UnknownTableException(self.cur_code, table_desc)
                logging.info(u"解析%s ..." % table_desc)
                self.load_func_dict[table_desc](table_element)
                self.driver.switch_to.default_content()
                logging.info(u"解析%s成功" % table_desc)


    def load_zhuyaorenyuan(self, table_element):
        zhuyaorenyuan_template.delete_from_database(self.cur_code)
        table_text = self.driver.find_element_by_xpath("//*[@id='memDiv']/table").text.strip()
        if table_text !='':
            if "javascript:slipFive" in self.driver.find_elements_by_xpath('//*[@id="beian"]/table[2]'):
                slip_five=True
            else:
                slip_five=False
                index_element=None
                i=0
            while True:
                if i>0: 
                    index_element=self.driver.find_element_by_xpath('.//*[@id="beian"]/table[2]/tbody/tr/th/a[%d]' % (i+1))
                    index_element.click()
                i+=1
                time.sleep(0.5)
                table_element = self.driver.find_element_by_xpath("//*[@id='memDiv']//tbody/tr")
                tr_element_list = table_element.find_elements_by_xpath("//*[@id='memDiv']//tbody/tr")
                for tr_element in tr_element_list:
                    values = []
                    td_element_list = tr_element.find_elements_by_xpath('td')
                    list_length = len(td_element_list)
                    fixed_length = list_length - list_length % 3
                    for j in range(fixed_length):
                        val = td_element_list[j].text.strip()   
                        values.append(val)
                        if len(values) == 3:
                            zhuyaorenyuan_template.insert_into_database(self.cur_code, values)
                            values = []
                if i==len(self.driver.find_elements_by_xpath('.//*[@id="beian"]/table[2]/tbody/tr/th/a[@id]')):
                    if slip_five:
                        self.driver.find_element_by_xpath(".//*[@id='beian']/table[2]/tbody/tr/th/a[last()]").click()
                        slip_five=False
                        i=0
                    else:
                        break      
        
                    
#     def load_jiatingchengyuan(self, table_element):
#         jiatingchengyuan_template.delete_from_database(self.cur_code)
#         table_element = self.driver.find_element_by_xpath("//*[@id='memDiv']/tbody/tr")
#         tr_element_list = table_element.find_elements_by_xpath("//*[@id='memDiv']/tbody/tr")
#         for tr_element in tr_element_list:
#             values = []
#             td_element_list = tr_element.find_elements_by_xpath('td')
#             list_length = len(td_element_list)
#             fixed_length = list_length - list_length % 3
#             for i in range(fixed_length):
#                 val = td_element_list[i].text.strip()
#                 values.append(val)
#                 if len(values) == 3:
#                     zhuyaorenyuan_template.insert_into_database(self.cur_code, values)
#                     values = []
#                     
    def load_chengyuanmingce(self, table_element):
        zhuyaorenyuan_template.delete_from_database(self.cur_code)
        table_text = self.driver.find_element_by_xpath("//*[@id='countryDiv']/table").text.strip()
        if table_text !='':
            if "javascript:slipFive" in self.driver.find_elements_by_xpath('//*[@id="beian"]/table[2]'):
                slip_five=True
            else:
                slip_five=False
                index_element=None
                i=0
            while True:
                if i>0: 
                    index_element=self.driver.find_element_by_xpath('.//*[@id="beian"]/table[2]/tbody/tr/th/a[%d]' % (i+1))
                    index_element.click()
                i+=1
                time.sleep(0.5)
                table_element = self.driver.find_element_by_xpath("//*[@id='countryDiv']//tbody/tr")
                tr_element_list = table_element.find_elements_by_xpath("//*[@id='countryDiv']//tbody/tr")
                for tr_element in tr_element_list:
                    values = []
                    td_element_list = tr_element.find_elements_by_xpath('td')
                    list_length = len(td_element_list)
                    fixed_length = list_length - list_length % 3
                    for j in range(fixed_length):
                        val = td_element_list[j].text.strip()   
                        values.append(val)
                        if len(values) == 3:
                            zhuyaorenyuan_template.insert_into_database(self.cur_code, values)
                            values = []
                if i==len(self.driver.find_elements_by_xpath('.//*[@id="beian"]/table[2]/tbody/tr/th/a[@id]')):
                    if slip_five:
                        self.driver.find_element_by_xpath(".//*[@id='beian']/table[2]/tbody/tr/th/a[last()]").click()
                        slip_five=False
                        i=0
                    else:
                        break      
 
    def load_fenzhijigou(self, table_element):
        fenzhijigou_template.delete_from_database(self.cur_code)
        table_text = self.driver.find_element_by_xpath("//*[@id='childDiv']/table").text.strip()
        if table_text !='':   
            if "javascript:slipFive" in self.driver.find_elements_by_xpath('//*[@id="beian"]/table[4]'):
                slip_five=True
            else:
                slip_five=False
                index_element=None
                i=0
                while True:
                    if i>0: 
                        index_element=self.driver.find_element_by_xpath('.//*[@id="beian"]/table[4]/tbody/tr/th/a[%d]' % (i+1))
                        index_element.click()
                    i+=1
                    time.sleep(0.5)            
                    tr_element_list = table_element.find_elements_by_xpath("//*[@id='childDiv']/table/tbody/tr")
                    for tr_element in tr_element_list:
                        td_element_list = tr_element.find_elements_by_xpath('td')
                        values = []
                        for td in td_element_list:
                            val = td.text.strip()
                            values.append(val)
                        fenzhijigou_template.insert_into_database(self.cur_code, values)
                    if i==len(self.driver.find_elements_by_xpath('.//*[@id="beian"]/table[4]/tbody/tr/th/a[@id]')):
                        if slip_five:
                            self.driver.find_element_by_xpath(".//*[@id='beian']/table[4]/tbody/tr/th/a[last()]").click()
                            slip_five=False
                            i=0
                        else:
                            break
        
 
    def load_qingsuan(self, table_element):
        pass


    def load_dongchandiyadengji(self):    
        dongchandiyadengji_template.delete_from_database(self.cur_code)    
        table_text = self.driver.find_element_by_xpath("//*[@id='mortDiv']/table").text.strip()
        if table_text !='':
            if "javascript:slipFive" in self.driver.find_elements_by_xpath("//*[@id='dongchandiya']/table[2]"):
                slip_five=True
            else:
                slip_five=False
                index_element=None
                i=0
            while True:
                if i>0: 
                    index_element=self.driver.find_element_by_xpath("//*[@id='dongchandiya']/table[2]/tbody/tr/th/a[%d]" % (i+1))
                    index_element.click()
                i+=1
                time.sleep(0.5)
                tr_element_list = self.driver.find_elements_by_xpath("//*[@id='mortDiv']/table/tbody/tr")
                for tr_element in tr_element_list:
                    td_element_list = tr_element.find_elements_by_xpath('td')
                    values = []
                    for td in td_element_list:
                        val = td.text.strip()
                        if val == u'详情':
                            values.append(td.find_element_by_xpath('a').get_attribute('href'))
                        else:
                            values.append(val)
                    dongchandiyadengji_template.insert_into_database(self.cur_code, values)
                if i==len(self.driver.find_elements_by_xpath('.//*[@id="dongchandiya"]/table[2]/tbody/tr/th/a[@id]')):
                    if slip_five:
                        self.driver.find_element_by_xpath(".//*[@id='dongchandiya']/table[2]/tbody/tr/th/a[last()]").click()
                        slip_five=False
                        i=0
                    else:
                        break                  

    def load_guquanchuzhidengji(self):
        guquanchuzhidengji_template.delete_from_database(self.cur_code)
        table_text = self.driver.find_element_by_xpath("//*[@id='pledgeDiv']/table").text.strip()
        if table_text !='':
            if "javascript:slipFive" in self.driver.find_elements_by_xpath("//*[@id='guquanchuzhi']/table[2]"):
                slip_five=True
            else:
                slip_five=False
                index_element=None
                i=0
            while True:
                if i>0: 
                    index_element=self.driver.find_element_by_xpath("//*[@id='guquanchuzhi']/table[2]/tbody/tr/th/a[%d]" % (i+1))
                    index_element.click()
                i+=1
                time.sleep(0.5)        
                tr_element_list = self.driver.find_elements_by_xpath("//*[@id='pledgeDiv']/table/tbody/tr")
                for tr_element in tr_element_list:       
                    td_element_list = tr_element.find_elements_by_xpath('td')
                    values = []
                    for td in td_element_list:
                        val = td.text.strip()
                        if val.endswith(u'详情'):
                            link=td.find_element_by_xpath('a').get_attribute('onclick')
                            xiangqing_link ="http://gsxt.xzaic.gov.cn"+link[13:-2]
                            print u'xiangqing_link:'+xiangqing_link
                            values.append(xiangqing_link)
                        else:
                            values.append(val)
                    guquanchuzhidengji_template.insert_into_database(self.cur_code, values)
                if i==len(self.driver.find_elements_by_xpath('.//*[@id="guquanchuzhi"]/table[2]/tbody/tr/th/a[@id]')):
                    if slip_five:
                        self.driver.find_element_by_xpath(".//*[@id='guquanchuzhi']/table[2]/tbody/tr/th/a[last()]").click()
                        slip_five=False
                        i=0
                    else:
                        break        
       
        
    def load_xingzhengchufa(self):
        xingzhengchufa_template.delete_from_database(self.cur_code)
        table_text = self.driver.find_element_by_xpath("//*[@id='punDiv']/table").text.strip()
        if table_text !='':
            if "javascript:slipFive" in self.driver.find_elements_by_xpath("//*[@id='xingzhengchufa']/table[2]"):
                slip_five=True
            else:
                slip_five=False
                index_element=None
                i=0
            while True:
                if i>0: 
                    index_element=self.driver.find_element_by_xpath("//*[@id='xingzhengchufa']/table[2]/tbody/tr/th/a[%d]" % (i+1))
                    index_element.click()
                i+=1
                time.sleep(0.5)
                tr_element_list = self.driver.find_elements_by_xpath("//*[@id='punTab']/tbody/tr")
                for tr_element in tr_element_list:         
                    td_element_list = tr_element.find_elements_by_xpath('td')
                    values = []
                    for td in td_element_list[:8]:
                        val = td.text.strip()
                        print val
                        if val.endswith(u'更多'):
                            td.find_element_by_xpath('a').click()
                            val = td.text.strip()
                            values.append(val[:-4].strip())
                        elif val == u'详情':
#                         values.append(td.find_element_by_xpath('a').get_attribute('href'))
                            link=td.find_element_by_xpath('a').get_attribute('onclick')
                            xiangqing_link ="http://www.ahcredit.gov.cn"+link[13:-2]
                            print u'xiangqing_link:'+xiangqing_link
                            values.append(xiangqing_link)
                        else:
                            values.append(val)

                    xingzhengchufa_template.insert_into_database(self.cur_code, values)
                if i==len(self.driver.find_elements_by_xpath('.//*[@id="xingzhengchufa"]/table[2]/tbody/tr/th/a[@id]')):
                    if slip_five:
                        self.driver.find_element_by_xpath(".//*[@id='xingzhengchufa']/table[2]/tbody/tr/th/a[last()]").click()
                        slip_five=False
                        i=0
                    else:
                        break        

              
    def load_jingyingyichang(self):
        jingyingyichang_template.delete_from_database(self.cur_code)
        table_text = self.driver.find_element_by_xpath("//*[@id='excTab']").text.strip()
        if table_text !='':
            if "javascript:slipFive" in self.driver.find_elements_by_xpath("//*[@id='jingyingyichangminglu']/table[2]"):
                slip_five=True
            else:
                slip_five=False
                index_element=None
                i=0
                while True:
                    if i>0: 
                        index_element=self.driver.find_element_by_xpath('.//*[@id="jingyingyichangminglu"]/table[2]/tbody/tr/th/a[%d]' % (i+1))
                        index_element.click()
                    i+=1
                    time.sleep(1)
                    tr_list = self.driver.find_elements_by_xpath("//*[@id='excTab']//tbody/tr")
                    if tr_list:
                        for tr_element in tr_list:
                            values = []
                            td_element_list = tr_element.find_elements_by_xpath('td')
                            for td in td_element_list:
                                val = td.text.strip()
                                if val.endswith(u'更多'):
                                    td.find_element_by_xpath('a').click()
                                    val = td.text.strip()
                                    values.append(val[:-4].strip())
                                else:
                                    values.append(val.strip())                
                            jingyingyichang_template.insert_into_database(self.cur_code, values)
                    print str(len(self.driver.find_elements_by_xpath('.//*[@id="jingyingyichangminglu"]/table[2]/tbody/tr/th/a[@id]')))
                    if i==len(self.driver.find_elements_by_xpath('.//*[@id="jingyingyichangminglu"]/table[2]/tbody/tr/th/a[@id]')):
                        if slip_five:
                            self.driver.find_element_by_xpath(".//*[@id='jingyingyichangminglu']/table[2]/tbody/tr/th/a[last()]").click()
                            slip_five=False
                            i=0
                        else:
                            break

    def load_yanzhongweifa(self):
        pass
 
    def load_chouchajiancha(self):
        chouchajiancha_template.delete_from_database(self.cur_code)
        table_text = self.driver.find_element_by_xpath("//*[@id='spotCheckDiv']/table").text.strip()
        if table_text !='':
            if "javascript:slipFive" in self.driver.find_elements_by_xpath("//*[@id='chouchaxinxi']/table[2]"):
                slip_five=True
            else:
                slip_five=False
                index_element=None
                i=0
                while True:
                    if i>0: 
                        index_element=self.driver.find_element_by_xpath('.//*[@id="chouchaxinxi"]/table[last()]/tbody/tr/th/a[%d]' % (i+1))
                        index_element.click()
                    i+=1
                    time.sleep(1)
                    tr_element_list = self.driver.find_elements_by_xpath("//div[@id='spotCheckDiv']//tbody/tr")
                    for tr_element in tr_element_list:         
                        td_element_list = tr_element.find_elements_by_xpath('td')
                        values = []
                        for td in td_element_list:
                            val = td.text.strip()
                            values.append(val)
                        chouchajiancha_template.insert_into_database(self.cur_code, values)
                    if i==len(self.driver.find_elements_by_xpath('.//*[@id="chouchaxinxi"]/table[last()]/tbody/tr/th/a[@id]')):
                        if slip_five:
                            self.driver.find_element_by_xpath(".//*[@id='chouchaxinxi']/table[last()]/tbody/tr/th/a[last()]").click()
                            slip_five=False
                            i=0
                        else:
                            break        
        

if __name__ == '__main__':

    code_list = [u"云道股份有限公司",u'京仪股份有限公司']
    searcher = AnhuiFirefoxSearcher()
    searcher.set_config()

    if searcher.build_driver() == 0:
        for name in code_list:
            searcher.search(name)
            # break
