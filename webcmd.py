# -*- coding: utf-8 -*-
"""
CMD命令
"""
import web
import sendmail
import json
import random
web.config.debug = False  


class WebCmd():
    
    def GET(self):
        #sendmail.sendMail()
        
        
    def POST(self):
        #sendmail.sendMail()
        Delete = False
        str_json = web.data() #获得post来的数据
        try:
            js = json.loads(str_json,"utf-8")
            user = js["user"]
            signature=js["signature"]
            timestamp=js["timestamp"]
            cmdstrin=js["cmdstr"]
            if "delete" in js:
                Delete = True
                ran = js["ran"]
        except:
            return u"---"
        webinfo = datas.select("webinfo.json",{"User":["=",user]})
        try:
            #自己的token
            token=webinfo["token"] #token
        except:
            return "----"
        #字典序排序
        if Delete:
            list=[token,timestamp,user,ran]
        else:
            list=[token,timestamp,user]
        list.sort()
        sha1=hashlib.sha1()
        map(sha1.update,list)
        hashcode=sha1.hexdigest()
        #sha1加密算法     
        if hashcode != signature:
            return "check error"
        timestamp_t = int(timestamp)
        if Delete:
            webcmd = datas.delete("webcmd.json",{"User":["=",user],"timestamp":["=",timestamp_t],"random":["=",ran]})
        else:
            webcmd = datas.select("webcmd.json",{"User":["=",user]})
            cmdlist = []
            for cmds in webcmd:
                if timestamp_t < webcmd["cmdtime"]:
                    if webcmd["cmdstr"] == cmdstrin:
                        cmdlist.append({"time":str(webcmd["cmdtime"]),"random":webcmd["ran"]})
                    
        return json.dumps(cmdlist)
        