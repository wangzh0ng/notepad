# !/user/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'w2h'

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
        self.BaseUrl='https://kyfw.12306.cn/otn'
        self.quryUrl ='leftTicket/queryZ'
        self.ThreadLock = threading.Lock()
        self.stopqury = False

    def setNoLogin(self):
        self.loginFlag = False

    def checkAuth(self):
        if self.loginFlag == True:
            self.auth()

    def set_station(self,from_station,to_station,date,trainNo,trainSeat):
        self.from_station=from_station
        self.to_station = to_station
        self.date = date
        self.trainNo = trainNo
        self.trainSeat = trainSeat
        self.fromstation,self.tostation = self.station_name(from_station,to_station)
        print('Date : %s  From %s(%s) To %s(%s)  '%(date, from_station,self.fromstation, to_station, self.tostation),trainNo,trainSeat)

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
            open('D:\\Program Files (x86)\\12306ai\\'+filename, 'wb').write(base64.b64decode(html_pic["image"]))
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

    def loginAuth(self):
        self.login()
        self.auth()

    def login(self):
        if self.ThreadLock.acquire(30):
            try:
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
                r = req.post(url_login, data=form_login, headers=headers, verify=False, proxies=proxy_dict)
                if r.status_code != 200:
                    req.cookies.clear()
                    self.setNoLogin()
                    print('登陆失败！返回代码：', r.status_code)
                    return

                html_login = r.json()
                print(html_login)
                if html_login['result_code'] == 0:
                    self.loginFlag = True
                    print('恭喜您,登录成功!')
                else:
                    print('账号密码错误,登录失败!')
                    exit()
            finally:
                self.ThreadLock.release()
        else:
            exit()


    def query(self):
        if self.stopqury==True:
            exit()
        '''余票查询'''
        #     https://kyfw.12306.cn/otn/leftTicket/queryA?leftTicketDTO.train_date=2019-01-01&leftTicketDTO.from_station=RTQ&leftTicketDTO.to_station=CSQ&purpose_codes=ADULT
        url = '{}/{}?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT'.format(self.BaseUrl,self.quryUrl,
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

            r = requests.get(url, headers=headers, allow_redirects=False,verify=False,proxies=proxy_dict)
            if r.status_code != 200 and r.headers.get('Content-Type')!='application/json;charset=utf-8':
                print(time.strftime('%Y-%m-%d %H:%M:%S'), '查询状态为：',r.status_code)
                return
            print(time.strftime('%Y-%m-%d %H:%M:%S'), '查询....')
            html = r.json()
            if  html['status']==False:
                if  'c_url' in html:
                    self.quryUrl = html['c_url']
                return
            alltrain=[]
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
                        if info[3] in self.trainNo:
                            pass
                        else:
                            continue
                        print(str(num) + '.' + info[3] + '车次还有余票:')
                        print('出发时间:' + info[8] + ' 到达时间:' + info[9] + ' 历时多久:' + info[10] + ' ', end='')
                        seat = {21: '高级软卧', 23: '软卧', 26: '无座', 28: '硬卧', 29: '硬座', 30: '二等座', 31: '一等座', 32: '商务座',
                                33: '动卧'}
                        for j in seat.keys():
                            if info[j] != '无' and info[j] != '':
                                if info[j] == '有':
                                    print(seat[j] + ':有票 ', end='')
                                else:
                                    print(seat[j] + ':有' + info[j] + '张票 ', end='')

                        print('\n')
                        for seatNo in self.trainSeat:
                            No = self.seat[seatNo]
                            if info[No] != '无' and info[No] != '':
                                alltrain.append(info)
                    elif info[1] == '预订':
                        print(str(num) + '.' + info[3] + '车次暂时没有余票')
                    elif info[1] == '列车停运':
                        print(str(num) + '.' + info[3] + '车次列车停运')
                    elif info[1] == '23:00-06:00系统维护时间':
                        print(str(num) + '.' + info[3] + '23:00-06:00系统维护时间')
                    else:
                        print(str(num) + '.' + info[3] + '车次列车运行图调整,暂停发售')
                    num += 1
                for x in self.trainNo:
                    for info in alltrain:
                        if x == info[3]:
                            for seatNo in self.trainSeat:
                                No = self.seat[seatNo]
                                if info[No] != '无' and info[No] != '':
                                    self.stopqury = True
                                    self.orderTicket(parse.unquote(info[0]), self.seat_dict[seatNo])

        except Exception as e:
            print('查询信息有误!请重新输入!')
            errorstr = ''.join(traceback.format_exception(*(sys.exc_info())))
            print(time.strftime('%Y-%m-%d %H:%M:%S'), errorstr)

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

    def orderTicket(self,secretStr,seatNo):
        if self.loginFlag == False:
            self.loginAuth()
        self.order(secretStr)
        content = self.price()
        #passengers = self.passengers(content[8])  # 打印乘客信息

        # 选择乘客和座位
        pass_info = self.chooseseat(content[8],seatNo)


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
        url_confirm = 'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue'
        head_2 = {
            'Host': 'kyfw.12306.cn',
            'Referer': 'https://kyfw.12306.cn/otn/confirmPassenger/initDc',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        }
        html_confirm = req.post(url_confirm, data=form, headers=head_2, verify=False,proxies=proxy_dict).json()
        print(html_confirm)
        if html_confirm['status'] == True and html_confirm['data']['submitStatus']==True :
            print('确认购票成功!')
            exit()
        else:
            self.stopqury = False
            print('确认购票失败!')
            exit()


    def passengers(self, token):
        '''打印乘客信息'''
        # 确认乘客信息
        url_pass = 'https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs'
        head_1 = {
            'Host': 'kyfw.12306.cn',
            'Referer': 'https://kyfw.12306.cn/otn/view/passengers.html',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        }
        form = {
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': token
        }
        global req
        html_pass = req.post(url_pass, data=form, headers=head_1,proxies=proxy_dict, verify=False).json()
        passengers = html_pass['data']['normal_passengers']
        print('\n')
        print('乘客信息列表:')
        #for i in passengers:
        #    print(str(int(i['index_id']) + 1) + '号:' + i['passenger_name'] + ' ', end='')
        #print('\n')
        return passengers

    def chooseseat(self,token,choose_type):
        '''选择乘客和座位'''
        pass_num = len(self.user)  # 购买的乘客数
        pass_dict = []
        for info in self.user:
            pass_name = info['pass_name']  # 名字
            pass_id = info['pass_id']  # 身份证号
            pass_phone = info['pass_phone']  # 手机号码
            pass_type = info['pass_type']  # 证件类型 儿童2，成人1
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
        url_checkorder = 'https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo'
        head_2 = {
            'Host': 'kyfw.12306.cn',
            'Referer': 'https://kyfw.12306.cn/otn/confirmPassenger/initDc',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        }
        html_checkorder = req.post(url_checkorder, data=form, headers=head_2,proxies=proxy_dict, verify=False).json()
        print(html_checkorder)
        if html_checkorder['status'] == True:
            print('检查订单信息成功!')
        else:
            self.stopqury = False
            print('检查订单信息失败!')
            exit()

        return passengerTicketStr, oldpassengerStr, choose_type

    def order(self,secretStr):
        '''提交订单'''
        url_order = 'https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest'
        head_1 = {
            'Host': 'kyfw.12306.cn',
            'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
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
        elif '未完成订单' in  html_order['messages'][0]:
            print('有未处理的订单，请您到[未完成订单]</a>进行处理!')
            os._exit()
        else:
            print('提交订单失败!')
            sys.exit()

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
        html_token = req.post(url_token, data=form, headers=head_1,proxies=proxy_dict, verify=False).text
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
        return train_date, train_no, stationTrainCode, fromStationTelecode, toStationTelecode, leftTicket, purpose_codes, train_location, token, key_check_isChange


if __name__ == '__main__':
    print('*' * 30 + '12306购票' + '*' * 30)
    t12306 = Ticket_12306('13025114177','ledong429')
    t12306.set_station('广州','衡阳','2019-01-27',['K9004','K9076'],['硬卧','二等座','硬座'])
    # 无座  硬座  硬卧  软卧  高级软卧  动卧  二等座  一等座   商务座
    pass_dict=[]
    dict = {
        'pass_name': '',#姓名
        'pass_id': '',#证件号码
        'pass_phone': '',#手机
        'pass_type': '1'# 1成人，2儿童
    }
    pass_dict.append(dict)
    t12306.set_user(pass_dict)  # '95165810'
    checkauth = datetime.datetime.now()
    checklogin = datetime.datetime.now() - datetime.timedelta(hours=7)
    while True:
        hour = int(time.strftime('%H'))
        if hour>=23 or hour <6:
            time.sleep(1)
            t12306.setNoLogin()
            continue
        t = runScriptThread(t12306.query)
        t.start()
        if difftime(checklogin)>60*60:
            checklogin = datetime.datetime.now()
            checkauth = datetime.datetime.now()
            t = runScriptThread(t12306.loginAuth)
            t.start()
        if difftime(checkauth)>3*60-1:
            checkauth = datetime.datetime.now()
            t = runScriptThread(t12306.checkAuth)
            t.start()
        time.sleep(10)
