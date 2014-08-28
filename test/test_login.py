# -*- coding: UTF-8 -*-
__author__ = 'Peter_Howe<haobibo@gmail.com>'

import urllib2
import cookielib
import time
import re
import json
import urllib
import base64
import binascii

import rsa

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
        self.postHeader = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.3 Safari/537.36'}

    def Login(self):
            "登陆程序"
            self.EnableCookie(self.enableProxy)#cookie或代理服务器配置

            serverTime, nonce, pubkey, rsakv = self.GetServerTime()#登陆的第一步
            postData = self.Encode(self.userName, self.passWord, serverTime, nonce, pubkey, rsakv)#加密用户和密码

            req = urllib2.Request(self.loginUrl, postData, self.postHeader)
            #print "Posted request data with length of %d ..." % len(postData)
            result = urllib2.urlopen(req)#登陆的第二步
            resp = result.read()
            #print resp

            '''
            resp = json.loads(resp,encoding='utf-8')
            retcode = int( resp.get('retcode') )
            if retcode>0:   #登陆异常
                reason = resp.get('reason')
                raise RuntimeError("[%d]%s" % (retcode,reason))
            '''

            try:
                loginUrl = sRedirectData(resp)#解析重定位结果
                urllib2.urlopen(loginUrl)
            except Exception as e:
                raise e

            print 'Login sucess!'
            return True

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
        postPara = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'userticket': '1',
            'ssosimplelogin': '1',
            'vsnf': '1',
            'vsnval': '',
            'su': encodedUserName,
            'service': 'miniblog',
            'servertime': serverTime,
            'nonce': nonce,
            'pwencode': 'rsa2',
            'sp': encodedPassWord,
            'encoding': 'UTF-8',
            'prelt': '115',
            'rsakv': rsakv,
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META'
        }
        postData = urllib.urlencode(postPara)#网络编码
        return postData

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
        postData = urllib.urlencode(postParam)#网络编码
        return postData

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

if __name__ == '__main__':
    weiboLogin = WeiboLogin('quizuser@sina.com', 'MicroGoogle')
    if weiboLogin.Login() == True:
        print "登陆成功！"

    htmlContent = urllib2.urlopen("http://weibo.com/box").read()
    print htmlContent