# coding=gbk

from template.TableTemplate import TableTemplate as TableTemplate


jiben_template = TableTemplate('Registered_Info', u'基本信息')
jiben_template.column_dict = {
    u'统一社会信用代码/注册号': 'RegistrationNo',
    u'注册号/统一社会信用代码': 'RegistrationNo',             # Modified by Jing
    u'注册号': 'RegistrationNo',                        # Modified by Jing
    u'名称': 'EnterpriseName',
    u'省份': 'Province',
    u'法定代表人': 'LegalRepresentative',
    u'经营者': 'Operator',                              # Modified by Jing
    u'类型': 'EnterpriseType',
    u'组成形式': 'CompositionForm',                       # Modified by Jing
    u'成立日期': 'EstablishmentDate',
    u'注册日期': 'EstablishmentDate',                    # Modified by Jing
    u'注册资本': 'RegisteredCapital',
    u'住所': 'ResidenceAddress',
    u'营业期限自': 'ValidityFrom',
    u'营业期限至': 'ValidityTo',
    u'经营期限自': 'ValidityFrom',
    u'经营期限至': 'ValidityTo',
    u'经营范围': 'BusinessScope',
    u'登记机关': 'RegistrationInstitution',
    u'核准日期': 'ApprovalDate',
    u'登记状态': 'RegistrationStatus',
    u'负责人': 'principal',
    u'营业场所': 'businessPlace',
    u'经营场所': 'businessPlace',                        # Modified by Jing
    u'吊销日期': 'RevocationDate',
    u'投资人': 'investor',
    u'投资人信息': 'investor',                              #Modified by Gang
    u'执行事务合伙人': 'ExecutivePartner',
    u'主要经营场所': 'MianBusinessPlace',
    u'合伙期限自': 'PartnershipFrom',
    u'合伙期限至': 'PartnershipTo',
}

gudong_template = TableTemplate('Shareholder_Info', u'股东信息')
gudong_template.column_list = ['Shareholder_Name', 'Shareholder_CertificationType', 'Shareholder_CertificationNo', 'Shareholder_Type', 'Shareholder_Details',
                               'Subscripted_Capital', 'ActualPaid_Capital', 'Subscripted_Method', 'Subscripted_Amount', 'Subscripted_Time', 'ActualPaid_Method',
                               'ActualPaid_Amount', 'ActualPaid_Time']

biangeng_template = TableTemplate('Changed_Announcement', u'变更信息')
biangeng_template.column_list = ['ChangedAnnouncement_Events', 'ChangedAnnouncement_Before', 'ChangedAnnouncement_After', 'ChangedAnnouncement_Date']

zhuyaorenyuan_template = TableTemplate('KeyPerson_Info', u'主要人员信息')
zhuyaorenyuan_template.column_list = ['KeyPerson_No', 'KeyPerson_Name', 'KeyPerson_Position']

jiatingchengyuan_template = TableTemplate('Family_Info', u'参加经营的家庭成员姓名')    # Modified by Jing
jiatingchengyuan_template.column_list = ['FamilyMember_No', 'FamilyMember_Name', 'FamilyMember_Position']

fenzhijigou_template = TableTemplate('Branches', u'分支机构信息')
fenzhijigou_template.column_list = ['Branch_No', 'Branch_RegistrationNo', 'Branch_RegistrationName', 'Branch_RegistrationInstitution']

qingsuan_template = TableTemplate('liquidation_Information', u'清算信息')
qingsuan_template.column_list = ['liquidation_PIC', 'liquidation_Member']

dongchandiyadengji_template = TableTemplate('Chattel_Mortgage', u'动产抵押登记信息')
dongchandiyadengji_template.column_list = ['ChattelMortgage_No', 'ChattelMortgage_RegistrationNo', 'ChattelMortgage_RegistrationDate',
                                           'ChattelMortgage_RegistrationInstitution', 'ChattelMortgage_GuaranteedAmount', 'ChattelMortgage_Status',
                                           'ChattelMortgage_AnnounceDate', 'ChattelMortgage_Details']

guquanchuzhidengji_template = TableTemplate('Equity_Pledge', u'股权出质登记信息')
guquanchuzhidengji_template.column_list = ['EquityPledge_No', 'EquityPledge_RegistrationNo', 'EquityPledge_Pledgor', 'EquityPledge_PledgorID',
                                           'EquityPledge_Amount', 'EquityPledge_Pawnee', 'EquityPledge_PawneeID', 'EquityPledge_RegistrationDate',
                                           'EquityPledge_Status', 'EquityPledge_AnnounceDate', 'EquityPledge_Change']

xingzhengchufa_template = TableTemplate('Administrative_Penalty', u'行政处罚信息')
xingzhengchufa_template.column_list = ['Penalty_No', 'Penalty_Code', 'Penalty_IllegalType', 'Penalty_DecisionContent',
                                       'Penalty_DecisionInsititution', 'Penalty_DecisionDate', 'Penalty_Details']

jingyingyichang_template = TableTemplate('Business_Abnormal', u'经营异常信息')
jingyingyichang_template.column_list = ['Abnormal_No', 'Abnormal_Events', 'Abnormal_DatesIn', 'Abnormal_MoveoutReason',
                                        'Abnormal_DatesOut', 'Abnormal_DecisionInstitution']

yanzhongweifa_template = TableTemplate('Serious_Violations', u'严重违法信息')
yanzhongweifa_template.column_list = ['Serious_No', 'Serious_Events', 'Serious_DatesIn', 'Serious_MoveoutReason',
                                      'Serious_DatesOut', 'Serious_DecisionInstitution']

chouchajiancha_template = TableTemplate('Spot_Check', u'抽查检查信息')
chouchajiancha_template.column_list = ['Check_No', 'Check_Institution', 'Check_Type',
                                       'Check_Date', 'Check_Result', 'Check_Remark']


# def delete_from_db(code):
#     jiben_template.delete_from_database(code)
#     gudong_template.delete_from_database(code)
#     biangeng_template.delete_from_database(code)
#     zhuyaorenyuan_template.delete_from_database(code)
#     fenzhijigou_template.delete_from_database(code)
#     qingsuan_template.delete_from_database(code)
#     dongchandiyadengji_template.delete_from_database(code)
#     guquanchuzhidengji_template.delete_from_database(code)
#     xingzhengchufa_template.delete_from_database(code)
#     jingyingyichang_template.delete_from_database(code)
#     yanzhongweifa_template.delete_from_database(code)
#     chouchajiancha_template.delete_from_database(code)
