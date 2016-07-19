# -*- encoding: utf-8 -*-
import urllib
import urllib2
import hashlib
#import lxml
#from lxml import etree
import json
import sys
sys.path.append("..")
import config

filelist = []
stamp = ""
HOSTURL = 'http://localhost:8080'

def getfiles():
    global filelist
    global stamp
    djs = {"passwd":config.passwdDatas,"type":"getfilelist"}
    dstr=json.dumps(djs)
    urldata = urllib2.urlopen(HOSTURL + '/cron/kvbackup',dstr)
    dataxml = urldata.read()
    filelist = dataxml.split(",")
    stamp = filelist[0]
    filelist = filelist[1:]


def doAction(type,index):
    sha1=hashlib.sha1()
    sha1.update(stamp)
    sha1.update(config.keyUserRestore)
    hashcode=sha1.hexdigest()
    #hashcode="12354646"
    djs = {"passwd":config.passwdDatas,"filename":filelist[index],"hashcode":hashcode}
    if type == '1':
        djs["type"] = "getfile"
    elif type == '2':
        djs["type"] = "restore"

    dstr=json.dumps(djs)
    urldata = urllib2.urlopen(HOSTURL + '/cron/kvbackup',dstr)
    dataxml = urldata.read()
    return dataxml


if __name__ == "__main__":
    # while True:
    while True:
        #print(u"请选择类型：\n".encode("utf-8").decode("gbk"))
        print(u"请选择类型：".encode("gbk"))
        print(u"1. 下载文件链接".encode("gbk"))
        print(u"2. 恢复文件".encode("gbk"))
        print(u"3. 备份文件".encode("gbk"))
        type = raw_input()
        if type == '1' or type == '2' or type == '3':
            break
        print(u"选择不正确，请重新选择".encode("gbk"))

    if type == '3':
        urldata = urllib2.urlopen(HOSTURL + '/cron/kvbackup')
        dataxml = urldata.read()
        print(dataxml.decode("utf-8").encode("gbk"))
        raw_input()
    else:
        while True:
            print(u"请选择文件：\n".encode("gbk"))
            getfiles()
            for i,name in enumerate(filelist,1):
                print (str(i) + ". " + name)

            filindex = int(raw_input()) - 1
            if filindex >= 0 and filindex < len(filelist):
                break
            print(u"选择不正确，请重新选择".encode("gbk"))

        ret = doAction(type,filindex)
        print(ret.decode("utf-8").encode("gbk"))
        raw_input()

