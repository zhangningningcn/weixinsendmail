# -*- coding: utf-8 -*-
import os,sys,io
import json,time,hashlib
import web,lxml
from lxml import etree
import datas,sendmail
#import setmail
from datetime import datetime

web.config.debug = True  


class WeixinInterface():
    """
    微信解析函数
    """
    def __init__(self):
        self.app_root = os.path.dirname(__file__)
        self.templates_root = os.path.join(self.app_root, 'templates')
        self.render = web.template.render(self.templates_root)
        self.comands = {"mail":sendmail.saveMailData,"setmail":setmail,\
        "now":timenow,"myid":disuserid,"help":cmdhelp}

    def GET(self):
        #获取输入参数
        data = web.input()
        signature=data.signature
        timestamp=data.timestamp
        nonce=data.nonce
        try:
            echostr=data.echostr
        except:
            return
        #自己的token
        token=config.weixintoken #这里改写你在微信公众平台里输入的token
        #字典序排序
        list=[token,timestamp,nonce]
        list.sort()
        sha1=hashlib.sha1()
        map(sha1.update,list)
        hashcode=sha1.hexdigest()
        #sha1加密算法        

        #如果是来自微信的请求，则回复echostr
        if hashcode == signature:
            return echostr
    def POST(self):        
        str_xml = web.data() #获得post来的数据
        xml = etree.fromstring(str_xml)#进行XML解析
        msgType=xml.find("MsgType").text
        fromUser=xml.find("FromUserName").text
        toUser=xml.find("ToUserName").text
        
        sret = ""
        if msgType == "text":
            content=xml.find("Content").text#获得用户所输入的内容
            if not content:
                return self.render.reply_text(fromUser,toUser,int(time.time()),u"无法解析重新输入")
            now = time.time()
            ss = datas.select("sesion.json",{"User":['=',fromUser]})
            state = 0
            if ss:
                tm = ss[0]["Time"]
                if tm > now:
                    state = ss[0]["State"]
            if state != 0:
                msgsplit = [ss[0]["App"],content]
            else:
                msgsplit = content.split(None,1)
            if not msgsplit:
                return self.render.reply_text(fromUser,toUser,int(time.time()),u"无法解析重新输入")
            if msgsplit[0] in self.comands:
                if len(msgsplit) == 1:
                    msgsplit.append("-l")
                sret = self.comands[msgsplit[0]](msgsplit[1],fromUser,state)
            else:
                #sret = u"暂时不支持\""+msgsplit[0]+u"\"命令"
                if len(msgsplit) < 2:
                    return self.render.reply_text(fromUser,toUser,int(time.time()),u"无法解析重新输入")
                sret = sendmail.saveMailData(content,fromUser,3)
        elif msgType == "event":
            content=xml.find("Event").text#获得Event
            if content == "subscribe":#(订阅)
                sret = config.welcome
            elif content == "unsubscribe":#(取消订阅)
                datas.delete("userinfo.json",{"User":["=",fromUser]})
        elif msgType == "image":
            sret = u"暂时不支持图片功能"
        elif msgType == "voice":
            sret = u"暂时不支持语音功能"
        elif msgType == "video":
            sret = u"暂时不支持视频功能"
        elif msgType == "shortvideo":
            sret = u"暂时不支持小视频功能"
        elif msgType == "location":
            sret = u"暂时不支持地理位置功能"
        elif msgType == "link":
            sret = u"暂时不支持链接功能"
        return self.render.reply_text(fromUser,toUser,int(time.time()),sret)
        
class Myfile:
    def __init__(self):
        self.s = ""
    def write(self,s):
        if isinstance(s,str):
            self.s += s
        else:
            raise TypeError
    def getvalue(self):
        return self.s
def setmail(s,user,state):
    """
    格式：setmail name@serveraddr
    设置默认邮箱地址
    """
    if '@' in s:
        datas.insert("userinfo.json",{"User":user,"mail":s},"User")
        return u"邮件已保存"
    else:
        if s == '-l':
            userinfo = datas.select("userinfo.json",{"User":["=",user]})
            if userinfo:
                return userinfo[0]["mail"]
        return u"邮件格式不正确，请重新设置"
def disuserid(s,user,state):
    """
    格式：myid
    查看自己的weixinID
    """
    return user

def timenow(s,user,state):
    """
    格式：now
    显示当前日期时间(北京时间)
    """
    now = datetime.now()
    return now.strftime(u"%Y-%m-%d %H:%M:%S")
def cmdhelp(s,user,state):
    """
    格式：help
    显示帮助列表
    
    格式：help 命令
    显示命令的详细帮助
    """
    if s == "-l":
        helpinfo = """
        命令列表：
        mail:添加定时邮件
        setmail:设置默认邮箱
        now:显示当前日期时间
        myid:显示微信ID
        help:显示帮助列表
        help 命令:显示命令详细信息 例如：help mail 
        """
        return helpinfo
    else:
        cmddict = {"mail":"sendmail.saveMailData","setmail":"weixinapp.setmail",\
        "now":"weixinapp.timenow","myid":"weixinapp.disuserid","help":"weixinapp.cmdhelp"}
        if s in cmddict.keys():
            # 重定向stdout获取help信息到变量
            ioFile = Myfile()
            oldstdout = sys.stdout
            sys.stdout = ioFile
            help(cmddict[s])
            sys.stdout = oldstdout
            sret = ioFile.getvalue()
            #sret = sret[sret.index(os.linesep)+1:]
            index = 0
            for i in range(3):
                index = sret.index("\n",index)+1
            sret = sret[index:]
        else:
            sret = u"没有该命令的帮助"
        return sret