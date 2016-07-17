# -*- coding: utf-8 -*-
import random
import hashlib
import base64
import web
import action
import datas
import time
from sae.mail import send_mail
web.config.debug = False  


class SetMail():
    """
    """
    def GET(self):
        data = web.input()
        mdata=data.mdata
        signature=data.signature
        mdata = base64.b64decode(mdata)
        mdata = mdata.split()
        userinfo = datas.select("userinfo.json",{"User":["=",user]})
        mdata.append(userinfo[0]["random"])
        sha1=hashlib.sha1()
        map(sha1.update,mdata)
        hexcode = sha1.hexdigest()
        if hexcode != signature:
            return u"验证失败"
        user = mdata[0]
        mail = mdata[2]
        if int(mdata[1]) > time.time():
            datas.update("userinfo.json",{"User":user,"mail":s},"User")
            retstr = u"邮箱修改成功"
        else:
            retstr = u"验证失败，请重新验证"
    def POST(self):
        return None
        
        
        
def CheckMail(user,mail,state):
    userinfo = datas.select("userinfo.json",{"User":["=",user]})
    sendmail = True
    if mail == u"-l":
        if userinfo and "mail" in userinfo:
            retstr = userinfo["mail"]
        else:
            retstr = u"您没有设置邮箱"
        sendmail = False
    else:
        ran = random.random()
        strtimestamp = [user,str(int(time.time())),mail,str(ran)]
        if userinfo:
            if "mail" in userinfo:
                mailaddr = userinfo["mail"]
                if mailaddr == mail:
                    retstr = u"新邮箱和原邮箱相同，未修改设置"
                    sendmail = False
            else:
                mailaddr = mail
            datas.update("userinfo.json",{"random":strtimestamp[3]},{"User":['=',user]})
        else:
            mailaddr = mail
            datas.insert("userinfo.json",{"User":user,"random":strtimestamp[3]})
        if sendmail:
            url = ""
            url += "mdata=" + base64.b64encode(' '.join(strtimestamp))
            sha1=hashlib.sha1()
            map(sha1.update,strtimestamp)
            url += "&signature=" + sha1.hexdigest()
            
            send_mail(mailaddr, u"邮箱验证", "\n" + url,\
              ("smtp.sina.com", 25, "nnzyserver@sina.com", "FtwjR02y84OKUmxg", False))
            retstr = u"已经发送验证邮件到" + mailaddr + "请到邮箱验证"
        