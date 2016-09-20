# -*- encoding:utf-8 -*-
import urllib.request
import urllib.parse
import json
import time
import random

token = "24e6c1cbcfdb173dc592de4046a64021"
cmdhist = []

def readCmdHist():
    global cmdhist
    with open("cmdhist.txt") as f:
        cmdhist = json.load(f)
def writeCmdHist():
    global cmdhist
    with open("cmdhist.txt","w") as f:
        json.dump(cmdhist,f)

def getData(url,cmd,user):
    global token,cmdhist
    timestamp = str(int(time.time()))
    
    dlist=[token,timestamp,user,cmd]
    dlist.sort()
    sha1=hashlib.sha1()
    map(sha1.update,dlist)
    signature=sha1.hexdigest()
    
    dt = {"user":user,"signature":signature,"timestamp":timestamp,"cmdstr":cmd}
    dt = json.dumps(dt)
    dt = urllib.parse.urlencode({"data":dt})
    
    r = urllib.request.urlopen(url,data=dt)
    s = r.read().decode('utf-8')
    
    js = json.loads(s)
    if js:
        cmdhist.append(js)
        if len(cmdhist) > 10:
            cmdhist.pop(0)
        writeCmdHist()
        #{"time":webcmd["cmdtime"],"random":webcmd["ran"]}
        timestamp = js["cmdtime"]
        ran = js["ran"]
        dlist=[token,timestamp,user,ran,cmd]
        dlist.sort()
        sha1=hashlib.sha1()
        map(sha1.update,dlist)
        signature=sha1.hexdigest()
        
        
        dt = {"user":user,"signature":signature,"timestamp":timestamp,"cmdstr":cmd,"ran":ran,"delete":"True"}
        dt = json.dumps(dt)
        dt = urllib.parse.urlencode({"data":dt})
        
