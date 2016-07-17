# -*- coding: utf-8 -*-

#from __future__ import print_function
import sys
import time
from datetime import date,datetime,timedelta
from datetime import time as dttime
# import sae.kvdb
from sae.mail import send_mail
import datas
try:
    import config
except ImportError:
    import configDemo as config

ChenseToNumber ={u"一":u"1",u"二":u"2",u"两":u"2",u"三":u"3",u"四":u"4",u"五":u"5",u"六":u"6",u"七":u"7",u"八":u"8",u"九":u"9",u"零":u"0"}
ChenseData ={u"年":0,u"月":1,u"日":2,u"号":2,u"时":3,u"点":3,u":":3,u"：":3,u"分":4}
TimeSegment ={u"早上":[0,8],u"上午":[0,8],u"中午":[3,12],u"下午":[2,14],u"晚上":[2,19],u"今晚":[2,19],u"凌晨":[0,0],u"傍晚":[2,17],u"明天":[0,24],u"明晚":[2,24],u"后天":[0,48]}

def strToDateTime( instr ):

    TimeIn = [0]*5 # 年月日时分
    today = datetime.now()
    TimeType = 0
    instrlen = len(instr)
    strindex = 0
    issettime = False
    #print(today)
    
    NextTimeperiod = 0
    lastdataindex = 2

    if instr[0:2] in TimeSegment.keys():
        strindex = 2
        k,t = TimeSegment[instr[0:2]]
        #today +=  timedelta(hours = t)
        if t > 23:
            today +=  timedelta(hours = t)
        else:
            today = datetime.combine(today.date(),dttime(t,0))
        TimeType = k
    else:
        if instr[0] == u"下":
            NextTimeperiod = 1
            strindex += 1
            if instr[strindex] == u"下":
                NextTimeperiod = 2
                strindex += 1
        if instr[strindex] == u"周" or instr[strindex:strindex+1] == u"星期":
            if instr[strindex] == u"周":
                strindex += 1
            else:
                strindex += 2
            number = u""
            if instrlen > strindex:
                word = instr[strindex]
                if word in ChenseToNumber.keys():
                    number += ChenseToNumber[word]
                elif word in u"123456":
                    number += word
                elif word == u"日":
                    number = u"7"

                strindex += 1
            else:
                return (-1,"12")
            try:
                inum = int(number) -1
            except ValueError:
                return (-1,"10")
            #issettime = True
            day = today.weekday()
            if day <= inum:
                today = today + timedelta(days = inum-day)
            else:
                today = today + timedelta(days = inum-day+7)
                NextTimeperiod -= 1
            if NextTimeperiod > 0:
                today = today + timedelta(days = NextTimeperiod*7)
            # else:
                # return (-1,u"")
        if u"后" in instr:
            afday = 0
            afhour = 0
            afminute = 0
            afweek = 0
            number = u''
            while strindex < instrlen:
                word = instr[strindex]
                if word in ChenseToNumber.keys():
                    number += ChenseToNumber[word]
                elif word in u"0123456789":
                    number += word
                elif word == u"天":
                    try:
                        afday = int(number)
                    except ValueError:
                        return (-1,"10")
                    number = u""
                    # issettime = True
                elif word == u"小":
                    strindex += 1
                    word = instr[strindex]
                    if word == u"时":
                        try:
                            afhour = int(number)
                        except ValueError:
                            return (-1,"10")
                        number = u""
                        lastdataindex = 3
                        issettime = True
                    else:
                        return (-1,u"1")
                elif word == u"分":
                    if instr[strindex+1] == u"钟":
                        strindex += 1
                    try:
                        afminute = int(number)
                    except ValueError:
                        return (-1,"10")
                    lastdataindex = 4
                    number = u''
                    issettime = True
                elif word == u"半":
                    strindex += 1
                    if instrlen - strindex < 3:
                        return (-1,u"2")
                    if instr[strindex] == u"个":
                        strindex += 1
                    if instr[strindex:strindex+2] == u"小时":
                        afminute = 30
                        strindex += 1
                        lastdataindex = 4
                        number = u''
                    else:
                        return (-1,u"3")
                elif word == u"个":
                    pass
                elif word == u"后":
                    strindex += 1
                    number = u''
                    today = today + timedelta(days = afday,hours = afhour,minutes = afminute,weeks = afweek)
                    break;
                elif word == u"周":
                    try:
                        afweek = int(number)
                    except ValueError:
                        return (-1,"10")
                    # issettime = True
                strindex += 1
    #else:
    TimeIn[0] = today.year
    TimeIn[1] = today.month
    TimeIn[2] = today.day
    TimeIn[3] = today.hour
    TimeIn[4] = today.minute

    #print(strindex)
    number = u''
    while strindex < instrlen:
        word = instr[strindex]
        if word in ChenseToNumber.keys():
            tnum = ChenseToNumber[word]
            if len(number) == 0:
                number = tnum
            elif len(number) == 2:
                number = number[0] + tnum
            else:
                return (-1,u"4")
            #number += ChenseToNumber[word]
        elif word == u"十":
            if number == u'':
                number = u'10'
            else:
                number += u"0"
        elif word == u"刻":
            try:
                number = str(int(number)*15)
            except ValueError:
                return (-1,"10")
            if int(number) > 59:
                return (-1,u"5")
            try:
                TimeIn[4] = int(number)
            except ValueError:
                return (-1,"10")
            number = u''
            issettime = True
            break
        elif word in ChenseData.keys():
            lastdataindex = ChenseData[word]
            #print(word)
            try:
                TimeIn[lastdataindex] = int(number)
            except ValueError:
                return (-1,"10")
            if lastdataindex == 3:
                TimeIn[4] = 0
                issettime = True
            number = u''
            if lastdataindex == 4:
                issettime = True
                break
        elif word in u"0123456789-":
            number += word
        elif word == u' ':
            if lastdataindex == 2:
                derror = False
                try:
                    if u'-' in number:
                        if number.count(u'-') == 1:
                            index = number.find(u'-')
                            TimeIn[1] = int(number[:index])
                            TimeIn[2] = int(number[index+1:])
                        elif number.count(u'-') == 2:
                            index = number.find(u'-')
                            TimeIn[0] = int(number[:index])
                            number = number[index+1:]
                            index = number.find(u'-')
                            TimeIn[1] = int(number[:index])
                            TimeIn[2] = int(number[index+1:])
                        else:
                            derror = True
                        number = u""
                    else:
                        if len(number) == 2:
                            TimeIn[2] = int(number)
                        elif len(number) == 4:
                            TimeIn[1] = int(number[:2])
                            TimeIn[2] = int(number[2:])
                        elif len(number) == 6:
                            TimeIn[0] = int(number[:2])+2000
                            TimeIn[1] = int(number[2:4])
                            TimeIn[2] = int(number[4:])
                        elif len(number) == 8:
                            TimeIn[0] = int(number[:4])
                            TimeIn[1] = int(number[4:6])
                            TimeIn[2] = int(number[6:])
                        else:
                            derror = True
                        number = u""
                except ValueError:
                    return (-1,u"6")
                if derror:
                    #return (-1,u"7")
                    if lastdataindex > 2:
                        break
                else:
                    lastdataindex = 3
            else:
                break
        elif instr[strindex:strindex+2] in TimeSegment.keys():
            k,t = TimeSegment[instr[strindex:strindex+2]]
            # today +=  timedelta(hours = t)
            TimeType = k
            strindex += 1
        elif word == u'半':
            if lastdataindex == 3:
                TimeIn[4] = 30
                issettime = True
            else:
                return (-1,u"8")
        elif word == u"&":
            break;
        else:
            break;
        strindex += 1
    else:
        result = (-1,u"11")
        # strindex -= 1
    # if strindex == instrle:
        
    strindex += 1
        
    if number != u'':
        try:
            TimeIn[lastdataindex+1] = int(number)
        except ValueError:
            return (-1,"10")
        issettime = True
    #晚上
    if TimeType == 2:
        if TimeIn[3] < 13:
            TimeIn[3] += 12
            if TimeIn[3] == 24:
                TimeIn[2] += 1
                TimeIn[3] = 0
    #中午
    elif TimeType == 3:
        if TimeIn[3] < 3:
            TimeIn[3] += 12

    if issettime == False:
        return (-1,u"13")
    #print (TimeIn)
    try:
        result = (strindex,datetime(TimeIn[0],TimeIn[1],TimeIn[2],TimeIn[3],TimeIn[4]))
    except:
        result = (-1,u"10")
    return result

def saveMailData(s,user,state):
    """
    格式：mail 时间 事件
    设定时间发邮件提醒您，邮件内容是设定的事件。
    时间格式：下周3晚上9点、下午5点、明天八点、0715 8:00、7-9 10:00 等等
    注意：周一是每周第一天，自然语言解析还不完善，设置时间后请确定时间是否正确
    系统每10分钟执行一次，只有整10分钟会发邮件，比如8:00,8:10等等
    不写命令，默认按mail解析。此命令也可以省去mail直接写:“时间 事件”(不包括引号)
    
    格式：mail -d n1 n2 ...
    删除序号对应的mail事件。
    不带序号时列出mail列表。列出列表后发送序号可删除对应mail事件
    
    格式：mail
    列出所有发送邮件事件。此时发序号不可以删除对应mail事件
    """
    s = s.strip()
    if state != 3:
        if s == u'exit':
            datas.delete("sesion.json",{"User":['=',user]})
        elif s == u'-l':
            return listMail(s,user)
        elif s == u'-d' or state != 0:
            return deleteMail(s,user,state)
        elif s[0:2] == u'-d':
            deleteMail(s[:2],user,state)
            state = 1
            return deleteMail(s[2:],user,state)
    userinfo = datas.select("userinfo.json",{"User":['=',user]})
    if not userinfo:
        return u"您的邮箱没设置"
    mail = "not set"
    if "mail" in userinfo[0]:
        mail = userinfo[0]["mail"]
    else:
        return u"您的邮箱没设置"
        
    m,t = strToDateTime(s)
    if m < 0:
        return u"Error "+t+u" 时间解析错误"
    if t < datetime.now():
        return u"设置时间早于当前时间，设置无效"
    s = s[m:]
    tm = (t - datetime(1970,1,1,8,0,0)).total_seconds() #8时区
    data_id = datas.select("sendmail_id.json",{"User":['=',user]})
    if data_id:
        data_id = data_id[0]["ID"]
    else:
        data_id = 0
    data_id = data_id+1
    # print(mail)
    data = {"User":user,"Time":tm,"Matter":s,"ID":data_id,"mail":mail}
    datas.insert("sendmail.json",data)
    datas.insert("sendmail_id.json",{"User":user,"ID":data_id},"User")
    if t.hour < 6:
        s += u"\n现在是凌晨，请确认您的时间设置没错"
    return t.strftime(u"%Y-%m-%d %H:%M")+u"发邮件到" +mail+u"提醒您："+s
    
def sendMail():
    now = time.time()
    datalist = datas.select("sendmail.json",{"Time":['<=',now]})
    for data in datalist:
        mail = data["mail"]
        send_mail(mail, u"事件提醒", data["Matter"],\
          ("smtp.sina.com", 25, "nnzyserver@sina.com", config.passwdmail, False))
        datas.delete("sendmail.json",{"ID":['=',data["ID"]]})
def deleteMail(s,user,state):
    rets = ""
    if state == 0:
        datalist = datas.select("sendmail.json",{"User":['=',user]})
        if not datalist:
            rets = u"事件列表里没有邮件提醒事件"
        else:
            rets = u"请选择：\n"
            #i = 1
            selectid = {}
            #for data in datalist:
            for i,data in enumerate(datalist,1):
                rets += str(i) +". " + data["mail"] + ":"
                rets += datetime.fromtimestamp(data["Time"]).strftime(u"%Y-%m-%d %H:%M#")\
                     +data["Matter"] + "\n"
                selectid[str(i)] = data["ID"]
                #i += 1
            datas.insert("sesion.json",{"User":user,"State":1,"App":"mail",\
                "Time":time.time()+300,"Data":selectid},"User")
    elif state == 1:
        ss = datas.select("sesion.json",{"User":['=',user]})
        data = ss[0]["Data"]
        slist = s.split()
        for sli in slist:
            if not sli in data.keys():
                rets = u"选择无效请重新选择： \n"
                #i = 1
                selectid = {}
                datalist = datas.select("sendmail.json",{"User":['=',user]})
                #for data in datalist:
                for i,data in enumerate(datalist,1):
                    rets += str(i) +". "
                    rets += datetime.fromtimestamp(data["Time"]).strftime(u"%Y-%m-%d %H:%M#")\
                         +data["Matter"] + "\n"
                    selectid[str(i)] = data["ID"]
                    #i += 1
                datas.insert("sesion.json",{"User":user,"State":1,"App":"mail",\
                    "Time":time.time()+300,"Data":selectid},"User")
                return rets
        #if s in data.keys():
        rets = u"已删除： \n"
        for sli in data.keys():
            dellist = datas.select("sendmail.json",{"ID":['=',data[sli]]})
            rets += datetime.fromtimestamp(dellist[0]["Time"]).strftime(u"%Y-%m-%d %H:%M#")\
                    +dellist[0]["Matter"] + "\n"
            datas.delete("sesion.json",{"User":['=',user]})
            datas.delete("sendmail.json",{"ID":['=',data[sli]]})
        #else:
    return rets
def listMail(s,user):
    datalist = datas.select("sendmail.json",{"User":['=',user]})
    if not datalist:
        rets = u"事件列表里没有邮件提醒事件"
    else:
        rets = u"事件列表：\n"
        #i = 1
        selectid = {}
        for i,data in enumerate(datalist,1):
            rets += str(i) +u". 邮箱:" + data["mail"] + ";"
            rets += u"时间:" + datetime.fromtimestamp(data["Time"]).strftime(u"%Y-%m-%d %H:%M;")\
                 +data["Matter"] + "\n"
            selectid[str(i)] = data["ID"]
            #i += 1
    datas.delete("sesion.json",{"User":['=',user]})
    return rets
    
    
    
if __name__ == "__main__":
    
    instr = [u"下周6 7点半 1111",u"上午8点 2222",u"晚上7点 3333",u"周1 晚上9点 打球",u"七点半 4444",u"十点一刻 睡觉",\
    u"半个小时后 5555",u"下周五 吃饭 6666",u"下下周六 77777",u"周三&8888",u"下午5点 9999",u"明天晚上八点 1111",u"后天早上7点 2222",u"下周3晚上9点",\
    u"三天后 3333",u"0715 8:00 4444",u"7-9 10:00 aaa",u"7-13 10:00 cccc",u"二十点",u"sss"]#，
    #   saveMailData(s,"znn")
    for s in instr:
       print s,
       print (strToDateTime(s))
    # print (strToDateTime("test"))
    # while True:
        # s = raw_input()
        # if s == "quit":
            # break;
        # now = time.time()
        # ss = datas.select("sesion.json",{"User":['=',"znn"]})
        # state = 0
        # if ss:
            # tm = ss[0]["Time"]
            # if tm > now:
                # state = ss[0]["State"]
            
        # print(saveMailData(s,"znn",state))
