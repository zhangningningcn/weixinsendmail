# -*- coding: utf-8 -*-

#本文件使用两个kvdb变量：kvdbchg,kvdatastamp 不是 json 结尾的


import os,io,os.path
import re,json,zipfile,hashlib
import web
from Crypto.Cipher import AES
from Crypto import Random


try:
    import config
except ImportError:
    import configDemo as config
    

# import config

import sae.kvdb
kv = sae.kvdb.Client()
from sae.storage import Bucket
from datetime import datetime
import time

class KVBackUp():
    
    def GET(self):
        return MakeBackup()
    def POST(self):
        bucket = Bucket('backup')
        str_data = web.data() #获得post来的数据
        js = json.loads(str_data,"utf-8")
        if "passwd" in js.keys():
            if js["passwd"] != config.passwdDatas:
                return u"密码错误"
        else:
            return u"请求格式不正确"
        if "type" in js.keys():
            if "filename" in js.keys():
                stamp = kv.get("kvdatastamp")
                sha1=hashlib.sha1()
                sha1.update(stamp)
                sha1.update(config.keyUserRestore)
                hashcode=sha1.hexdigest()
                if not "hashcode" in js.keys():
                    return u"请求类型不正确"
                if hashcode != js["hashcode"]:
                    return u"验证失败"
                if js["type"] == "restore":
                    return ReadZipFile(js["filename"])
                elif js["type"] == "getfile":
                    return bucket.generate_url(js["filename"])
                else:
                    return u"请求类型不正确"
            elif js["type"] == "getfilelist":
                filelist = []
                stamp = str(int(time.time()))
                filelist.append(stamp)
                kv.set("kvdatastamp",stamp)
                for finf in bucket.list():
                    filelist.append(str(finf[u'name']))
                return ",".join(filelist)
            else:
                return u"请求格式不正确"
                
        else:
            return u"请求格式不正确"
            
        # return None

def FindKVDBKeys():
    """
    搜索kvdb key
    """
    datas = set()
    filenames = os.listdir(".")
    for name in filenames:
        if name[-3:] == ".py" and os.path.isfile(name):
            file = io.open(name,mode='r',encoding='utf-8',errors='ignore')
            while True:
                lines = file.readlines(10000)
                if not lines:
                    break;
                for line in lines:
                    m = re.match(r".*datas\..*\"(.*\.json)\".*",line)
                    if m:
                        datas.add(m.group(1))
    return datas
def WriteZipFile(filename):
    """
    保存所有kvdb数据，压缩成zip然后aes cbc加密
    """
    FileBuffer = io.BytesIO()
    datalist = FindKVDBKeys()
    if datalist:
        zfile = zipfile.ZipFile(FileBuffer,mode='w')
        for data in datalist:
            # bytedata = (data + "tttttttt").encode(encoding="utf-8")
            bytedata = kv.get(str(data))
            if bytedata:
                # print(bytedata)
                zfile.writestr(str(data),bytedata)
        zfile.close() 
        key = config.keyDataBackUp
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key, AES.MODE_ECB)
        CryptIV = cipher.encrypt(iv)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        bytebuffer = FileBuffer.getvalue()
        lendata = 16 - len(bytebuffer)%16
        bytebuffer = bytebuffer + chr(lendata)*lendata
        #print(bytebuffer)
        CryptData = CryptIV + cipher.encrypt(bytebuffer)
        bucket = Bucket('backup')
        # print(FileBuffer.getvalue())
        bucket.put_object(filename,CryptData)
        FileBuffer.close()
def ReadZipFile(filename):

    """
    从storage中读取数据，还原到kvdb中
    参数 filename 要还原数据的文件名
    """
    bucket = Bucket('backup')
    # print(filename)
    CryptData = bucket.get_object_contents(filename)
    # print(CryptData)
    # -FileBuffer.close()
    key = config.keyDataBackUp
    cipher = AES.new(key, AES.MODE_ECB)
    iv = cipher.decrypt(CryptData[:16])
    # print(str(iv))
    cipher = AES.new(key, AES.MODE_CBC, iv)
    bytebuffer = cipher.decrypt(CryptData[16:])
    lendata = ord(bytebuffer[-1])
    FileBuffer = io.BytesIO(bytebuffer[:-lendata])
    zfile = zipfile.ZipFile(FileBuffer,mode='r')
    namelist = zfile.namelist()
    for name in namelist:
        bytedata = zfile.read(name)
        kv.set(name,bytedata.decode("utf-8"))
        
    return u"数据已还原"
        
def MakeBackup():

    """
    定时备份文件任务
    """
    dbchgcounter = kv.get("kvdbchg")
    if dbchgcounter == None:
        dbchgcounter = 0
    if dbchgcounter == 0:
        return u"数据未改变"
    dbchgcounter = 0
    kv.set("kvdbchg",dbchgcounter)
    
    
    bucket = Bucket('backup')
    tm = datetime.now()
    # 删除过期文件
    dellist = []
    fdlist = []
    fwlist = []
    for finf in bucket.list():
        last_modified = str(finf[u'last_modified'])
        last_modified = last_modified[:last_modified.index(".")]#2013-05-22T05:09:32.259140 -> 2013-05-22T05:09:32
        filetime = datetime.strptime(last_modified,"%Y-%m-%dT%H:%M:%S")
        fname = str(finf[u"name"])
        if "d.zip.data" in fname:
            fdlist.append((fname,tm-filetime))
        else:
            fwlist.append((fname,tm-filetime))
            
    if len(fdlist) > 3:
        sorted(fdlist,key = lambda x:x[1])
        dellist = fdlist[3:]
    if len(fwlist) > 4:
        sorted(fwlist,key = lambda x:x[1])
        dellist += fdlist[4:]
    
    for fname in dellist:
        bucket.delete_object(fname[0])
    
    #备份新文件
    filename = tm.strftime(u"%Y-%m-%d_%H_%M_%S")
    if tm.weekday() == 5: #周六
        filename += "w.zip.data"
    else:
        filename += "d.zip.data"
    WriteZipFile(filename)
    
    return u"已备份"
    
    

if __name__ == "__main__":
    WriteZipFile("test.zip")
    # jslist = FindKVDBKeys()
    # for js in jslist:
        # print (js)