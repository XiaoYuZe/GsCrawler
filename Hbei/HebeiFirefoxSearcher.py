# coding=gbk
from template.DBClient import database_client_cursor
from template.FirefoxSearcher import FirefoxSearcher
from selenium import common
import template.SysConfig as SysConfig
import sys
import os
from template.UnknownTableException import UnknownTableException
from template.UnknownColumnException import UnknownColumnException
from template.Tables import *
from template.DataModel import DataModel
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from template.logger import *
import traceback
from selenium import webdriver
import subprocess
import sys
import os


class HebeiFirefoxSearcher(FirefoxSearcher):

    def __init__(self):
        super(HebeiFirefoxSearcher, self).__init__()
        # ���ĳ������Ϣȱ�ٱ�ע��
        chouchajiancha_template.column_list.pop()

        gudong_template.column_list = ['Shareholder_Type','Shareholder_Name', 'Shareholder_CertificationType', 'Shareholder_CertificationNo',  'Shareholder_Details',
                               'Subscripted_Capital', 'ActualPaid_Capital', 'Subscripted_Method', 'Subscripted_Amount', 'Subscripted_Time', 'ActualPaid_Method',
                               'ActualPaid_Amount', 'ActualPaid_Time']
        dongchandiyadengji_template.column_list.remove('ChattelMortgage_AnnounceDate')
        gudong_template.column_list.remove('Shareholder_Details')
        guquanchuzhidengji_template.column_list.remove('EquityPledge_AnnounceDate')
        self.start_page_handle_bak = None
        self.detail_page_handle = None
        self.search_model = None
        self.result_model = None
        self.login_error_path = None

    def get_validate_file_path(self):
        return os.path.join(sys.path[0],'..\\data\\' + str(os.getpid()))
        print sys.path[0]

        # ʶ����֤��
    def recognize_validate_code(self, validate_path,validate_result_path):
        print '>>>>>>>>'
        cmd = self.plugin_path + " " + validate_path+" "+ validate_result_path+'.txt'
        print cmd
        # time.sleep(0.5)
        process = subprocess.Popen(cmd.encode('GBK', 'ignore'), stdout=subprocess.PIPE)
        process.communicate()

        fr = open(validate_result_path+'.txt', 'r')
        answer = fr.readline().strip()
        fr.close()
        print 'answer: '+answer
        os.remove(validate_path)
        os.remove(validate_result_path+'.txt')
        return answer


    # ����ҳ��Ԫ��xpath����������
    def set_config(self):
        self.start_url = 'http://www.hebscztxyxx.gov.cn/notice/'
        self.code_input_box_xpath = "//*[@id='keyword']"
        self.code_submit_button_xpath = "//a[contains(@onclick,'#keyword')]"
        self.validate_image_xpath = ".//*[@id='cpt-img']"
        self.validate_input_box_xpath = "//*[@id='cpt-input']"
        self.validate_submit_button_xpath = ".//*[@id='captcha']/div[2]/a"
        self.tab_list_xpath = '/html/body/div[4]/div/div/div[2]/div[1]/ul/li'
        self.plugin_path = os.path.join(sys.path[0], r'..\ocr\hebei\hebei.bat')
        self.login_error_path = 'html/body/div[8]/div[3]/div/button'
        self.province = u'�ӱ�ʡ'

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

    # ��ѯ����
    def search(self, name):
        self.cur_name = name
        self.search_model = DataModel(name, self.province)
        try:
            if not self.get_ip_status():
                # IP������update_status��4
                self.search_model.set_update_status(4)
            else:
                self.submit_search_request()
                self.get_search_result()
                if self.search_model.update_status == 1:
                    result_list = self.driver.find_elements_by_xpath(".//*[@class='list-info']/div")
                    for result in result_list:
                        # self.driver.execute_script("arguments[0].style=''", result)
                        org_name = result.find_element_by_xpath("div[1]/a").text
                        self.cur_code = result.find_element_by_xpath("div[2]/span[1]").text
                        print org_name, self.cur_code
                        self.result_model = DataModel(org_name, self.province)

                        sql_1 = "select EnterpriseName from Registered_Info where RegistrationNo='%s'" % org_name
                        database_client_cursor.execute(sql_1)
                        res_1 = database_client_cursor.fetchone()
                        if res_1:
                            print u'%s�Ѹ���' % org_name
                        else:
                            self.result_model.set_update_status(1)
                            result.find_element_by_xpath("div[1]/a").click()
                            self.detail_page_handle = self.driver.window_handles[-1]
                            self.driver.switch_to.window(self.detail_page_handle)
                            print u'��������ҳ�ɹ���'
                            try:
                                self.parse_detail_page()
                            except (UnknownTableException, UnknownColumnException):
                                # δ֪������������update_status��8
                                self.result_model.set_update_status(8)
                            print "*******************************************"+self.driver.current_window_handle
                            self.driver.close()
                            # time.sleep(1)
                            self.driver.switch_to.window(self.start_page_handle)
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
        except Exception:
            print "# δ֪�쳣��update_status��3"
            traceback.print_exc()
            self.search_model.set_update_status(3)
        self.switch_to_search_page()
        # time.sleep(2)
        # self.driver.back()
        return self.search_model

    def switch_to_search_page(self):
        for handle in self.driver.window_handles:
            if handle != self.start_page_handle:
                self.driver.switch_to.window(handle)
                self.driver.close()
                self.driver.switch_to.window(self.start_page_handle)

    def switch_to_result_page(self):
        pass

    def get_search_result(self):
        if not self.get_ip_status():
            return 4
        # print u'�ȴ���ѯ���'
        search_result = self.find_element(".//*[@class='list-stat']")
        #/html/body/div[4]/div/div[3]
        result_text = search_result.text.strip()
        print result_text
        if result_text == u'>> �������������޲�ѯ��� <<':
            print result_text,'unicorn'
            logging.info(u'��ѯ���0��')
            self.search_model.set_update_status(0)
        else:
            self.search_model.set_update_status(1)

    # �ύ��ѯ����
    def submit_search_request(self):
        self.start_page_handle_bak = None
        self.code_input_box = self.find_element(self.code_input_box_xpath)
        self.code_submit_button = self.find_element(self.code_submit_button_xpath)
        self.code_input_box.clear()  # ��������
        self.code_input_box.send_keys(self.cur_name)  # �����ѯ����
        self.code_submit_button.click()
        iframe = self.find_element("/html/body/div[6]/div/iframe")
        self.screenshot_offset_x = iframe.location['x']
        self.screenshot_offset_y = iframe.location['y']
        self.driver.switch_to.frame(iframe)
        # self.driver.switch_to.default_content()
        # self.validate_image = self.find_element(self.validate_image_xpath)  # ��λ��֤��ͼƬ

        validate_image_save_path = SysConfig.get_validate_image_save_path()  # ��ȡ��֤�뱣��·��
        validate_file_path = self.get_validate_file_path()
        for i in range(SysConfig.max_try_times):
            try:
                self.validate_image = self.find_element(self.validate_image_xpath)  # ��λ��֤��ͼƬ
                self.validate_input_box = self.find_element(self.validate_input_box_xpath)  # ��λ��֤�������
                self.validate_submit_button = self.find_element(self.validate_submit_button_xpath)  # ��λ��֤���ύ��ť
                if i >0:
                    self.validate_top2 = self.validate_image.location['y']              #����վ���ڶ���֮����Ҫ��֤����������ƶ�150������
                    self.driver.execute_script("window.scrollTo(0,"+str(self.validate_top2-150)+");")
                self.download_validate_image(self.validate_image, validate_image_save_path)  # ��ͼ��ȡ��֤��

                validate_code = self.recognize_validate_code(validate_image_save_path,validate_file_path)  # ʶ����֤��
                # print validate_code,type(validate_code)
                self.validate_input_box.clear()  # �����֤�������
                # time.sleep(0.5)
                self.validate_input_box.send_keys(validate_code.decode('gbk'))  # ������֤��
                self.validate_submit_button.click()  # �����������֤�뵯����
                try:
                    self.driver.switch_to.default_content()
                    # self.driver.switch_to.alert.accept()
                    # print u'������'
                    self.find_element('/html/body/div[8]/div[3]/div/button', 1).click()

                    # self.find_element('/html/body/div[8]/div[3]/div/button').click()
                    # time.sleep(0.5)
                    self.driver.switch_to.frame(iframe)
                except:
                    print '*****try*****'
                    break
                # time.sleep(1)
            # except common.exceptions.NoAlertPresentException:
            #     print '*******'
            #     break
            except:
                self.driver.get(self.start_url)    # ���¼���������ʼҳ
                # time.sleep(5)
                i=0
                self.code_input_box = self.find_element(self.code_input_box_xpath)
                self.code_submit_button = self.find_element(self.code_submit_button_xpath)
                self.code_input_box.clear()  # ��������
                self.code_input_box.send_keys(self.cur_name)  # �����ѯ����
                self.code_submit_button.click()
                iframe = self.find_element("/html/body/div[6]/div/iframe")
                self.screenshot_offset_x = iframe.location['x']
                self.screenshot_offset_y = iframe.location['y']
                self.driver.switch_to.frame(iframe)
                # self.driver.switch_to.default_content()
                self.validate_image = self.find_element(self.validate_image_xpath)  # ��λ��֤��ͼƬ

                validate_image_save_path = SysConfig.get_validate_image_save_path()  # ��ȡ��֤�뱣��·��
                validate_file_path = self.get_validate_file_path()
                # time.sleep(1)
        self.driver.switch_to.default_content()
        logging.info(u"�ύ��ѯ����ɹ�")

    # �ж�IP�Ƿ񱻽�
    def get_ip_status(self):
        body_text = self.find_element("/html/body").text
        if body_text.startswith(u'���ķ��ʹ���Ƶ��'):
            return False
        else:
            return True

    # �ж�������ʼҳ�Ƿ���سɹ� {0:�ɹ�, 1:ʧ��}
    def wait_for_load_start_url(self):
        load_result = True
        try:
            self.driver.get(self.start_url)
            self.start_page_handle = self.driver.current_window_handle
        except common.exceptions.TimeoutException:
            pass
        return load_result

    # ��������ҳ ����int�� {0����ѯ�޽����1����ѯ�н���ҽ���ɹ���4��IP������9������ʧ��}
    # def enter_detail_page(self):
    #     res = 9
    #     if not self.get_ip_status():
    #         return 4
    #     search_result = self.find_element('/html/body/form/div/div/dl')
    #     result_text = search_result.text.strip()
    #     if result_text == '':
    #         logging.info(u'��ѯ���0��')
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
    #         logging.info(u"��������ҳ�ɹ�")
    #     return res

    #ҳ����ת
    def parse_detail_page(self):
        tab_list_length = len(self.driver.find_elements_by_xpath(self.tab_list_xpath))
        for i in range(tab_list_length):
            tab = self.find_element("/html/body/div[4]/div/div/div[2]/div[1]/ul/li[%d]" % (i+1))
            tab_text = tab.text
            # print tab_text
            if tab.get_attribute('class') != 'current':
                tab.click()
            self.load_func_dict[tab_text]()

    # ���صǼ���Ϣ
    def load_dengji(self):
        # print u'���صǼ���Ϣ'
        table_div_list_large = self.driver.find_elements_by_xpath("/html/body/div[4]/div/div/div[2]/div[3]")
        for table_div_list in table_div_list_large:
            table_list = table_div_list.find_elements_by_xpath(".//*[@style='display: block;']")
            for table_element in table_list:
                table_desc_element = table_element.find_element_by_xpath("table/tbody/tr[1]/th[1]")
                table_desc = table_desc_element.text.split('\n')[0].strip()
                print table_desc
                if table_desc not in self.load_func_dict:
                    raise UnknownTableException(self.cur_code, table_desc)
                logging.info(u"����%s ..." % table_desc)
                self.load_func_dict[table_desc](table_element)
                self.driver.switch_to.default_content()
                logging.info(u"����%s�ɹ�" % table_desc)

    # ���ػ�����Ϣ
    def load_jiben(self, table_element):
        jiben_template.delete_from_database(self.cur_code)
        # print u'���ػ�����Ϣ'
        # table_element = self.find_element("/html/body/div[4]/div/div/div[2]/div[3]/div[1]/table")
        tr_element_list = table_element.find_elements_by_xpath('table/tbody/tr')
        # print tr_element_list

        values = {}
        for tr_element in tr_element_list[1:]:
            # print tr_element.text
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
        values[u'ʡ��'] = self.province
        jiben_template.insert_into_database(self.cur_code, values)

    # ���عɶ���Ϣ
    def load_gudong(self, table_element):
        # print u'���عɶ���Ϣ'
        condition = False
        gudong_template.delete_from_database(self.cur_code)
        table_element = self.find_element(".//*[@id='investorTable']")
        if len(table_element.find_elements_by_xpath("tbody/tr")) > 3:
            try:
                last_index_element = table_element.find_elements_by_xpath("tbody/tr[last()]/th/ul/li")
                    # ('/html/body/table[2]/tbody/tr/th/a[last()-1]')
                if len(last_index_element) > 3:
                    condition = True
            except:
                pass


                # index_element_list_length = int(last_index_element.text.strip())



            # for i in range(index_element_list_length):
            #     if i > 0:
            #         index_element = self.find_element('/html/body/table[2]/tbody/tr/th/a[%d]' % (i+1))
            #         index_element.click()
            #         table_element = self.find_element("/html/body/table[1]")
            tr_element_list = table_element.find_elements_by_xpath('tbody/tr')
            for tr_element in tr_element_list[2:(len(tr_element_list)-1)]:
                td_element_list = tr_element.find_elements_by_xpath('td')
                values = []
                for td in td_element_list:
                    val = td.text.strip()
                    if val == u'����':
                        # values.append(td.find_element_by_xpath('a').get_attribute('href'))
                        td.find_element_by_xpath('a').click()
                        values.extend(self.load_gudong_detail())
                        # self.driver.switch_to.frame(table_iframe)
                    else:
                        values.append(val)
                values.extend((len(gudong_template.column_list) - len(values))*[''])
                gudong_template.insert_into_database(self.cur_code, values)
            if condition == True:
                # print u'����������������������������������'
                i=3
                while i <= len(last_index_element)-1:
                    table_element.find_element_by_xpath("tbody/tr[last()]/th/ul/li[%d]/a" %i).click()
                    # time.sleep(0.5)
                    tr_element_list = table_element.find_elements_by_xpath('tbody/tr[@style="display: table-row;"]')
                    for tr_element in tr_element_list[2:(len(tr_element_list)-1)]:
                        td_element_list = tr_element.find_elements_by_xpath('td')
                        values = []
                        for td in td_element_list:
                            val = td.text.strip()
                            if val == u'����':
                                # values.append(td.find_element_by_xpath('a').get_attribute('href'))
                                td.find_element_by_xpath('a').click()
                                values.extend(self.load_gudong_detail())
                                # self.driver.switch_to.frame(table_iframe)
                            else:
                                values.append(val)
                        values.extend((len(gudong_template.column_list) - len(values))*[''])
                        gudong_template.insert_into_database(self.cur_code, values)
                    i+=1

                # for i in range(index_element_list_length):
                #     if i > 0:
                #         index_element = self.find_element('/html/body/table[2]/tbody/tr/th/a[%d]' % (i+1))
                #         index_element.click()
                #         table_element = self.find_element("/html/body/table[1]")

        # pass
        # print u'���عɶ���Ϣ�ɹ���'

    def load_gudong_detail(self):
        self.driver.switch_to.window(self.driver.window_handles[-1])
        td_element_list = self.driver.find_elements_by_xpath(".//*[@id='investor']/tbody/tr[4]/td")
        values = []
        for td in td_element_list[1:]:
            values.append(td.text.strip())
        self.driver.close()
        self.driver.switch_to.window(self.detail_page_handle)
        return values

    # ���ر����Ϣ
    def load_biangeng(self, table_element):
        # print u'���ر����Ϣ'
        condition = False
        biangeng_template.delete_from_database(self.cur_code)
        table_element = self.find_element("//*[@id='alterTable']")
        if len(table_element.find_elements_by_xpath("tbody/tr")) > 3:
            try:
                last_index_element = table_element.find_elements_by_xpath("tbody/tr[last()]/th/ul/li")
                if len(last_index_element)>3:
                    condition = True
            except:
                pass
            # last_index_element = self.find_element('/html/body/table[2]/tbody/tr/th/a[last()-1]')
            # index_element_list_length = int(last_index_element.text.strip())
            # for i in range(index_element_list_length):
            #     if i > 0:
            #         index_element = self.find_element('/html/body/table[2]/tbody/tr/th/a[%d]' % (i+1))
            #         index_element.click()
            #         table_element = self.find_element("/html/body/table[1]")
            tr_element_list = table_element.find_elements_by_xpath('tbody/tr')
            for tr_element in tr_element_list[2:(len(tr_element_list)-1)]:
                td_element_list = tr_element.find_elements_by_xpath('td')
                values = []
                for td in td_element_list:
                    val = td.text.strip()
                    if val.endswith(u'����'):
                        td.find_element_by_xpath('a').click()
                        val = td.text.strip()
                        values.append(val[:-4].strip())
                    else:
                        values.append(val.strip())
                biangeng_template.insert_into_database(self.cur_code, values)
            if condition== True:
                # print u'������������������������������', len(last_index_element)
                i=3
                while i <= len(last_index_element)-1:
                    table_element.find_element_by_xpath("tbody/tr[last()]/th/ul/li[%d]/a" %i).click()
                    # time.sleep(0.5)
                    tr_element_list = table_element.find_elements_by_xpath('tbody/tr[@style="display: table-row;"]')
                    for tr_element in tr_element_list:
                        td_element_list = tr_element.find_elements_by_xpath('td')
                        values = []
                        for td in td_element_list:
                            val = td.text.strip()
                            if val.endswith(u'����'):
                                td.find_element_by_xpath('a').click()
                                val = td.text.strip()
                                values.append(val[:-4].strip())
                            else:
                                values.append(val.strip())
                        biangeng_template.insert_into_database(self.cur_code, values)
                    i+=1

        # pass
        # print u'���ر����Ϣ�ɹ�'

    # ���ر�����Ϣ
    def load_beian(self):
        # print u'���ر�����Ϣ'
        # time.sleep(0.5)
        table_div_list_large = self.driver.find_elements_by_xpath("/html/body/div[4]/div/div/div[2]/div[3]")
        for table_div_list in table_div_list_large:
            table_list = table_div_list.find_elements_by_xpath(".//*[@style='display: block;']")
            for table_element in table_list:
                table_desc_element = table_element.find_element_by_xpath("table/tbody/tr[1]/th[1]")
                table_desc = table_desc_element.text.split('\n')[0].strip()
                # print table_desc,'Uni'
                if table_desc not in self.load_func_dict:
                    raise UnknownTableException(self.cur_code, table_desc)
                logging.info(u"����%s ..." % table_desc)
                self.load_func_dict[table_desc](table_element)
                self.driver.switch_to.default_content()
                logging.info(u"����%s�ɹ�" % table_desc)

    # ������Ҫ��Ա��Ϣ
    def load_zhuyaorenyuan(self, table_element):
        condition = False
        zhuyaorenyuan_template.delete_from_database(self.cur_code)
        table_element = self.find_element("//*[@id='memberTable']")
        if len(table_element.find_elements_by_xpath("tbody/tr")) > 3:
            try:
                last_index_element = table_element.find_elements_by_xpath("tbody/tr[last()]/th/ul/li")
                    # ('/html/body/table[2]/tbody/tr/th/a[last()-1]')
                if len(last_index_element) > 3:
                    condition = True
            except:
                pass

            # last_index_element = self.find_element('/html/body/table[2]/tbody/tr/th/a[last()-1]')
            # index_element_list_length = int(last_index_element.text.strip())
            # for i in range(index_element_list_length):
            #     if i > 0:
            #         index_element = self.find_element('/html/body/table[2]/tbody/tr/th/a[%d]' % (i+1))
            #         index_element.click()
            #         table_element = self.find_element("/html/body/table[1]")
            tr_element_list = table_element.find_elements_by_xpath('tbody/tr')
            for tr_element in tr_element_list[2:len(tr_element_list)-1]:
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
            if condition==True:
                # print '@@@@@@@@@@@@@@@'
                i = 3
                while i <= len(last_index_element)-1:
                    table_element.find_element_by_xpath("tbody/tr[last()]/th/ul/li[%d]/a" %i).click()
                    # time.sleep(0.5)
                    tr_element_list = table_element.find_elements_by_xpath('tbody/tr[@style="display: table-row;"]')
                    for tr_element in tr_element_list[2:len(tr_element_list)-1]:
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
                    i += 1
        # pass

    # ���ط�֧������Ϣ
    def load_fenzhijigou(self, table_iframe):

        table_element = self.find_element(".//*[@id='branchTable']")
        if len(table_element.find_elements_by_xpath("tbody/tr")) > 3:
            fenzhijigou_template.delete_from_database(self.cur_code)
        #     last_index_element = self.find_element('/html/body/table[2]/tbody/tr/th/a[last()-1]')
        #     index_element_list_length = int(last_index_element.text.strip())
        #     for i in range(index_element_list_length):
        #         if i > 0:
        #             index_element = self.find_element('/html/body/table[2]/tbody/tr/th/a[%d]' % (i+1))
        #             index_element.click()
        #             table_element = self.find_element("/html/body/table[1]")
            tr_element_list = table_element.find_elements_by_xpath('tbody/tr')
            for tr_element in tr_element_list[2:len(tr_element_list)-1]:
                td_element_list = tr_element.find_elements_by_xpath('td')
                values = []
                for td in td_element_list:
                    val = td.text.strip()
                    values.append(val)
                fenzhijigou_template.insert_into_database(self.cur_code, values)
        # pass

    # ����������Ϣ
    def load_qingsuan(self, table_iframe):
        # table_element = self.find_element("/html/body/table[1]")
        # val_1 = table_element.find_element_by_xpath('tbody/tr[2]/td').text.strip()
        # val_2 = table_element.find_element_by_xpath('tbody/tr[3]/td').text.strip()
        # values = [val_1, val_2]
        # if len(values[0]) != 0 or len(values[1]) != 0:
        #     qingsuan_template.delete_from_database(self.cur_code)
        #     qingsuan_template.insert_into_database(self.cur_code, values)
        pass

    # ���ض�����Ѻ��Ϣ
    def load_dongchandiyadengji(self):

        table_element = self.find_element(".//*[@id='mortageTable']")
        if len(table_element.find_elements_by_xpath("tbody/tr")) > 3:
            dongchandiyadengji_template.delete_from_database(self.cur_code)
            tr_element_list = table_element.find_elements_by_xpath('tbody/tr')
        # self.driver.switch_to.frame(table_iframe)
        # table_element_list = self.driver.find_elements_by_xpath("/html/body/table")
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
        #         tr_element_list = table_element.find_elements_by_xpath('tbody/tr')
            for tr_element in tr_element_list[2:len(tr_element_list)-1]:
                td_element_list = tr_element.find_elements_by_xpath('td')
                values = []
                for td in td_element_list:
                    val = td.text.strip()
                    if val == u'�鿴����':
                        values.append(td.find_element_by_xpath('a').get_attribute('href'))
                    else:
                        values.append(val)
                dongchandiyadengji_template.insert_into_database(self.cur_code, values)
        self.driver.switch_to.default_content()

    # ���ع�Ȩ���ʵǼ���Ϣ
    def load_guquanchuzhidengji(self):

        table_element = self.find_element(".//*[@id='pledgeTable']")
        if len(table_element.find_elements_by_xpath("tbody/tr")) > 3:
            guquanchuzhidengji_template.delete_from_database(self.cur_code)
            tr_element_list = table_element.find_elements_by_xpath('tbody/tr')
        # self.driver.switch_to.frame(table_iframe)
        # table_element_list = self.driver.find_elements_by_xpath("/html/body/table")
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
        #         tr_element_list = table_element.find_elements_by_xpath('tbody/tr')
            for tr_element in tr_element_list[2:len(tr_element_list)-1]:
                td_element_list = tr_element.find_elements_by_xpath('td')
                values = []
                for td in td_element_list:
                    val = td.text.strip()
                    values.append(val)
                guquanchuzhidengji_template.insert_into_database(self.cur_code, values)
        self.driver.switch_to.default_content()

    # ��������������Ϣ
    def load_xingzhengchufa(self):

        table_element = self.find_element(".//*[@id='punishTable']")
        if len(table_element.find_elements_by_xpath("tbody/tr")) > 3:
            xingzhengchufa_template.delete_from_database(self.cur_code)
            tr_element_list = table_element.find_elements_by_xpath('tbody/tr')
        # self.driver.switch_to.frame(table_iframe)
        # table_element_list = self.driver.find_elements_by_xpath("/html/body/table")
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
        #     tr_element_list = table_element.find_elements_by_xpath('tbody/tr')
            for tr_element in tr_element_list[2:len(tr_element_list)-1]:
                td_element_list = tr_element.find_elements_by_xpath('td')
                values = []
                for td in td_element_list:
                    val = td.text.strip()
                    values.append(val)
                xingzhengchufa_template.insert_into_database(self.cur_code, values)
        self.driver.switch_to.default_content()

    # ���ؾ�Ӫ�쳣��Ϣ
    def load_jingyingyichang(self):
        # print 'helloworld'

        table_element = self.find_element("//*[@id='exceptTable']")
        # print table_element.text
        if len(table_element.find_elements_by_xpath("tbody/tr")) > 3:
            jingyingyichang_template.delete_from_database(self.cur_code)
            tr_element_list = table_element.find_elements_by_xpath('tbody/tr')

            for tr_element in tr_element_list[2:len(tr_element_list)-1]:
                td_element_list = tr_element.find_elements_by_xpath('td')
                values = []
                for td in td_element_list:
                    # print td.text
                    val = td.text.strip()
                    values.append(val)
                jingyingyichang_template.insert_into_database(self.cur_code, values)
        self.driver.switch_to.default_content()

    # ��������Υ����Ϣ
    def load_yanzhongweifa(self):

        table_element = self.find_element("//*[@id='blackTable']")
        if len(table_element.find_elements_by_xpath("tbody/tr")) > 3:
            yanzhongweifa_template.delete_from_database(self.cur_code)
        # self.driver.switch_to.frame(table_iframe)
        # table_element_list = self.driver.find_elements_by_xpath("/html/body/table")
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
            tr_element_list = table_element.find_elements_by_xpath('tbody/tr')
            for tr_element in tr_element_list[2:len(tr_element_list)-1]:
                td_element_list = tr_element.find_elements_by_xpath('td')
                values = []
                for td in td_element_list:
                    val = td.text.strip()
                    values.append(val)
                yanzhongweifa_template.insert_into_database(self.cur_code, values)
        self.driver.switch_to.default_content()

    # ���س������Ϣ
    def load_chouchajiancha(self):

        table_element = self.find_element("//*[@id='spotcheckTable']")
        if len(table_element.find_elements_by_xpath("tbody/tr")) > 3:
            chouchajiancha_template.delete_from_database(self.cur_code)
        # self.driver.switch_to.frame(table_iframe)
        # table_element_list = self.driver.find_elements_by_xpath("/html/body/table")
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
            tr_element_list = table_element.find_elements_by_xpath('tbody/tr')
            for tr_element in tr_element_list[2:len(tr_element_list)-1]:
                td_element_list = tr_element.find_elements_by_xpath('td')
                values = []
                for td in td_element_list:
                    val = td.text.strip()
                    values.append(val)
                chouchajiancha_template.insert_into_database(self.cur_code, values)
        self.driver.switch_to.default_content()

if __name__ == '__main__':

    # code_list = ['640103200001999', '640100200099662', '640000100002816', '91640000715044058N',  '640221200010727',  '640103200001999', '640181200008860']
    # searcher = HebeiFirefoxSearcher()
    # searcher.set_config()
    #
    # if searcher.build_driver() == 0:
    #     searcher.search(u"�ӱ�¡��ʯ�����޹�˾", u'ʯ��ׯ������������ԵʳƷ����',u'�Ϻ��ع�������ũ�����޹�˾')
    name_list = [u"�߱�������ͨ�豸�������޹�˾"]
    searcher = HebeiFirefoxSearcher()
    searcher.set_config()
    for name in name_list:
        if searcher.build_driver() == 0:
            searcher.search(name)
