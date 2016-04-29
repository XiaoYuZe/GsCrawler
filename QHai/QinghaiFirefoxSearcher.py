# coding=gbk
from template.DBClient import database_client_cursor
from template.FirefoxSearcher import FirefoxSearcher
from selenium import common
import template.SysConfig as SysConfig
import sys
import os
from template.UnknownTableException import UnknownTableException
from template.UnknownColumnException import UnknownColumnException
from template.UnknownTableException import UnknownTableException as unknown_table
from template.Tables import *
from template.DataModel import DataModel
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from template.logger import *
import traceback
from selenium import webdriver
import time


class QingHaiFirefoxSearcher(FirefoxSearcher):

    def __init__(self):
        super(QingHaiFirefoxSearcher, self).__init__()
        # 青海抽查检查信息缺少备注列
        chouchajiancha_template.column_list.pop()
        self.start_page_handle = None
        gudong_template.column_list.remove('Shareholder_Details')
        self.detail_page_handle = None
        self.search_model = None
        self.result_model = None





    # 配置页面元素xpath与浏览器插件
    def set_config(self):
        self.start_url = 'http://218.95.241.36/search.jspx'
        self.code_input_box_xpath = ".//*[@id='entName']"
        self.code_submit_button_xpath = ".//*[@id='form']/div[2]/a/img"
        self.validate_image_xpath = ".//*[@id='valCode']"
        self.validate_input_box_xpath = ".//*[@id='checkNoShow']"
        self.validate_submit_button_xpath = ".//*[@id='woaicss_con1']/ul/li[4]/a"
        self.tab_list_xpath = ".//*[@id='tabs']/ul/li"
        self.plugin_path = os.path.join(sys.path[0], r'..\ocr\qinghai\qinghai.bat')
        self.province = u'青海省'

    def build_driver(self):
        build_result = 0
        profile = webdriver.FirefoxProfile()
        self.driver = webdriver.Firefox(firefox_profile=profile)
        self.set_timeout_config()
        for i in xrange(SysConfig.max_try_times):
            if self.wait_for_load_start_url():
                break
            else:
                if i == SysConfig.max_try_times:
                    build_result = 1
        return build_result

    # parser from Sichuan
    def parse_detail_page(self):
        tab_list_length = len(self.find_elements(self.tab_list_xpath))
        #print tab_list_length
        #print self.find_elements(self.tab_list_xpath)[1]
        for i in range(tab_list_length):
            tab = self.find_element(".//*[@id='tabs']/ul/li[%d]" % (i+1))
            tab_text = tab.text
            # print 'ddddddddddddddd'
            # print tab_text, 'tab_text_66'
            # print 'dddddddddddddd'
            if tab.get_attribute('class') != 'current':
                tab.click()
            self.load_func_dict[tab_text]()

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
                self.get_search_result()
                if self.search_model.update_status == 1:
                    result_list = self.find_elements("/html/body/div[1]/div/div[2]/div")
                    row = 1

                    for result in result_list:
                        # print len(result_list),'~~~~89~~~~~'
                        if row ==len(self.find_elements("html/body/div[1]/div/div[2]/div[@class='list']"))+1:
                            # print "the_search_result_row_number_is:"+str(row-1)
                            # self.switch_to_search_page()
                            # self.driver.switch_to.window(self.start_page_handle)
                            # self.driver.close()
                            continue
                        result = self.find_element("html/body/div[1]/div/div[2]/div[@class='list']["+str(row)+"]")
                        # self.driver.execute_script("arguments[0].style=''", result)
                        # print result.text, 'result 90'
                        org_name = result.find_element_by_xpath("ul/li[1]/a").text
                        self.cur_code = result.find_element_by_xpath("ul/li[2]/span[1]").text
                        print org_name,  self.cur_code

                        self.result_model = DataModel(org_name, self.province)
                        self.result_model.set_code(self.cur_code)

                        sql_1 = "select EnterpriseName from Registered_Info where RegistrationNo='%s'" % org_name
                        database_client_cursor.execute(sql_1)
                        res_1 = database_client_cursor.fetchone()
                        # print res_1,'102'
                        if res_1:
                            print u'%s已更新' % org_name
                        else:
                            self.result_model.set_update_status(1)
                            result.find_element_by_xpath("ul/li[1]/a").click()
                            self.detail_page_handle = self.driver.window_handles[-1]
                            self.driver.switch_to.window(self.detail_page_handle)
                            try:
                                self.parse_detail_page()
                            except (UnknownTableException, UnknownColumnException):
                                # 未知表名或列名，update_status：8
                                self.result_model.set_update_status(8)
                            print "*******************************************"+self.driver.current_window_handle
                            # time.sleep(10)
                            self.driver.back()


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

                # self.switch_to_result_page()
        except Exception:
            # print u'33333333333'
            # 未知异常，update_status：3
            traceback.print_exc()
            self.search_model.set_update_status(3)

        self.switch_to_search_page()
        return self.search_model



    def switch_to_search_page(self):
        for handle in self.driver.window_handles:
            if handle != self.start_page_handle:
                self.driver.switch_to.window(handle)
                self.driver.close()
                # print '154dafdsafsd'
                self.driver.switch_to.window(self.start_page_handle)
                # print '145bbdsfasadf'
            # else:
            #     self.driver.close()


    def switch_to_result_page(self):
        pass
        # for handle in self.driver.window_handles:
        #     if handle != self.start_page_handle:
        #         self.driver.window_handles[-1]
        #         # self.driver.switch_to.window(handle)
        #         self.driver.back()
                # self.search_result_handle=handle

    def get_search_result(self):
        # print '>>>>>>>fgh144fgjk>>>>>>'
        if not self.get_ip_status():
            return 4

        for handle in self.driver.window_handles:
            if handle != self.start_page_handle:
                self.driver.switch_to.window(handle)
                self.search_result_handle=handle
        search_result = self.find_element("html/body/div[1]/div/div[2]/div")

        result_text = search_result.text.strip()
        # print result_text
        # u您搜索的条件无查询结果

        if result_text == u'>> 您搜索的条件无查询结果。 <<':
            logging.info(u'查询结果0条')
            self.search_model.set_update_status(0)
        else:
            self.search_model.set_update_status(1)

    # 提交查询请求
    def submit_search_request(self):
        #self.start_page_handle_bak = None
        self.code_input_box = self.find_element(self.code_input_box_xpath)
        self.code_submit_button = self.find_element(self.code_submit_button_xpath)
        self.code_input_box.clear()  # 清空输入框
        self.code_input_box.send_keys(self.cur_name)  # 输入查询代码
        #ActionChains(self.driver).key_down(Keys.SHIFT).perform()
        self.code_submit_button.click()
        #ActionChains(self.driver).key_up(Keys.SHIFT).perform()
        #self.start_page_handle_bak = self.driver.window_handles[-1]
        self.validate_image = self.find_element(self.validate_image_xpath)  # 定位验证码图片
        self.validate_input_box = self.find_element(self.validate_input_box_xpath)  # 定位验证码输入框
        self.validate_submit_button = self.find_element(self.validate_submit_button_xpath)  # 定位验证码提交按钮
        validate_image_save_path = SysConfig.get_validate_image_save_path()  # 获取验证码保存路径
        for i in range(SysConfig.max_try_times):
            try:
                self.validate_image = self.find_element(self.validate_image_xpath)  # 定位验证码图片
                self.download_validate_image(self.validate_image, validate_image_save_path)  # 截图获取验证码
                validate_code = self.recognize_validate_code(validate_image_save_path)  # 识别验证码
                self.validate_input_box.clear()  # 清空验证码输入框
                self.validate_input_box.send_keys(validate_code)  # 输入验证码
                self.validate_submit_button.click()  # 点击搜索（验证码弹窗）
                self.driver.switch_to.alert.accept()
                # time.sleep(1)
            except common.exceptions.NoAlertPresentException:
                break
        logging.info(u"提交查询请求成功")


    # 判断IP是否被禁
    def get_ip_status(self):
        body_text = self.find_element("/html/body").text
        if body_text.startswith(u'您的访问过于频繁'):
            return False
        else:
            return True

    # 判断搜索起始页是否加载成功 {0:成功, 1:失败}
    def wait_for_load_start_url(self):
        load_result = True
        try:
            self.driver.get(self.start_url)
            self.start_page_handle = self.driver.current_window_handle
        except common.exceptions.TimeoutException:
            load_result = False
        return load_result


    # 进入详情页 返回int型 {0：查询无结果，1：查询有结果且进入成功，4：IP被禁，9：进入失败}
    # def enter_detail_page(self):
    #     res = 9
    #     if not self.get_ip_status():
    #         return 4
    #     search_result = self.find_element('/html/body/form/div/div/dl')
    #     result_text = search_result.text.strip()
    #     if result_text == '':
    #         logging.info(u'查询结果0条')
    #         res = 0
    #     else:
    #         info_list = result_text.split('\n')
    #         company_name = info_list[0]
    #         company_abstract = info_list[1]
    #         self.cur_code = search_result.find_element_by_xpath('div/dd/span[1]').text.strip()
    #         # print 'cur_code:' + self.cur_code
    #         # print 'company_name:'+company_name
    #         # print 'company_abstract:'+company_abstract
    #         detail_link = self.find_element('/html/body/form/div/div/dl/div/dt/a')
    #         detail_link.click()
    #         self.detail_page_handle = self.driver.window_handles[-1]
    #         self.driver.close()
    #         res = 1
    #         self.driver.switch_to.window(self.detail_page_handle)
    #         logging.info(u"进入详情页成功")
    #     return res

    # 加载登记信息
    def load_dengji(self):
        # print u'开始登记'+str(time.time())
        # target_div = self.find_element("//*[@id='jibenxinxi']")
        #print target_div.text, 'divtext247'
        table_list = self.find_elements("//*[@id='jibenxinxi']/table")
        table_lens = len(table_list)
        for i in range(table_lens):
            table_element = table_list[i]
            if table_element.text.split('\n')[0].strip() == '<<  1  >>':
                # print table_element.text,'SB269'
                continue
            elif table_element.text.split('\n')[0].strip() == '<<  1  2  >>':
                # print '~~~~~~~272~~~~~~~'
                continue
            else:
                # print table_element.text, 'here 266'
                # table_desc_element = self.find_element("//*[@id='jibenxinxi']/table[i]/tbody/tr[1]/th[1]")
                # print table_desc_element.text, 'content it is'
                table_desc = table_element.text.split('\n')[0].strip()

                # print table_desc[0].strip(), 'dsdsds271',type(table_desc)
                # if table_desc == u'基本信息':
                #     # print u'基本信息268'
                #     self.load_func_dict[table_desc](table_element)
                # elif table_desc == u'股东信息':
                #     # print u'股东信息271'
                #     self.load_func_dict[table_desc](table_element)
                if table_desc in self.load_func_dict:
                    self.load_func_dict[table_desc](table_element)
                elif table_desc.split('\n')[0] == u'股东（发起人）信息':
                    # print "1000000000000000000000000dfasdfasdfas00000000000000000000001"
                    table_desc = u'股东信息'
                    self.load_func_dict[table_desc](table_element)
                # elif table_desc == u'变更信息':
                #     # print u'变更信息274'
                #     self.load_func_dict[table_desc](table_element)

                else:
                    # pass
                    # print u'dengjic'
                    raise unknown_table(self.cur_code, table_desc)

        self.driver.switch_to.default_content()




    # 加载基本信息
    def load_jiben(self, table_desc):
        jiben_template.delete_from_database(self.cur_code)

        table_element = self.find_element(".//*[@id='jibenxinxi']/table[1]")
        tr_element_list = table_element.find_elements_by_xpath('tbody/tr')
        values = {}
        # print tr_element_list, u'jiben_tr_list'
        for tr_element in tr_element_list[1:]:
            th_element_list = tr_element.find_elements_by_xpath('th')
            td_element_list = tr_element.find_elements_by_xpath('td')
            if len(th_element_list) == len(td_element_list):
                col_nums = len(th_element_list)
                for i in range(col_nums):
                    col = th_element_list[i].text.strip().replace('\n','')
                    val = td_element_list[i].text.strip()
                    # print col, val
                    if col != u'':
                        values[col] = val
        values[u'省份'] = self.province
        jiben_template.insert_into_database(self.cur_code, values)

    # 加载股东信息
    def load_gudong(self, table_element):
        # print 'gudongSTART:'+str(time.time())
        try:
            condition = 'javascript:goPage3' in self.driver.find_element_by_xpath(".//*[@id='ainv2']").get_attribute('href')
            # print condition,'MMMMMMMMMMMMMMMayBBBBBBBBBBBBBBBBB545'
            # try:
            #     condition2= 'javascript:goPage3' in self.find_element(".//*[@id='ainv3']").get_attribute('href')
            #     if condition2==True:
            #         rounds=3
            # except:
            #         rounds=2
            rounds=2
        except:
            condition = False

        # table_th_list = table_element.find_elements_by_xpath('tbody/tr[2]/th')
        table_td_if = self.find_element("//*[@id='invDiv']")

        # print table_td_if.text, 'Now_Gudong_Message336'
        if table_td_if.text != u'':
            gudong_template.delete_from_database(self.cur_code)
            # print 'now is:'+str(time.time())
            table_td_tr_list = table_td_if.find_elements_by_xpath('table/tbody/tr')
            for table_tr in table_td_tr_list:
                # print table_tr.text,'gudong341table_tr'
                values = []
                table_td_list = table_tr.find_elements_by_xpath('td')
                for table_td in table_td_list:
                    # print table_td.text,'**********384*********'
                    val = table_td.text
                    if val == u'详情':
                        table_td.find_element_by_xpath('a').click()
                        for handle in self.driver.window_handles:
                            if handle != self.start_page_handle and handle!=self.detail_page_handle:
                                self.driver.switch_to.window(handle)
                        tr_detail_list = self.find_elements("/html/body/div[2]/table/tbody/tr")
                        tr_ele = tr_detail_list[-1]
                        td_ele_list = tr_ele.find_elements_by_xpath('td')
                        for td in td_ele_list[1:]:
                            va = td.text.strip()
                            # print va,u'??????????????396????????????????????????'
                            values.append(va)
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[-1])
                    else:
                        values.append(val)
                # if len(values) < 6:
                #     values.extend(['','','','','','',''])
                values.extend((len(gudong_template.column_list) - len(values))*[''])
                # values.insert(4,'')
                gudong_template.insert_into_database(self.cur_code, values)
            if condition == True:
                self.find_element(".//*[@id='ainv2']").click()
                time.sleep(0.1)
                table_td_tr_list = table_td_if.find_elements_by_xpath('table/tbody/tr')
                for table_tr in table_td_tr_list:
                    # print table_tr.text,'gudong341table_tr'
                    values = []
                    table_td_list = table_tr.find_elements_by_xpath('td')

                    for table_td in table_td_list:
                        # print table_td.text,'**********384*********'
                        val = table_td.text
                        if val == u'详情':
                            table_td.find_element_by_xpath('a').click()
                            for handle in self.driver.window_handles:
                                if handle != self.start_page_handle and handle != self.detail_page_handle:
                                    self.driver.switch_to.window(handle)
                            tr_detail_list = self.find_elements("/html/body/div[2]/table/tbody/tr")
                            tr_ele = tr_detail_list[-1]
                            td_ele_list = tr_ele.find_elements_by_xpath('td')
                            for td in td_ele_list[1:]:
                                va = td.text.strip()
                                # print va,u'??????????????396????????????????????????'
                                values.append(va)
                            self.driver.close()
                            self.driver.switch_to.window(self.driver.window_handles[-1])
                        else:
                            values.append(val)
                    # if len(values)<6:
                    #     values.extend(['','','','','','',''])
                    values.extend((len(gudong_template.column_list) - len(values))*[''])

                    # values.insert(4,'')
                    gudong_template.insert_into_database(self.cur_code, values)
            # print 'gudongEND:'+str(time.time())


                # table_td_list = table_tr.text.split(' ')
                # print table_td_list,type(table_td_list), 'gudong344'
                # for table_td in table_td_list:
                #     print table_td,'gudong344'
                #
                #     values.append(table_td.strip())

                # gudong_template.insert_into_database(self.cur_code, values)






        # gudong_template.delete_from_database(self.cur_code)
        # table_element = self.find_element("/html/body/table[1]")
        # if len(table_element.find_elements_by_xpath("tbody/tr")) > 2:
        #     last_index_element = self.find_element('/html/body/table[2]/tbody/tr/th/a[last()-1]')
        #     index_element_list_length = int(last_index_element.text.strip())
        #     for i in range(index_element_list_length):
        #         if i > 0:
        #             index_element = self.find_element('/html/body/table[2]/tbody/tr/th/a[%d]' % (i+1))
        #             index_element.click()
        #             table_element = self.find_element("/html/body/table[1]")
        #         tr_element_list = table_element.find_elements_by_xpath('tbody/tr')
        #         for tr_element in tr_element_list[2:]:
        #             td_element_list = tr_element.find_elements_by_xpath('td')
        #             values = []
        #             for td in td_element_list:
        #                 val = td.text.strip()
        #                 if val == u'详情':
        #                     values.append(td.find_element_by_xpath('a').get_attribute('href'))
        #                     td.find_element_by_xpath('a').click()
        #                     values.extend(self.load_gudong_detail())
        #                     self.driver.switch_to.frame(table_iframe)
        #                 else:
        #                     values.append(val)
        #                 print val
        #             values.extend((len(gudong_template.column_list) - len(values))*[''])
        #             gudong_template.insert_into_database(self.cur_code, values)
    def load_gudong_detail(self):
        # self.driver.switch_to.window(self.driver.window_handles[-1])
        # td_element_list = self.find_elements("//*[@id='details']/table/tbody/tr[4]/td")
        # values = []
        # for td in td_element_list[1:]:
        #     values.append(td.text.strip())
        # self.driver.close()
        # self.driver.switch_to.window(self.detail_page_handle)
        # return values
        pass


    # 加载变更信息
    def load_biangeng(self, table_element):
        # print 'biangengSTART'+str(time.time())
        # biangeng_template.delete_from_database(self.cur_code)
        try:
            condition = 'javascript:goPage3' in self.driver.find_element_by_xpath(".//*[@id='aalt2']").get_attribute('href')
            # print condition,'MMMMMMMMMMMMMMMayBBBBBBBBBBBBBBBBB545'
            # try:
            #     condition2= 'javascript:goPage3' in self.find_element(".//*[@id='aalt3']").get_attribute('href')
            #     if condition2==True:
            #         rounds=3
            # except:
            #         rounds=2
            rounds=2
        except:
            condition = False
        # table_element_list = self.find_elements("//*[@id='jibenxinxi']/table")
        # for table_element in table_element_list:
        #     table_if =table_element.find_element_by_xpath('tbody/tr[1]/th').text
        #     if table_if == u"变更信息":

        # table_th_list = table_element.find_elements_by_xpath('tbody/tr[2]/th')
        table_td_if = self.find_element("//*[@id='altDiv']")

        # print table_td_if.text, 'No biangeng Message357'
        if table_td_if.text != u'':
            biangeng_template.delete_from_database(self.cur_code)
            table_td_tr_list = table_td_if.find_elements_by_xpath("table/tbody/tr")
            # print table_td_tr_list,'405'
            for table_tr in table_td_tr_list:
                values = []
                # print table_tr.text,'biangengline407'
                table_td_list = table_tr.text.split(' ')
                table_td_list = table_tr.find_elements_by_xpath('td')
                for table_td in table_td_list:
                    try:
                        if 'javascript:void(0)' in table_td.find_element_by_xpath('a').get_attribute('href'):
                            table_td.find_element_by_xpath('a').click()
                            time.sleep(0.2)
                            values.append(table_td.text.strip().strip(u'收起更多'))
                    # print table_td,'biangengtd411'
                    except:
                        values.append(table_td.text.strip())

                biangeng_template.insert_into_database(self.cur_code, values)
            if condition==True:
                self.find_element(".//*[@id='aalt2']").click()
                time.sleep(0.1)
                table_td_tr_list = table_td_if.find_elements_by_xpath("table/tbody/tr")
                # print table_td_tr_list,'405'
                for table_tr in table_td_tr_list:
                    values = []
                    # print table_tr.text,'biangengline407'
                    table_td_list = table_tr.find_elements_by_xpath('td')
                    # print 'teststart'+str(time.time())
                    for table_td in table_td_list:
                        try:
                            if 'javascript:void(0)' in table_td.find_element_by_xpath('a').get_attribute('href'):
                                table_td.find_element_by_xpath('a').click()
                                time.sleep(0.1)
                                values.append(table_td.text.strip().strip(u'收起更多'))
                            # print table_td,'biangengtd411'
                        except:
                            values.append(table_td.text.strip())
                    # print 'testend'+str(time.time())
                    biangeng_template.insert_into_database(self.cur_code, values)
        # print 'biangengEND'+str(time.time())






    # 加载备案信息
    def load_beian(self):
        # print 'beianSTART'+str(time.time())
        table_list = self.find_elements("//*[@id='beian']/table")

        for table_element in table_list:
            # row_cnt = len(table_element.find_elements_by_xpath("tbody/tr"))
            # print 'iiiSTART'+str(time.time())
            table_desc_element = table_element.find_element_by_xpath("tbody/tr/th")
            table_desc = table_desc_element.text.split('\n')[0].strip()
            # print 'iiiEND'+str(time.time())
            # if table_desc == u'主要人员信息':
            #     self.load_func_dict[table_desc](table_element)
            # elif table_desc == u'分支机构信息':
            #     self.load_func_dict[table_desc](table_element)
            if table_desc == '<<  1  >>':
                # print "USB beian"
                continue
            elif table_desc == '<<  1  2  >>':
                # print  'youfenye453'
                continue

            elif table_desc == '<<  1  2  3  >>':
                # print '3youfenye457'

                continue
            elif table_desc in self.load_func_dict:
                self.load_func_dict[table_desc](table_element)
            else:
                raise unknown_table(self.cur_code, table_desc)

            self.driver.switch_to.default_content()
        # print 'beianEND'+str(time.time())

    # 加载主要人员信息
    def load_zhuyaorenyuan(self, table_element):
        # zhuyaorenyuan_template.delete_from_database(self.cur_code)

        # table_element_list = self.find_elements("//*[@id='beian']/table")
        #
        # for table_element in table_element_list:
        #     table_if =table_element.find_element_by_xpath('tbody/tr[1]/th').text
        #     # print table_if, 'table_if450'
        #     if table_if == u"主要人员信息":
        # print 'zhuyaorenyuanSTART'+str(time.time())
        try:
            condition = 'javascript:goPage3' in self.driver.find_element_by_xpath(".//*[@id='amem2']").get_attribute('href')
            # try:
            #     condition2= 'javascript:goPage3' in self.find_element(".//*[@id='amem3']").get_attribute('href')
            #     if condition2==True:
            #         rounds=3
            # except:
            #         rounds=2
            rounds = 2
        except:
            condition = False
        # print 'zhuyaorenyuianPos1'+str(time.time())
        # table_th_list = table_element.find_elements_by_xpath('tbody/tr[2]/th')
        table_td_if = self.find_element("//*[@id='memDiv']")
        # print table_td_if.text, 'Now zhuyaorenyuan Message357'
        # print 'zhuyaorenyuianPosc'+str(time.time())
        if table_td_if.text != u'':
            zhuyaorenyuan_template.delete_from_database(self.cur_code)
            # print 'zhuyaorenyuianPos2'+str(time.time())
            table_td_if = self.find_element("//*[@id='memDiv']")
            table_td_tr_list = table_td_if.find_elements_by_xpath("table/tbody/tr")
            # print 'zhuyaorenyuianPos3'+str(time.time())
            for tr_element in table_td_tr_list:
                values = []
                td_element_list = tr_element.find_elements_by_xpath('td')
                list_length = len(td_element_list)
                fixed_length = list_length - list_length % 3
                for i in range(fixed_length):
                    val = td_element_list[i].text.strip()
                    values.append(val)
                    if len(values) == 3:
                        zhuyaorenyuan_template.insert_into_database(self.cur_code, values)
                        values = []

            # for table_tr in table_td_tr_list:
            #     values = []
            #     # print table_tr.text,'biangengline407'
            #     table_td_list = table_tr.text.split(' ')
            #
            #     for table_td in table_td_list:
            #         # print table_td,'biangengtd411'
            #         values.append(table_td.strip())
            #
            #     zhuyaorenyuan_template.insert_into_database(self.cur_code, values)
            if condition==True:
                # print 'please562~~~~~~~True~~~~~~'
                # print rounds
                for cons in range(1,rounds):
                    # table_td_if = self.find_element("//*[@id='memDiv']")
                    # table_td_tr_list = table_td_if.find_elements_by_xpath("table/tbody/tr")
                    self.find_element('//*[@id="amem2"]').click()
                    time.sleep(0.5)
                    table_td_if = self.find_element("//*[@id='memDiv']")
                    table_td_tr_list = table_td_if.find_elements_by_xpath("table/tbody/tr")
                    # print cons,'594roundcircle'
                    for tr_element in table_td_tr_list:
                        values = []
                        td_element_list = tr_element.find_elements_by_xpath('td')
                        list_length = len(td_element_list)
                        fixed_length = list_length - list_length % 3
                        for i in range(fixed_length):
                            val = td_element_list[i].text.strip()
                            values.append(val)
                            if len(values) == 3:
                                zhuyaorenyuan_template.insert_into_database(self.cur_code, values)
                                values = []
                    cons += 1
            # print 'zhuyaorenyuianEND'+str(time.time())

                    # if i<rounds+1:






    # 加载分支机构信息
    def load_fenzhijigou(self, table_element):
        fenzhijigou_template.delete_from_database(self.cur_code)

        # table_element_list = self.find_elements("//*[@id='beian']/table")
        # for table_element in table_element_list:
        #     table_if =table_element.find_element_by_xpath('tbody/tr[1]/th').text
        #     # print table_if, 'table_if494'
        #     if table_if == u"分支机构信息":
        #         table_th_list = table_element.find_elements_by_xpath('tbody/tr[2]/th')
        table_td_if = self.find_element("//*[@id='childDiv']")

        # print table_td_if.text, 'Now fenzhijigou Message499'
        if table_td_if.text != u'':
            # print '~~501~~'
            table_td_tr_list = table_td_if.find_elements_by_xpath("table/tbody/tr")
            # print table_td_tr_list,'503'
            for table_tr in table_td_tr_list:
                values = []
                # print table_tr.text,'fenzhijigou506'
                table_td_list = table_tr.text.split(' ')

                for table_td in table_td_list:
                    # print table_td,'fenzhijigou509'
                    values.append(table_td.strip())

                fenzhijigou_template.insert_into_database(self.cur_code, values)
        # print '~~514~~'

    # 加载清算信息
    def load_qingsuan(self, table_element):

        table_element_list = self.find_elements("//*[@id='beian']/table")
        for table_element in table_element_list:
            table_if =table_element.find_element_by_xpath('tbody/tr[1]/th').text
            if table_if == u"清算信息":

                val_1 = table_element.find_element_by_xpath('tbody/tr[2]/td').text.strip()
                val_2 = table_element.find_element_by_xpath('tbody/tr[3]/td').text.strip()
                values = [val_1, val_2]
                # print values, 'qingsuan_value_446'
                if len(values[0]) != 0 or len(values[1]) != 0:
                    qingsuan_template.delete_from_database(self.cur_code)
                    qingsuan_template.insert_into_database(self.cur_code, values)

    # 加载动产抵押信息
    def load_dongchandiyadengji(self):
        # dongchandiyadengji_template.delete_from_database(self.cur_code)
        # table_iframe = self.find_element(".//div[@id='dcdy']/iframe")
        # self.driver.switch_to.frame(table_iframe)
        table_element_if = self.find_element("//*[@id='mortDiv']/table")
        # print table_element_if.text,'dongchandiya'
        if table_element_if.text !='':
            dongchandiyadengji_template.delete_from_database(self.cur_code)
        # table_element = table_element_list[0]
        # row_cnt = len(table_element.find_elements_by_xpath("tbody/tr"))
        # if row_cnt > 2:
        #     last_index_element = self.find_element('/html/body/table[2]/tbody/tr/th/a[last()-1]')
        #     index_element_list_length = int(last_index_element.text.strip())
        #     for i in range(index_element_list_length):
        #         if i > 0:
        #             index_element = self.find_element('/html/body/table[2]/tbody/tr/th/a[%d]' % (i+1))
        #             index_element.click()
        #             table_element = self.find_element("/html/body/table[1]")
            tr_element_list = table_element_if.find_elements_by_xpath('tbody/tr')
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
        self.driver.switch_to.default_content()

    # 加载股权出质登记信息
    def load_guquanchuzhidengji(self):
        # # table_iframe = self.find_element(".//div[@id='guquanchuzhi']/iframe")
        # # self.driver.switch_to.frame(table_iframe)
        table_element_if = self.find_element("//*[@id='pledgeDiv']/table")
        # print table_element_if.text, 'guquanchuzhi'
        if table_element_if.text != '':
            guquanchuzhidengji_template.delete_from_database(self.cur_code)

        # table_element = table_element_list[0]
        # row_cnt = len(table_element.find_elements_by_xpath("tbody/tr"))
        # if row_cnt > 2:
        #     last_index_element = self.find_element('/html/body/table[2]/tbody/tr/th/a[last()-1]')
        #     index_element_list_length = int(last_index_element.text.strip())
        #     for i in range(index_element_list_length):
        #         if i > 0:
        #             index_element = self.find_element('/html/body/table[2]/tbody/tr/th/a[%d]' % (i+1))
        #             index_element.click()
        #             table_element = self.find_element("/html/body/table[1]")
            tr_element_list = table_element_if.find_elements_by_xpath('tbody/tr')
            for tr_element in tr_element_list:
                td_element_list = tr_element.find_elements_by_xpath('td')
                values = []
                for td in td_element_list:
                    val = td.text.strip()
                    values.append(val)
                guquanchuzhidengji_template.insert_into_database(self.cur_code, values)
        self.driver.switch_to.default_content()

    # 加载行政处罚信息
    def load_xingzhengchufa(self):

        # # table_iframe = self.find_element(".//div[@id='xingzhengchufa']/iframe")
        #  #self.driver.switch_to.frame(table_iframe)
        table_element_if = self.find_element("//*[@id='punDiv']/table")
        # print table_element_if.text, 'xingzhengchufa'
        if table_element_if.text !='':
            xingzhengchufa_template.delete_from_database(self.cur_code)
        #  table_element = table_element_list[0]
        #  row_cnt = len(table_element.find_elements_by_xpath("tbody/tr"))
        #  if row_cnt > 2:
        #      last_index_element = self.find_element('/html/body/table[2]/tbody/tr/th/a[last()-1]')
        #      index_element_list_length = int(last_index_element.text.strip())
        #      for i in range(index_element_list_length):
        #          if i > 0:
        #              index_element = self.find_element('/html/body/table[2]/tbody/tr/th/a[%d]' % (i+1))
        #              index_element.click()
        #              table_element = self.find_element("/html/body/table[1]")
            tr_element_list = table_element_if.find_elements_by_xpath('tbody/tr')
            for tr_element in tr_element_list:
                td_element_list = tr_element.find_elements_by_xpath('td')
                values = []
                for td in td_element_list:
                    val = td.text.strip()
                    values.append(val)
                if len(values) > 5:
                    values.pop(-2)
                xingzhengchufa_template.insert_into_database(self.cur_code, values)
        self.driver.switch_to.default_content()

    # 加载经营异常信息
    def load_jingyingyichang(self):

        # table_iframe = self.find_element(".//div[@id='jyyc']/iframe")
        # self.driver.switch_to.frame(table_iframe)
        table_element_if = self.find_element("//*[@id='excDiv']/table")
        # print table_element_if.text,'jingyingyichang'
        if table_element_if.text !='':
            jingyingyichang_template.delete_from_database(self.cur_code)
        # table_element = table_element_list[0]
        # row_cnt = len(table_element.find_elements_by_xpath("tbody/tr"))
        # if row_cnt > 2:
        #     last_index_element = self.find_element('/html/body/table[2]/tbody/tr/th/a[last()-1]')
        #     index_element_list_length = int(last_index_element.text.strip())
        #     for i in range(index_element_list_length):
        #         if i > 0:
        #             index_element = self.find_element('/html/body/table[2]/tbody/tr/th/a[%d]' % (i+1))
        #             index_element.click()
        #             table_element = self.find_element("/html/body/table[1]")
            tr_element_list = table_element_if.find_elements_by_xpath('tbody/tr')
            for tr_element in tr_element_list:
                td_element_list = tr_element.find_elements_by_xpath('td')
                values = []
                for td in td_element_list:
                    val = td.text.strip()
                    values.append(val)
                jingyingyichang_template.insert_into_database(self.cur_code, values)
        self.driver.switch_to.default_content()

    # 加载严重违法信息
    def load_yanzhongweifa(self):

        # table_iframe = self.find_element(".//div[@id='yzwf']/iframe")
        # self.driver.switch_to.frame(table_iframe)
        table_element_if = self.find_element("//*[@id='serillDiv']/table")
        # print table_element_if.text,'yanzhongweifa'
        if table_element_if.text != '':
            yanzhongweifa_template.delete_from_database(self.cur_code)
        # table_element = table_element_list[0]
        # row_cnt = len(table_element.find_elements_by_xpath("tbody/tr"))
        # if row_cnt > 2:
        #     last_index_element = self.find_element('/html/body/table[2]/tbody/tr/th/a[last()-1]')
        #     index_element_list_length = int(last_index_element.text.strip())
        #     for i in range(index_element_list_length):
        #         if i > 0:
        #             index_element = self.find_element('/html/body/table[2]/tbody/tr/th/a[%d]' % (i+1))
        #             index_element.click()
        #             table_element = self.find_element("/html/body/table[1]")
            tr_element_list = table_element_if.find_elements_by_xpath('tbody/tr')
            for tr_element in tr_element_list:
                td_element_list = tr_element.find_elements_by_xpath('td')
                values = []
                for td in td_element_list:
                    val = td.text.strip()
                    values.append(val)
                yanzhongweifa_template.insert_into_database(self.cur_code, values)
        self.driver.switch_to.default_content()

    # 加载抽查检查信息
    def load_chouchajiancha(self):

        # table_iframe = self.find_element(".//div[@id='ccjc']/iframe")
        # self.driver.switch_to.frame(table_iframe)
        table_element_if = self.find_element("//*[@id='spotCheckDiv']/table")
        # print table_element_if.text, 'chouchajiancha'
        if table_element_if.text != '':
            chouchajiancha_template.delete_from_database(self.cur_code)
        # table_element = table_element_list[0]
        # row_cnt = len(table_element.find_elements_by_xpath("tbody/tr"))
        # if row_cnt > 2:
        #     last_index_element = self.find_element('/html/body/table[2]/tbody/tr/th/a[last()-1]')
        #     index_element_list_length = int(last_index_element.text.strip())
        #     for i in range(index_element_list_length):
        #         if i > 0:
        #             index_element = self.find_element('/html/body/table[2]/tbody/tr/th/a[%d]' % (i+1))
        #             index_element.click()
        #             table_element = self.find_element("/html/body/table[1]")
            tr_element_list = table_element_if.find_elements_by_xpath('tbody/tr')
            for tr_element in tr_element_list:
                td_element_list = tr_element.find_elements_by_xpath('td')
                values = []
                for td in td_element_list:
                    val = td.text.strip()
                    values.append(val)
                chouchajiancha_template.insert_into_database(self.cur_code, values)
        self.driver.switch_to.default_content()

if __name__ == '__main__':

    name_list = [u'西宁朵云轩典藏商贸有限公司']
    searcher = QingHaiFirefoxSearcher()
    searcher.set_config()
    for name in name_list:
        if searcher.build_driver() == 0:
            searcher.search(name)
