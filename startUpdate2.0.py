# 加***的都是要你自己修改的部分
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
import json
import random
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

#第三方邮件发送模块
def sendEmail(title, receivers, content):

    mail_host = "smtp.***.com"      # SMTP服务器
    mail_user = "***@163.com"                  # 用户名
    mail_pass = "***"               # 授权密码，非登录密码

    sender = '***@163.com'    # 发件人邮箱(最好写全, 不然会失败)

    message = MIMEMultipart('related')
    message['From'] = "{}".format(sender)
    message['To'] = ",".join(receivers)
    message['Subject'] = title

    message_text = MIMEText(content, 'plain', 'utf-8')  # 内容, 格式, 编码
    message.attach(message_text)

    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, 465)  # 启用SSL发信, 端口一般是465
        smtpObj.login(mail_user, mail_pass)  # 登录验证
        smtpObj.sendmail(sender, receivers, message.as_string())  # 发送
        print("Mail has been send successfully.")
    except smtplib.SMTPException as e:
        print(e)

#失败信息
def fail_update(usrname ,email):
    title = '通知：自动健康打码失败！！！'  # 邮件主题
    receivers = ['***@163.com', email]
    content = '现在是' + str(datetime.now()) + '，' + usrname + ' 的打卡失败，请自行进入app查看。' + \
         '\n—这是一条来自DS的温馨提示qwq\n' + \
         ' 无奈学校系统更新，已经无法通过网页查看状态，请自行进入app查看。'
    sendEmail(title, receivers, content)

#成功信息
def success_update(usrname ,email):
    title = '通知：自动健康打码成功'  # 邮件主题
    receivers = ['***@163.com', email]

    content = '现在是' + str(datetime.now()) + '，' + usrname + '打卡成功！耶耶耶！\n' + \
         '\n—这是一条来自DS的温馨提示qwq\n' + \
         ' 无奈学校系统更新，已经无法通过网页查看状态，请自行进入app查看。'
    sendEmail(title, receivers, content)

#中文转unicode(JS)
def unicodeStrInJS(str):
    str=bytes(str,'unicode_escape').decode('utf-8').replace(r'\u',r'\\u').replace(r'\\\u',r'\\u')
    str=bytes(str,'utf-8').decode('unicode_escape')
    return str

# 使用selenium打开网址,然后让用户完成手工登录,再获取cookie
def getAllCookies(usrname, usrpasw):
    #chromeSetting
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')#解决DevToolsActivePort文件不存在的报错
    chrome_options.add_argument('--disable-gpu') #谷歌文档提到需要加上这个属性来规避bug
    chrome_options.add_argument('--hide-scrollbars') #隐藏滚动条, 应对一些特殊页面
    chrome_options.add_argument('blink-settings=imagesEnabled=false') #不加载图片, 提升速度
    chrome_options.add_argument('--headless') #浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    url = 'http://my.lzu.edu.cn:8080/login?service=http://my.lzu.edu.cn'
    # driver = webdriver.Chrome(chrome_options=chrome_options, executable_path='/usr/bin/chromedriver') #utubun18.0.4
    driver = webdriver.Chrome(chrome_options=chrome_options) # win10
    try_times = 0
    while True:
        try:
            driver.get(url=url)
            # 输入用户密码
            userName = driver.find_element_by_xpath('//*[@id="username"]').send_keys('%s'%(usrname))
            userPassword = driver.find_element_by_xpath('//*[@id="password"]').send_keys('%s'%(usrpasw))
            lognInBtn = driver.find_element_by_xpath('//*[@id="loginForm"]/div[3]/button')
            lognInBtn.click()
            # 刷新页面
            driver.refresh()
            c = driver.get_cookies()
            # print(c)
            AllCookies = {}
            # 获取cookie中的name和value,转化成requests可以使用的形式
            for cookie in c:
                AllCookies[cookie['name']] = cookie['value']
            # print(cookies)
            driver.quit()
            return AllCookies
            break 
        except:
            if try_times > 5:
                driver.quit()
                return 0
            else:
                try_times += 1

#开始request
def getST(AllCookies):
    # ST信息
    cookies = {
        'JSESSIONID': AllCookies['JSESSIONID'],
        'SSO_PORTAL_SESSION_KEY': AllCookies['SSO_PORTAL_SESSION_KEY'],
        'iPlanetDirectoryPro': AllCookies['iPlanetDirectoryPro'],
        'CASTGC': AllCookies['CASTGC'],
        'PORTALSID': AllCookies['PORTALSID'],
    }

    headers = {
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'http://my.lzu.edu.cn',
        'Referer': 'http://my.lzu.edu.cn/main;JSESSIONID=48ce1a93-3714-4da4-bbb6-b43c862b7093',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }

    data = {
    'service': 'http://127.0.0.1'
    }

    try_times = 0
    while True:
        if try_times > 5:
            return 0
        response = requests.post('http://my.lzu.edu.cn/api/getST', headers=headers, cookies=cookies, data=data, verify=False)
        if response.status_code == 200:
            data = json.loads(response.text)
            st = data['data']
            return st
        else:
            try_times += 1
            continue

# 获取通行证
def getAccessToken(AllCookies, st, PersonID):
    headers = {
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
        'Content-Type': 'application/json; charset=UTF-8',
        'Accept': '*/*',
        'Referer': 'http://appservice.lzu.edu.cn/dailyReportAll/',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }

    params = (
        ('st', st),
        ('PersonID', PersonID),
    )

    try_times = 0
    while True:
        if try_times > 5:
            return 0
        response = requests.get('http://appservice.lzu.edu.cn/dailyReportAll/api/auth/login', headers=headers, params=params, cookies=cookies, verify=False)
        if response.status_code == 200:
            data = json.loads(response.text)
            accessToken = data['data']['accessToken']
            # print(accessToken)
            return accessToken
        else:
            try_times += 1
            continue

# 获取MD5
def getMD5(AllCookies, accessToken, PersonID, headers):
    data = {
    'cardId': PersonID
    }

    try_times = 0
    while True:
        if try_times > 5:
            return 0
        response = requests.post('http://appservice.lzu.edu.cn/dailyReportAll/api/encryption/getMD5', headers=headers, cookies=cookies, data=data, verify=False)
        if response.status_code ==200:
            data = json.loads(response.text)
            md5 = data['data']
            return md5
        else:
            try_times += 1
            continue

# 获取个人信息
def getInfo(AllCookies, accessToken, PersonID, md5, headers):

    data = {
    'cardId': PersonID,
    'md5': md5
    }

    try_times = 0
    while True:
        if try_times > 5:
            return 0
        response = requests.post('http://appservice.lzu.edu.cn/dailyReportAll/api/grtbMrsb/getInfo', headers=headers, cookies=cookies, data=data, verify=False)
        if response.status_code == 200:
            data = json.loads(response.text)
            return data
        else:
            try_times += 1
            continue

# 打卡提交
def dailyReportAll(AllCookies, data, headers):
    #dataLoading
    bh = data['data']['list'][0]['bh']
    xykh = data['data']['list'][0]['xykh']
    sbr = unicodeStrInJS(data['data']['list'][0]['xm'])
    sjd = data['data']['sjd']
    zcwd = data['data']['list'][0]['zcwd']
    zwwd = data['data']['list'][0]['zwwd']
    wswd = data['data']['list'][0]['wswd']

    print('姓名为：', end="")
    print(data['data']['list'][0]['xm'])
    print('目前温度分别为：', end="")
    print(zcwd, zwwd, wswd)

    #时间段判断并选择温度
    if sjd == '0':
        if zcwd == None:
            zcwd = str(round(random.uniform(35.7,36.6),1))
        else:
            return -1
    elif sjd == '1':
        if zwwd == None:
            zwwd = str(round(random.uniform(35.7,36.6),1))
        else:
            return -1
    elif sjd == '2':
        if wswd == None:
            wswd = str(round(random.uniform(35.7,36.6),1))
        else:
            return -1
    else:
        #非打卡时间段
        return 2

    #printWdData
    print('提交温度分别为：', end="")
    print(zcwd, zwwd, wswd)

    data = {
    'bh': bh,
    'xykh': xykh,
    'twfw': '0',
    'sfzx': '1',
    'sfgl': '0',
    'szsf': '',
    'szds': '',
    'szxq': '',
    'sfcg': '0',
    'cgdd': '',
    'gldd': '',
    'jzyy': '',
    'bllb': '0',
    'sfjctr': '0',
    'jcrysm': '',
    'xgjcjlsj': '',
    'xgjcjldd': '',
    'xgjcjlsm': '',
    'zcwd': zcwd,
    'zwwd': zwwd,
    'wswd': wswd,
    'sbr': sbr,
    'sjd': sjd
    }

    response = requests.post('http://appservice.lzu.edu.cn/dailyReportAll/api/grtbMrsb/submit', headers=headers, cookies=cookies, data=data, verify=False)
    return response.status_code

##
# data
person = [{'usrname': '***','usrpasw': '***','PersonID': '***', 'email': '***@***.com'}]

#计时开始
startTime = datetime.now()

print("=====================================================================================")
for i in range(0, len(person)):
    print('**********************************')
    try_times = 0
    while True:
        if try_times > 5:
            break
        try: 
            usrname = person[i]['usrname']
            usrpasw = person[i]['usrpasw']
            PersonID = person[i]['PersonID']
            email = person[i]['email']
            AllCookies = getAllCookies(usrname, usrpasw)
            if AllCookies == 0:
                try_times += 1
                continue
            st = getST(AllCookies)
            if st == 0:
                try_times += 1
                continue
            cookies = {
                        'iPlanetDirectoryPro': AllCookies['iPlanetDirectoryPro'],
                        }
            accessToken = getAccessToken(cookies, st, PersonID)
            if accessToken == 0:
                try_times += 1
                continue
            headers = {
                        'Connection': 'keep-alive',
                        'Pragma': 'no-cache',
                        'Cache-Control': 'no-cache',
                        'Authorization': accessToken,
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Accept': '*/*',
                        'Origin': 'http://appservice.lzu.edu.cn',
                        'Referer': 'http://appservice.lzu.edu.cn/dailyReportAll/',
                        'Accept-Language': 'zh-CN,zh;q=0.9',
                        }
            md5 = getMD5(cookies, accessToken, PersonID, headers)
            if md5 == 0:
                try_times += 1
                continue
            data = getInfo(cookies, accessToken, PersonID, md5 ,headers)
            if data == 0:
                try_times += 1
                continue
            break        
        except Exception as e:
            try_times += 1
            print(e)
    if try_times >= 5:
            # 发送失败邮件
            print('打卡状态：失败')
            fail_update(data['data']['list'][0]['xm'] ,email)
            print('**********************************')
            continue

    try_times = 0
    while True:
        sig = dailyReportAll(cookies, data, headers)
        if try_times >= 5:
            # 发送失败邮件
            print('打卡状态：失败')
            fail_update(data['data']['list'][0]['xm'] ,email)
            print('**********************************')
            break
        if sig == 404:
            sig = dailyReportAll(cookies, data)
            try_times += 1
        elif sig == 200:
            # 发送成功邮件
            print('打卡状态：成功')
            success_update(data['data']['list'][0]['xm'] ,email)
            print('**********************************')
            break
        else:
            print('打卡状态：已打卡或不在时间内')
            print('**********************************')
            break

print("打卡日期 ：", end="")
print(datetime.now())
print("打卡用时 ：", end="")

#计时结束
endTime = datetime.now()
runTime = endTime - startTime
print(runTime)
print('**********************************')
print("=====================================================================================")


