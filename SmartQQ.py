"""
By clouduan  dyzplus@gmail.com
Refer:http://www.scienjus.com/webqq-analysis-1/
网页入口：http://w.qq.com
"""
import json
import time
from NetHandler import HttpHandler
from PIL import Image

AppID = 501004106
ClientID = 53999199
PTWebQQ = ''
PSessionID = ''
VFWebQQ = ''
UIN = ''


class QQ(HttpHandler):
    def __init__(self):
        super().__init__()
        self.friend_list = {}
        self.current_user_info = {}
        self.GroupNameList = {}
        self.GroupCodeList = {}

    def login(self, retries=5):
        global AppID, PTWebQQ, VFWebQQ, PSessionID, UIN
        try:
            self.Download(
                'https://ssl.ptlogin2.qq.com/ptqrshow?appid=501004106&e=0&l=M&s=5&d=72&v=4&t=0.1')
            print("获取二维码成功,请扫描：")
            Image._show(Image.open('./qrcode.png'))
            while True:
                html = self.Get(
                    "https://ssl.ptlogin2.qq.com/ptqrlogin?ptqrtoken={ptqrtoken}&webqq_type=10&remember_uin=1&login2qq=1&aid=501004106&u1=http%3A%2F%2Fw.qq.com%2Fproxy.html%3Flogin2qq%3D1%26webqq_type%3D10&ptredirect=0&ptlang=2052&daid=164&from_ui=1&pttype=1&dumy=&fp=loginerroralert&action=0-0-32750&mibao_css=m_webqq&t=undefined&g=1&js_type=0&js_ver=10197&login_sig=&pt_randsalt=0".format(
                        ptqrtoken=self.get_qrtoken(self.s.cookies['qrsig'])))
                ret = html.split("'")
                if ret[1] == '65' or ret[1] == '0':  # 65: QRCode 失效, 0: 验证成功, 66: 未失效, 67: 验证中
                    break
                time.sleep(2)

            if ret[1] != '0':
                return self.login(retries - 1)

            print("二维码已扫描，正在登陆")

            self.Get(ret[5])  # 必须从“访问ret返回的数据中的状态接口链接获得的cookies”中获得'ptewbqq'参数
            PTWebQQ = self.s.cookies['ptwebqq']
            loginError = 3
            while loginError > 0:
                try:
                    html = self.Post('http://d1.web2.qq.com/channel/login2', {
                        'r': json.dumps({
                            "ptwebqq": PTWebQQ,
                            "clientid": ClientID,
                            "psessionid": PSessionID,
                            "status": "online"})
                    }, refer='http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2')
                    ret = json.loads(html)
                    html2 = self.Get(
                        "http://s.web2.qq.com/api/getvfwebqq?ptwebqq={0}&clientid={1}&psessionid={2}&t=0.1".format(
                            PTWebQQ,
                            ClientID,
                            PSessionID),
                        refer='http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2')
                    ret2 = json.loads(html2)
                    loginError = 0
                except Exception as e:
                    loginError -= 1
                    print("Error:%s" % e)  # todo
                if ret['retcode'] != 0 or ret2['retcode'] != 0:
                    raise ValueError("Login Retcode=" + str(ret['retcode']))

                VFWebQQ = ret2['result']['vfwebqq']
                PSessionID = ret['result']['psessionid']
                UIN = ret['result']['uin']
                print("登陆成功,QQ号：{0} ".format(ret['result']['uin']))
        except Exception as e:
            print("Error occur: %s ,retrying..." % e)
            return self.login(retries=retries - 1)

    def get_friends_class(self):
        """
        获取 好友分类列表
        :return:dict={"friends": [{"uin": 41837138855, "flag": 4, "categories": 1}], "info": [{"uin": 41837138855, "nick": "\u6635\u79f0", "flag": 4751942, "face": 603}], "categories": [{"sort": 2, "name": "\u540c\u5b66", "index": 0}], "marknames": [{"uin": 37761915054, "markname": "\u5907\u6ce8", "type": 0}], "vipinfo": [{"u": 20191343597, "is_vip": 0, "vip_level": 0}]}
        """
        try:
            html = self.Post('http://s.web2.qq.com/api/get_user_friends2', {
                'r': json.dumps(
                    {
                        "vfwebqq": VFWebQQ,
                        "hash": self.gethash(str(UIN), str(PTWebQQ))
                    }
                )
            }, refer='http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1')
            ret = json.loads(html)
            if ret['retcode'] != 0:
                print("Error: %s" % ret)
            friends = ret['result']
            # self.friend_list[] =
            return friends
        except Exception as e:
            print("Error:%s" % e)
            return

    def get_friends_online(self):
        """
        获取 在线的好友
        :return:dict={"status": "online", "uin": 3017767504, "client_type": 1}
        """
        try:
            html = self.Get(
                'http://d1.web2.qq.com/channel/get_online_buddies2?vfwebqq={0}&clientid={1}&psessionid={2}&t=0.1'.format(
                    VFWebQQ,
                    ClientID,
                    PSessionID),
                refer='http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2')
            ret = json.loads(html)
            if ret['retcode'] != 0:
                print("Error: %s" % ret)
            online_friends = ret['result']
            return online_friends
        except Exception as e:
            print("Error %s" % e)
            return None

    def get_friend_info(self, tuin):
        """
        获取 特定好友的详细信息
        :param tuin:
        :return:dict={"province": "", "occupation": "\u5176\u4ed6", "blood": 5, "college": "aaa", "constel": 7, "personal": "\u8fd9\u662f\u7b80\u4ecb", "shengxiao": 11, "email": "352323245@qq.com", "mobile": "139 ********", "nick": "ABCD", "gender": "female", "city": "", "country": "\u4e4d\u5f97", "stat": 20, "face": 603, "uin": 1382902354, "allow": 1, "phone": "110", "birthday": {"month": 8, "year": 1895, "day": 15}, "vip_info": 6, "homepage": "\u6728\u6709"}
        """
        try:
            html = self.Get(
                'http://s.web2.qq.com/api/get_friend_info2?tuin={0}&vfwebqq={1}&clientid={2}&psessionid={3}&t=0.1'.format(
                    str(tuin),
                    VFWebQQ,
                    ClientID,
                    PSessionID))
            ret = json.loads(html)
            if ret['retcode'] != 0:
                print("Error: %s" % ret)
            info = ret['result']
            info['account'] = self.uin_to_account(tuin)
            self.friend_list[tuin] = info
            return info
        except Exception as e:
            print("Error:%s" % e)
            return

    def get_groups_list(self):
        """
        获取 群列表
        :return:dict={"gmasklist": [],
        "gnamelist": [{"flag": 167864331,"name": "群名","gid": 14611812014,"code": 3157131718}],"gmarklist": [{"uin": 18796074161,"markname": "备注"}]}
        """
        try:
            html = self.Post('http://s.web2.qq.com/api/get_group_name_list_mask2', {
                'r': '{{"vfwebqq":"{0}","hash":"{1}"}}'.format(str(VFWebQQ), self.gethash(str(UIN), str(PTWebQQ)))
            }, refer='http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2')
            ret = json.loads(html)

            if ret['retcode'] != 0:
                raise ValueError("retcode error when getting group list: retcode=" + str(ret['retcode']))
            for t in ret['result']['gnamelist']:
                self.GroupNameList[str(t["name"])] = t["gid"]
                self.GroupCodeList[int(t["gid"])] = int(t["code"])
            return self.GroupNameList
        except Exception as e:
            print("Error %s" % e)
            return

    def get_group_info(self, gcode):
        """
        获取 特定群的详细信息
        :param:gcode:群列表中获取的code
        :return:dict={"stats": [{"stat": 50, "uin": 2146674552, "client_type": 1}], "minfo": [{"nick": "\u6635\u79f0", "city": "", "gender": "male", "country": "\u4e2d\u56fd", "province": "\u5317\u4eac", "uin": 3623536468}], "vipinfo": [{"is_vip": 1, "vip_level": 6, "u": 2390929289}], "cards": [{"card": "\u7fa4\u540d\u7247", "muin": 3623536468}], "ginfo": {"memo": "\u7fa4\u516c\u544a\uff01", "class": 25, "owner": 3509557797, "name": "\u7fa4\u540d\u79f0", "gid": 2419762790, "level": 4, "option": 2, "fingermemo": "", "createtime": 1231435199, "face": 0, "flag": 721421329, "code": 591539174, "members": [{"muin": 3623536468, "mflag": 192}]}}
        """
        try:
            html = self.Get(
                'http://s.web2.qq.com/api/get_group_info_ext2?gcode={0}&vfwebqq={1}&t=0.1'.format(gcode, VFWebQQ),
                refer='http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1')
            ret = json.loads(html)
            if ret['retcode'] != 0:
                print("Error:%s" % ret)
                return
            return ret['result']
        except Exception as e:
            print("Error:%s" % e)
            return

    def get_discuss_list(self):
        """
        获取 讨论组列表
        :return:dict={"dnamelist": [{"name": "讨论组名", "did": 167864331}]}
        """
        try:
            html = self.Get(
                'http://s.web2.qq.com/api/get_discus_list?clientid=53999199&psessionid={0}&vfwebqq={1}&t=0.1'.format(
                    PSessionID, VFWebQQ))
            ret = json.loads(html)
            if ret['retcode'] != 0:
                print("Error:%s" % ret)
                return
            return ret['result']
        except Exception as e:
            print("Error:%s" % e)
            return

    def get_discuss_info(self, did):
        """
        获取 特定讨论组的详细信息
        :param:did
        :return:dict={"mem_status": [{"status": "online", "client_type": 7, "uin": 3253160543}], "info": {"discu_name": "***", "mem_list": [{"ruin": 1301948, "mem_uin": 3466696377}], "did": 236426547}, "mem_info": [{"nick": "Hey", "uin": 3466696377}]}
        """
        try:
            html = self.Get(
                'http://d1.web2.qq.com/channel/get_discu_info?did={0}&psessionid={1}&vfwebqq={2}&clientid=53999199&t=0.1'.format(
                    did, PSessionID, VFWebQQ),
                refer='http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1')
            ret = json.loads(html)
            if ret['retcode'] != 0:
                print("Error:%s" % ret)
                return
            return ret['result']
        except Exception as e:
            print("Error:%s" % e)
            return

    def get_recent_msglist(self):
        """
        获取 最近会话列表
        :return:json={"result": [{"type": 1, "uin": 2856977416}], "retcode": 0}
        """
        try:
            html = self.Get('http://d1.web2.qq.com/channel/get_recent_list2', {
                'r': json.dumps(
                    {
                        "vfwebqq": VFWebQQ,
                        "clientid": ClientID,
                        "psessionid": PSessionID
                    }
                )
            })
            ret = json.loads(html)
            if ret['retcode'] != 0:
                print("Error:%s" % ret)
                return
            print(ret['result'])
            return ret['result']
        except Exception as e:
            print("Error:%s" % e)
            return

    def get_current_user(self):
        """
        获取 当前登录用户信息
        :return:dict
        """
        try:
            ret = json.loads(self.Get(
                'http://s.web2.qq.com/api/get_self_info2&t=0.1',
                refer='http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1'))
            if ret['retcode'] != 0:
                print("Error:%s" % ret)
                return
            self.current_user_info = ret['result']
            return ret['result']
        except Exception as e:
            print("Error:%s" % e)
            return

    def msg_check(self, errors=5):
        """
        查询 有无新消息
        :param errors:
        :return:
        """
        global PTWebQQ
        while True:
            try:
                ret = self.Post('https://d1.web2.qq.com/channel/poll2', {
                    'r': json.dumps(
                        {
                            "ptwebqq": PTWebQQ,
                            "clientid": ClientID,
                            "psessionid": PSessionID,
                            "key": ""
                        }
                    )
                }, refer='https://d1.web2.qq.com/cfproxy.html?v=20151105001&callback=1')
            except Exception as e:
                print("Error:%s" % e)
                return self.msg_check()
            retcode = ret['retcode']

            # 开始检验,心跳包轮询
            if retcode == 0:  #
                print(ret)
                if 'result' in ret:
                    return ret['result']
                else:
                    continue
            if retcode == 116:  # 更新ptwebqq
                PTWebQQ = ret['p']
                continue
            if retcode == 102:  # 无消息?
                continue
            if retcode == 100006:
                print('post数据有误')
                break
            if errors < 0:  # 103等其他错误:
                print("轮询错误超过5次")
                return None
            else:
                return self.msg_check(errors - 1)

    def msg_analyse(self):
        """
        处理 消息
        :return:
        """
        msg = self.msg_check()

    def send_friend_msg(self, user_id, msg):
        """
        发送消息 给好友
        :param user_id:
        :param msg:
        :return:
        """
        html = self.Post('http://d1.web2.qq.com/channel/send_buddy_msg2', {
            'r': json.dumps(
                {
                    "to": user_id,
                    "content": str([
                        "msg",
                        [
                            "font",
                            {
                                "name": "宋体",
                                "size": 10,
                                "style": [0, 0, 0],
                                "color": "000000"
                            }
                        ]
                    ]),
                    "face": 522,
                    "clientid": ClientID,
                    "msg_id": 65890001,
                    "psessionid": PSessionID
                })}, refer='http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2')
        ret = json.loads(html)
        if ret['msg'] != 'send ok':
            print('Error:%s' % ret)
            return
        return True

    def send_group_msg(self, group_uin, msg):  # send_qun_msg
        """
        :param group_uin:
        :param msg:
        :return:
        """
        html = self.Post('http://d1.web2.qq.com/channel/send_qun_msg2', {
            'r': json.dumps(
                {
                    "to": group_uin,
                    "content": str([
                        "msg",
                        [
                            "font",
                            {
                                "name": "宋体",
                                "size": 10,
                                "style": [0, 0, 0],
                                "color": "000000"
                            }
                        ]
                    ]),
                    "face": 522,
                    "clientid": ClientID,
                    "msg_id": 65890001,
                    "psessionid": PSessionID
                })}, refer='http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2')
        ret = json.loads(html)
        if ret['msg'] != 'send ok':
            print('Error:%s' % ret)
            return
        return True

    def send_discuss_msg(self, did, msg):
        """
        :param did:
        :param msg:
        :return:
        """
        html = self.Post('http://d1.web2.qq.com/channel/send_discu_msg2', {
            'r': json.dumps(
                {
                    "to": did,
                    "content": str([
                        "msg",
                        [
                            "font",
                            {
                                "name": "宋体",
                                "size": 10,
                                "style": [0, 0, 0],
                                "color": "000000"
                            }
                        ]
                    ]),
                    "face": 522,
                    "clientid": ClientID,
                    "msg_id": 65890001,
                    "psessionid": PSessionID
                })}, refer='http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2')
        ret = json.loads(html)
        if ret['msg'] != 'send ok':
            print('Error:%s' % ret)
            return
        return True

    # 工具类函数声明
    def uin_to_account(self, uin):
        """
        转化 uin编号->qq号
        :param uin:int
        :return qq_account: str
        :ret ={"retcode": 0,"result": {"uiuin": "account": 3524125,"uin": 1382902354}}
        """
        try:
            html = self.Get(
                'http://s.web2.qq.com/api/get_friend_uin2?tuid={0}&type=1&vfwebqq={1}&t=0.1'.format(uin, VFWebQQ),
                refer='http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2')
            ret = json.loads(html)
            if ret['retcode'] != 0:
                print("Error:%s" % ret)
                return
            return ret['result']['account']
        except Exception as e:
            print("Error:%s" % e)
            return

    def get_qrtoken(self, qrsig):
        e = 0
        for i in qrsig:
            e += (e << 5) + ord(i)
        return 2147483647 & e

    def gethash(self, selfuin, ptwebqq):
        selfuin += ""
        N = [0, 0, 0, 0]
        for T in range(len(ptwebqq)):
            N[T % 4] = N[T % 4] ^ ord(ptwebqq[T])
        U = ["EC", "OK"]
        V = [0, 0, 0, 0]
        V[0] = int(selfuin) >> 24 & 255 ^ ord(U[0][0])
        V[1] = int(selfuin) >> 16 & 255 ^ ord(U[0][1])
        V[2] = int(selfuin) >> 8 & 255 ^ ord(U[1][0])
        V[3] = int(selfuin) & 255 ^ ord(U[1][1])
        U = [0, 0, 0, 0, 0, 0, 0, 0]
        U[0] = N[0]
        U[1] = V[0]
        U[2] = N[1]
        U[3] = V[1]
        U[4] = N[2]
        U[5] = V[2]
        U[6] = N[3]
        U[7] = V[3]
        N = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"]
        V = ""
        for T in range(len(U)):
            V += N[U[T] >> 4 & 15]
            V += N[U[T] & 15]
        return V