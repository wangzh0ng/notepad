# !/user/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'wzh'

import requests,os, re, time, ssl
from urllib import parse
import base64
import urllib3

urllib3.disable_warnings() #不显示警告信息
ssl._create_default_https_context = ssl._create_unverified_context
req = requests.Session()

proxy_dict = {
    "https": "https://127.0.0.1:8088"
}
class Ding_12306(object):
    def __init__(self,username,password):
        self.username = username
        self.password = password
        self.seat = { '无座':26, '硬卧':28 , '硬座':29, '二等座':30, '一等座':31}
        self.loginFlag = False

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
        if html_pic['result_code'] == "0":
            open('D:\\Program Files (x86)\\12306ai\\img\\pic.jpg', 'wb').write(base64.b64decode(html_pic["image"]))
        else:
            print('验证码有误！')
            if num > 3:
                exit()
            return self.pass_captcha(num + 1)

        try:
            result = requests.get(url_captcha + "img/pic.jpg", verify=False).text
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
        url = 'https://kyfw.12306.cn/otn/leftTicket/queryA?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT'.format(
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
                                self.order(info[0] )
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

    def order(self, result, train_number, from_station, to_station, date,secretStr):
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



if __name__ == '__main__':
    print('*' * 30 + '12306购票' + '*' * 30)
    d12306 = Ding_12306('13786169829','ledong429')
    d12306.set_station('东莞','长沙','2019-01-02',{'K9064':['硬座'],'K9076':['硬卧']})
    d12306.query()
    #d12306.login()



