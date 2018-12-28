# !/user/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'wzh'

import requests,os, re, time, ssl
from urllib import parse
import base64,uuid
import urllib3,datetime
import threading,traceback,sys

urllib3.disable_warnings() #不显示警告信息
ssl._create_default_https_context = ssl._create_unverified_context
req = requests.Session()

proxy_dict = {
    "https": "https://127.0.0.1:8088"
}

def difftime(t):
    tt =datetime.datetime.now()-t
    return float("%.4f"%float("%d.%d"%(tt.seconds,tt.microseconds)))

class runScriptThread(threading.Thread):
    def __init__(self, funcName,*args):
        threading.Thread.__init__(self)
        self.args = args
        self.funcName = funcName

    def run(self):
        try:
            if len(self.args) == 0:
                self.funcName()
            else:
                self.funcName(*(self.args))
        except Exception as e:
            errorstr=''.join(traceback.format_exception(*(sys.exc_info())))
            print(time.strftime('%Y-%m-%d %H:%M:%S'),errorstr)
            raise

class Ticket_12306(object):
    def __init__(self,username,password):
        self.username = username
        self.password = password
        self.seat = { '无座':26, '硬卧':28 , '硬座':29, '二等座':30, '一等座':31}
        self.seat_dict = {'无座': '1', '硬座': '1', '硬卧': '3', '软卧': '4', '高级软卧': '6', '动卧': 'F', '二等座': 'O', '一等座': 'M',
                     '商务座': '9'}
        self.loginFlag = False

    def setNoLogin(self):
        self.loginFlag = False

    def checkAuth(self):
        if self.loginFlag == True:
            self.auth()

    def set_station(self,from_station,to_station,date,trainNo):
        self.from_station=from_station
        self.to_station = to_station
        self.date = date
        self.trainNo = trainNo
        self.trainKey = trainNo.keys()
        self.fromstation,self.tostation = self.station_name(from_station,to_station)
        print('Date : %s  From %s(%s) To %s(%s)  '%(date, from_station,self.fromstation, to_station, self.tostation))

    def station_name(self, from_station,to_station):
        '''获取车站简拼'''
        if not os.path.isfile("station_name.js"):
            print('下载取车站简拼...')
            station_url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js'
            html = requests.get(station_url, verify=False, proxies=proxy_dict).text
            open("station_name.js", 'w',encoding="utf-8").write(html)
        else:
            html = open("station_name.js", encoding="utf-8").read()

        result = html.split('@')[1:]
        dict = {}
        for i in result:
            key = str(i.split('|')[1])
            value = str(i.split('|')[2])
            dict[key] = value
        return dict[from_station],dict[to_station]

    def pass_captcha(self,num=0):
        '''自动识别验证码'''
        print('正在识别验证码...')
        global req
        req.cookies.clear()
        url_pic = 'https://kyfw.12306.cn/passport/captcha/captcha-image64?login_site=E&module=login&rand=sjrand&1545882313593&_=1545882311000'
        url_captcha = 'http://127.0.0.1:6666/'
        headers = {
            'Host': 'kyfw.12306.cn',
            'Referer': 'https://kyfw.12306.cn/otn/login/init',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        }
        html = req.get(url_pic, headers=headers, verify=False, proxies=proxy_dict)
        if 'result_code' in html.text:
            pass
        else:
            print('取验证码有误！重试',num)
            return self.pass_captcha(num + 1)

        #print(html.text)
        html_pic = html.json()
        filename = "img/%s.jpg" % uuid.uuid4()
        if html_pic['result_code'] == "0":
            open('C:\\12306\\github\\12306-Captcha-Crack\\'+filename, 'wb').write(base64.b64decode(html_pic["image"]))
        else:
            print('验证码有误！',num)
            if num > 3:
                exit()
            return self.pass_captcha(num + 1)

        try:
            result = requests.get(url_captcha + filename, verify=False).text
            print(num,'验证码：',result)
            if result.index(',') == -1:
                print('未别验证码！')
                if num > 3:
                    exit()
                return self.pass_captcha(num + 1)
            return result
        except :
            print('Sorry!验证码自动识别网址已失效~')
            exit()

    def captcha(self, answer):
        url_check = 'https://kyfw.12306.cn/passport/captcha/captcha-check'
        headers = {
            'Host': 'kyfw.12306.cn',
            'Referer': 'https://kyfw.12306.cn/otn/login/init',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        }
        # 验证验证码
        form_check = {
            'answer': answer,
            'login_site': 'E',
            'rand': 'sjrand'
        }
        global req
        html_check = req.post(url_check, data=form_check, headers=headers, verify=False,proxies=proxy_dict).json()
        print(html_check)
        if html_check['result_code'] == '4':
            print('验证码校验成功!')
            return True
        else:
            print('验证码校验失败!',answer)
            return False

    def login(self):
        self.checklogin = datetime.datetime.now()
        scuess = True
        url_login = 'https://kyfw.12306.cn/passport/web/login'
        headers = {
            'Host': 'kyfw.12306.cn',
            'Referer': 'https://kyfw.12306.cn/otn/login/init',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        }
        for x in range(3):
            answer_num = self.pass_captcha()
            scuess = self.captcha(answer_num)
            if scuess == True:
                break
        if scuess == False:
            print('验证码校验失败三次!')
            exit()

        '''登录账号'''
        form_login = {
            'username': self.username,
            'password': self.password,
            'appid': 'otn'
        }
        global req
        html_login = req.post(url_login, data=form_login, headers=headers, verify=False,proxies=proxy_dict).json()
        print(html_login)
        if html_login['result_code'] == 0:
            self.loginFlag = True
            print('恭喜您,登录成功!')
        else:
            print('账号密码错误,登录失败!')
            exit()

    def query(self):
        '''余票查询'''
        #     https://kyfw.12306.cn/otn/leftTicket/queryA?leftTicketDTO.train_date=2019-01-01&leftTicketDTO.from_station=RTQ&leftTicketDTO.to_station=CSQ&purpose_codes=ADULT
        hour = int(time.strftime('%H'))
        if hour >= 23 or hour<6:
            url ='https://kyfw.12306.cn/otn/leftTicket/queryZ'
        else:
            url ='https://kyfw.12306.cn/otn/leftTicket/queryA'
        url = url +'?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT'.format(
            self.date, self.fromstation, self.tostation)
        headers = {
            'Host': 'kyfw.12306.cn',
            'If-Modified-Since': '0',
            'Pragma': 'no-cache',
            'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        try:
            r = requests.get(url, headers=headers, verify=False,proxies=proxy_dict)
            if r.status_code != 200:
                return
            html = r.json()
            result = html['data']['result']
            if result == []:
                print('很抱歉,没有查到符合当前条件的列车!')
                exit()
            else:
                #print(date + from_station + '-' + to_station + '查询成功!')
                # 打印出所有车次信息
                num = 1  # 用于给车次编号,方便选择要购买的车次
                for i in result:
                    info = i.split('|')
                    if info[0] != '' and info[0] != 'null':
                        if info[3] in self.trainKey:
                            pass
                        else:
                            continue
                        print(str(num) + '.' + info[3] + '车次还有余票:')
                        print('出发时间:' + info[8] + ' 到达时间:' + info[9] + ' 历时多久:' + info[10] + ' ', end='')
                        seat = {21: '高级软卧', 23: '软卧', 26: '无座', 28: '硬卧', 29: '硬座', 30: '二等座', 31: '一等座', 32: '商务座',
                                33: '动卧'}
                        #from_station_no = info[16]
                        #to_station_no = info[17]
                        for j in seat.keys():
                            if info[j] != '无' and info[j] != '':
                                if info[j] == '有':
                                    print(seat[j] + ':有票 ', end='')
                                else:
                                    print(seat[j] + ':有' + info[j] + '张票 ', end='')
                        print('\n')
                        for seatNo in self.trainNo[info[3]]:
                            No = self.seat[seatNo]
                            if  info[No] != '无' and info[No]  != '':
                                #self.order(info[0] )
                                print('订订订订订订订订订订订')
                    elif info[1] == '预订':
                        print(str(num) + '.' + info[3] + '车次暂时没有余票')
                    elif info[1] == '列车停运':
                        print(str(num) + '.' + info[3] + '车次列车停运')
                    elif info[1] == '23:00-06:00系统维护时间':
                        print(str(num) + '.' + info[3] + '23:00-06:00系统维护时间')
                    else:
                        print(str(num) + '.' + info[3] + '车次列车运行图调整,暂停发售')
                    num += 1
            return result
        except Exception as err:
            print(err)
            print('查询信息有误!请重新输入!')
            exit()

    def auth(self):
        url_uam = 'https://kyfw.12306.cn/passport/web/auth/uamtk'
        url_uamclient = 'https://kyfw.12306.cn/otn/uamauthclient'
        head_1 = {
            'Host': 'kyfw.12306.cn',
            'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        }
        '''验证uamtk和uamauthclient'''
        # 验证uamtk
        form = {
            'appid': 'otn',
            # '_json_att':''
        }
        global req
        html_uam = req.post(url_uam, data=form, headers=head_1, verify=False,proxies=proxy_dict).json()
        print(html_uam)
        if html_uam['result_code'] == 0:
            print('恭喜您,uam验证成功!')
        else:
            print('uam验证失败!')
            exit()
        # 验证uamauthclient
        tk = html_uam['newapptk']

        form = {
            'tk': tk,
            # '_json_att':''
        }
        html_uamclient = req.post(url_uamclient, data=form, headers=head_1, verify=False,proxies=proxy_dict).json()
        print(html_uamclient)
        if html_uamclient['result_code'] == 0:
            print('恭喜您,uamclient验证成功!')
        else:
            print('uamclient验证失败!')
            exit()

    def orderTicket(self,secretStr):
        if self.loginFlag == False:
            self.login()
        self.order(secretStr)
        content = self.price()
        passengers = self.passengers(content[8])  # 打印乘客信息
        # 选择乘客和座位
        pass_info = self.chooseseat(passengers, content[8])
        # 查看余票数
        self.leftticket(content[0], content[1], content[2], pass_info[2], content[3], content[4], content[5],
                         content[6],
                         content[7], content[8])

        # 最终确认订单
        self.confirm(pass_info[0], pass_info[1], content[9], content[5], content[6], content[7], content[8])

    def confirm(self, passengerTicketStr, oldpassengerStr, key_check_isChange, leftTicket, purpose_codes,
                train_location, token):
        '''最终确认订单'''
        form = {
            'passengerTicketStr': passengerTicketStr,
            'oldPassengerStr': oldpassengerStr,
            'randCode': '',
            'key_check_isChange': key_check_isChange,
            'choose_seats': '',
            'seatDetailType': '000',
            'leftTicketStr': leftTicket,
            'purpose_codes': purpose_codes,
            'train_location': train_location,
            '_json_att': '',
            'whatsSelect': '1',
            'roomType': '00',
            'dwAll': 'N',
            'REPEAT_SUBMIT_TOKEN': token
        }
        global req
        html_confirm = req.post(self.url_confirm, data=form, headers=self.head_2, verify=False).json()
        print(html_confirm)
        if html_confirm['status'] == True:
            print('确认购票成功!')
        else:
            print('确认购票失败!')
            exit()

    def passengers(self, token):
        '''打印乘客信息'''
        # 确认乘客信息
        form = {
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': token
        }
        global req
        html_pass = req.post(self.url_pass, data=form, headers=self.head_1, verify=False).json()
        passengers = html_pass['data']['normal_passengers']
        print('\n')
        print('乘客信息列表:')
        for i in passengers:
            print(str(int(i['index_id']) + 1) + '号:' + i['passenger_name'] + ' ', end='')
        print('\n')
        return passengers

    def chooseseat(self, passengers, passengers_name, choose_seat, token):
        '''选择乘客和座位'''
        seat_dict = {'无座': '1', '硬座': '1', '硬卧': '3', '软卧': '4', '高级软卧': '6', '动卧': 'F', '二等座': 'O', '一等座': 'M',
                     '商务座': '9'}
        choose_type = seat_dict[choose_seat]
        pass_num = len(self.user)  # 购买的乘客数
        pass_dict = []
        for i in self.user:
            info = None
            for j in  passengers:
                if j['passenger_id_no']==i:
                    info = j
                    break
            if info == None:
                print('用户不存在：',i)
                continue
            pass_name = info['passenger_name']  # 名字
            pass_id = info['passenger_id_no']  # 身份证号
            pass_phone = info['mobile_no']  # 手机号码
            pass_type = info['passenger_type']  # 证件类型
            dict = {
                'choose_type': choose_type,
                'pass_name': pass_name,
                'pass_id': pass_id,
                'pass_phone': pass_phone,
                'pass_type': pass_type
            }
            pass_dict.append(dict)

        num = 0
        TicketStr_list = []
        for i in pass_dict:
            if pass_num == 1:
                TicketStr = i['choose_type'] + ',0,1,' + i['pass_name'] + ',' + i['pass_type'] + ',' + i[
                    'pass_id'] + ',' + i['pass_phone'] + ',N'
                TicketStr_list.append(TicketStr)
            elif num == 0:
                TicketStr = i['choose_type'] + ',0,1,' + i['pass_name'] + ',' + i['pass_type'] + ',' + i[
                    'pass_id'] + ',' + i['pass_phone'] + ','
                TicketStr_list.append(TicketStr)
            elif num == pass_num - 1:
                TicketStr = 'N_' + i['choose_type'] + ',0,1,' + i['pass_name'] + ',' + i['pass_type'] + ',' + i[
                    'pass_id'] + ',' + i['pass_phone'] + ',N'
                TicketStr_list.append(TicketStr)
            else:
                TicketStr = 'N_' + i['choose_type'] + ',0,1,' + i['pass_name'] + ',' + i['pass_type'] + ',' + i[
                    'pass_id'] + ',' + i['pass_phone'] + ','
                TicketStr_list.append(TicketStr)
            num += 1

        passengerTicketStr = ''.join(TicketStr_list)
        print(passengerTicketStr)

        num = 0
        passengrStr_list = []
        for i in pass_dict:
            if pass_num == 1:
                passengerStr = i['pass_name'] + ',' + i['pass_type'] + ',' + i['pass_id'] + ',1_'
                passengrStr_list.append(passengerStr)
            elif num == 0:
                passengerStr = i['pass_name'] + ',' + i['pass_type'] + ',' + i['pass_id'] + ','
                passengrStr_list.append(passengerStr)
            elif num == pass_num - 1:
                passengerStr = '1_' + i['pass_name'] + ',' + i['pass_type'] + ',' + i['pass_id'] + ',1_'
                passengrStr_list.append(passengerStr)
            else:
                passengerStr = '1_' + i['pass_name'] + ',' + i['pass_type'] + ',' + i['pass_id'] + ','
                passengrStr_list.append(passengerStr)
            num += 1

        oldpassengerStr = ''.join(passengrStr_list)
        print(oldpassengerStr)
        form = {
            'cancel_flag': '2',
            'bed_level_order_num': '000000000000000000000000000000',
            'passengerTicketStr': passengerTicketStr,
            'oldPassengerStr': oldpassengerStr,
            'tour_flag': 'dc',
            'randCode': '',
            'whatsSelect': '1',
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': token
        }
        global req
        html_checkorder = req.post(self.url_checkorder, data=form, headers=self.head_2, verify=False).json()
        print(html_checkorder)
        if html_checkorder['status'] == True:
            print('检查订单信息成功!')
        else:
            print('检查订单信息失败!')
            exit()

        return passengerTicketStr, oldpassengerStr, choose_type

    def leftticket(self, train_date, train_no, stationTrainCode, choose_type, fromStationTelecode, toStationTelecode,
                   leftTicket, purpose_codes, train_location, token):
        '''查看余票数量'''
        form = {
            'train_date': train_date,
            'train_no': train_no,
            'stationTrainCode': stationTrainCode,
            'seatType': choose_type,
            'fromStationTelecode': fromStationTelecode,
            'toStationTelecode': toStationTelecode,
            'leftTicket': leftTicket,
            'purpose_codes': purpose_codes,
            'train_location': train_location,
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': token
        }
        global req
        html_count = req.post(self.url_count, data=form, headers=self.head_2, verify=False).json()
        print(html_count)
        if html_count['status'] == True:
            print('查看余票数量成功!')
            count = html_count['data']['ticket']
            print('此座位类型还有余票' + count + '张~')
        else:
            print('查看余票数量失败!')
            exit()

    def order(self,secretStr):
        '''提交订单'''
        url_order = 'https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest'
        head_1 = {
            'Host': 'kyfw.12306.cn',
            'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        }
        back_train_date = time.strftime("%Y-%m-%d", time.localtime())
        form = {
            'secretStr': secretStr,  # 'secretStr':就是余票查询中你选的那班车次的result的那一大串余票信息的|前面的字符串再url解码
            'train_date': self.date,  # 出发日期(2018-04-08)
            'back_train_date': back_train_date,  # 查询日期
            'tour_flag': 'dc',  # 固定的
            'purpose_codes': 'ADULT',  # 成人票
            'query_from_station_name': self.from_station,  # 出发地
            'query_to_station_name': self.to_station,  # 目的地
            'undefined': ''  # 固定的
        }
        global req
        html_order = req.post(url_order, data=form, headers=head_1, verify=False,proxies=proxy_dict).json()
        print(html_order)
        if html_order['status'] == True:
            print('恭喜您,提交订单成功!')
        else:
            print('提交订单失败!')
            exit()

    def set_user(self, user):
        self.user = user

    def price(self):
        '''打印票价信息'''
        form = {
            '_json_att': ''
        }
        global req
        head_1 = {
            'Host': 'kyfw.12306.cn',
            'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        }
        url_token = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
        html_token = req.post(url_token, data=form, headers=head_1, verify=False).text
        token = re.findall(r"var globalRepeatSubmitToken = '(.*?)';", html_token)[0]
        leftTicket = re.findall(r"'leftTicketStr':'(.*?)',", html_token)[0]
        key_check_isChange = re.findall(r"'key_check_isChange':'(.*?)',", html_token)[0]
        train_no = re.findall(r"'train_no':'(.*?)',", html_token)[0]
        stationTrainCode = re.findall(r"'station_train_code':'(.*?)',", html_token)[0]
        fromStationTelecode = re.findall(r"'from_station_telecode':'(.*?)',", html_token)[0]
        toStationTelecode = re.findall(r"'to_station_telecode':'(.*?)',", html_token)[0]
        date_temp = re.findall(r"'to_station_no':'.*?','train_date':'(.*?)',", html_token)[0]
        timeArray = time.strptime(date_temp, "%Y%m%d")
        timeStamp = int(time.mktime(timeArray))
        time_local = time.localtime(timeStamp)
        train_date_temp = time.strftime("%a %b %d %Y %H:%M:%S", time_local)
        train_date = train_date_temp + ' GMT+0800 (中国标准时间)'
        train_location = re.findall(r"tour_flag':'.*?','train_location':'(.*?)'", html_token)[0]
        purpose_codes = re.findall(r"'purpose_codes':'(.*?)',", html_token)[0]
        print('token值:' + token)
        print('leftTicket值:' + leftTicket)
        print('key_check_isChange值:' + key_check_isChange)
        print('train_no值:' + train_no)
        print('stationTrainCode值:' + stationTrainCode)
        print('fromStationTelecode值:' + fromStationTelecode)
        print('toStationTelecode值:' + toStationTelecode)
        print('train_date值:' + train_date)
        print('train_location值:' + train_location)
        print('purpose_codes值:' + purpose_codes)
        price_list = re.findall(r"'leftDetails':(.*?),'leftTicketStr", html_token)[0]
        # price = price_list[1:-1].replace('\'', '').split(',')
        print('票价:')
        for i in eval(price_list):
            # p = i.encode('latin-1').decode('unicode_escape')
            print(i + ' | ', end='')
        return train_date, train_no, stationTrainCode, fromStationTelecode, toStationTelecode, leftTicket, purpose_codes, train_location, token, key_check_isChange



if __name__ == '__main__':
    print('*' * 30 + '12306购票' + '*' * 30)
    t12306 = Ticket_12306('13786169829','ledong429')
    t12306.set_station('东莞','长沙','2019-01-02',{'K9064':['硬座'],'K9076':['硬卧']})
    t12306.set_user(['430423198204290015'])#'E95165810'
    checkauth = datetime.datetime.now()
    checklogin = datetime.datetime.now() - datetime.timedelta(hours=7)
    while True:
        hour = int(time.strftime('%H'))
        '''if hour>=23 or hour <6:
            time.sleep(1)
            d12306.setNoLogin()
            continue'''
        t = runScriptThread(t12306.query)
        t.start()
        if difftime(checkauth)>3*60:
            checkauth = datetime.datetime.now()
            t = runScriptThread(t12306.checkAuth)
            t.start()
        if difftime(checklogin)>6*60:
            checklogin = datetime.datetime.now()
            checkauth = datetime.datetime.now()
            t = runScriptThread(t12306.login)
            t.start()

        time.sleep(100000)
    #d12306.query()




