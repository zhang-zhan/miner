# -*- coding: UTF-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

'''代码说明：本脚本文件，可以根据一个给定的用户名和密码，获得其对应的新浪微博API的AccessToken
该AccessToken的获取，是利用了Weico.Pro软件的一个漏洞，在其明文显示Token的时候将其截获。
具体的使用方法，参见本代码文件的main函数。
https://api.weibo.com/oauth2/authorize?action=login&display=js&withOfficalFlag=0&response_type=token&regCallback=https%253A%252F%252Fapi.weibo.com%252F2%252Foauth2%252Fauthorize%253Fclient_id%253D2323547071%2526response_type%253Dtoken%2526display%253Djs%2526redirect_uri%253Dhttps%253A%252F%252Fapi.weibo.com%252Foauth2%252Fxd.html%2526from%253D%2526with_cookie%253D&redirect_uri=https%3A%2F%2Fapi.weibo.com%2Foauth2%2Fxd.html&appkey62=3KeSKP&client_id=2323547071&verifyToken=null
'''

import urllib,urllib2,cookielib
import re,json,time,binascii
import base64,rsa
import random

agents = [
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.2; .NET4.0C; .NET4.0E)',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.3 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; rv:22.0) Gecko/20100101 Firefox/22.0',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.71 Safari/537.36',
    'Mozilla/5.0 (Linux; U; Android 4.1.2; zh-cn; L36h Build/10.1.1.A.1.253) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 6_1_3 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Mobile/10B329',
    'Mozilla/5.0 (iPad; CPU OS 6_1_3 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10B329 Safari/8536.25',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.92 Safari/537.1 LBBROWSER'
]

class WeiboLogin:
    def __init__(self, user, pwd, enableProxy = False, proxy=None):
        "初始化WeiboLogin，enableProxy表示是否使用代理服务器，默认关闭"
        self.userName = user
        self.passWord = pwd
        self.enableProxy = enableProxy
        self.proxy = proxy

        self.serverUrl = "https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.15)&_=%d" % (int(time.time())-4)
        self.loginUrl = "https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)&_=%d" % int(time.time())
        self.authUrl = "https://api.weibo.com/oauth2/authorize"

        rnd = random.random() * len(agents)
        self.postHeader = {'User-Agent': agents[int(rnd)],'Pragma':'no-cache'}

    def Login(self):
            "登陆程序"
            self.EnableCookie(self.enableProxy)#cookie或代理服务器配置

            serverTime, nonce, pubkey, rsakv = self.GetServerTime()#登陆的第一步
            postData = self.Encode(self.userName, self.passWord, serverTime, nonce, pubkey, rsakv)#加密用户和密码
            pData = urllib.urlencode(postData)#网络编码

            req = urllib2.Request(self.loginUrl, pData, self.postHeader)
            #print "Posted request data with length of %d ..." % len(postData)
            result = urllib2.urlopen(req)#登陆的第二步
            resp = result.read()
            #print resp
            resp = json.loads(resp,encoding='utf-8')

            retcode = int( resp.get('retcode') )
            if retcode>0:   #登陆异常
                reason = resp.get('reason')
                info = "[%d]%s" % (retcode,reason)
                print(info)
                raise RuntimeError(info)

            self.ticket = resp.get('ticket')

            postData = self.authorize()
            pData = urllib.urlencode(postData)#网络编码
            header = dict()

            header.update(self.postHeader)
            refer = "https://api.weibo.com/oauth2/authorize?verifyToken=null&withOfficalFlag=0&response_type=token&action=login&display=js&regCallback=%s&client_id=%s&userId=%s&redirect_uri=%s&appkey62=%s&ticket=%s"
            header['Referer'] = refer % (postData['regCallback'],postData['client_id'],postData['userId'],postData['redirect_uri'],postData['appkey62'],postData['ticket'])
            req = urllib2.Request(self.authUrl, pData, header)
            result = urllib2.urlopen(req) #Authorize
            resp = result.read()

            flag = 'access_token":"'
            starts = resp.find(flag)
            if starts<0:
                print(resp)
                raise RuntimeError('Access Token not found in the respone content!')

            return resp[starts+len(flag):starts+len(flag)+32]

    def EnableCookie(self, enableProxy):
        "Enable cookie & proxy (if needed)."
        cookiejar = cookielib.LWPCookieJar()#建立cookie
        cookie_support = urllib2.HTTPCookieProcessor(cookiejar)

        if enableProxy:
            proxy_support = urllib2.ProxyHandler({'http':self.proxy})#使用代理
            opener = urllib2.build_opener(proxy_support, cookie_support, urllib2.HTTPHandler)
            print "Proxy enabled"
        else:
            opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)

        urllib2.install_opener(opener)#构建cookie对应的opener

    def GetServerTime(self):
        "Get server time and nonce, which are used to encode the password"
        serverData = urllib2.urlopen(self.serverUrl).read()#得到网页内容
        try:
            serverTime, nonce, pubkey, rsakv = sServerData(serverData)#解析得到serverTime，nonce等
            return serverTime, nonce, pubkey, rsakv
        except:
            raise RuntimeError('Get server time & nonce error!')

    def Encode(self, userName, passWord, serverTime, nonce, pubkey, rsakv):
        "Used to generate POST data"
        encodedUserName = GetUserName(userName)#用户名使用base64加密
        encodedPassWord = getPassword(passWord, serverTime, nonce, pubkey)#目前密码采用rsa加密
        postParam = {
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'su': encodedUserName,
            'sp': encodedPassWord,
            'servertime': serverTime,
            'nonce': nonce,
            'rsakv': rsakv,
            'entry': 'openapi',
            'gateway': '1',
            'from': '',
            'savestate': '0',
            'userticket': '1',
            'ssosimplelogin': '1',
            'vsnf': '1',
            'vsnval': '',
            'service': 'miniblog',
            'pwencode': 'rsa2',
            'sr':'800*600',
            'encoding': 'UTF-8',
            'cdult':'2',
            'domain':'weibo.com',
            'prelt': '95',
            'returntype': 'TEXT'
        }
        return postParam

    def authorize(self):
        postParam = {
            'userId':self.userName,
            'passwd':'',
            'ticket':self.ticket,

            'regCallback':'https://api.weibo.com/2/oauth2/authorize?response_type=token&display=js&redirect_uri=https://api.weibo.com/oauth2/xd.html&client_id=2323547071',
            'appkey62':'3KeSKP',
            'client_id':'2323547071',

            'redirect_uri':'https://api.weibo.com/oauth2/xd.html',
            'action':'login',
            'display':'js',
            'transport':'',
            'withOfficalFlag':'0',
            'withOfficalAccount':'',
            'scope':'',
            'isLoginSina':'',
            'response_type':'token',
            'state':'',
            'from':'',
            'verifyToken':'null'
        }
        return postParam

def sServerData(serverData):
    "Search the server time & nonce from server data"
    p = re.compile('\((.*)\)')
    jsonData = p.search(serverData).group(1)
    data = json.loads(jsonData)
    serverTime = str(data['servertime'])
    nonce = data['nonce']
    pubkey = data['pubkey']#
    rsakv = data['rsakv']#
    #print "Server time is:", serverTime
    #print "Nonce is:", nonce
    return serverTime, nonce, pubkey, rsakv

def sRedirectData(text):
    p = re.compile('location\.replace\([\'"](.*?)[\'"]\)')
    loginUrl = p.search(text).group(1)
    print 'loginUrl:',loginUrl
    return loginUrl

def GetUserName(userName):
    "Used to encode user name"
    userNameTemp = urllib.quote(userName)
    userNameEncoded = base64.encodestring(userNameTemp)[:-1]
    return userNameEncoded

def getPassword(password, servertime, nonce, pubkey):
    rsaPublickey = int(pubkey, 16)
    key = rsa.PublicKey(rsaPublickey, 65537) #创建公钥
    message = str(servertime) + '\t' + str(nonce) + '\n' + str(password) #拼接明文js加密文件中得到
    passwd = rsa.encrypt(message, key) #加密
    passwd = binascii.b2a_hex(passwd) #将加密信息转换为16进制。
    return passwd

def getToken(uname, pwd):
    sim = WeiboLogin(uname,pwd)
    token = sim.Login()
    return token

if __name__ == '__main__':
    users = {
        'wsi_gucas@sina.com': 'wsi_208'
    }
    for uname,pwd in users.iteritems():
        token = getToken(uname,pwd)
        print token