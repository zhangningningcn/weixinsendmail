# -*- encoding: utf-8 -*-
import urllib
import urllib2
#import lxml
from lxml import etree

def sendData(s):
    dxml = """
    <xml>
    <MsgType>text</MsgType>
    <FromUserName>znn</FromUserName>
    <ToUserName>ser</ToUserName>
    <Content>""" + s.decode("gbk").encode("utf-8") +"</Content></xml>"
    urldata = urllib2.urlopen('http://localhost:8080/weixin',dxml)
    dataxml = urldata.read()
    xml = etree.fromstring(dataxml)#½øÐÐXML½âÎö
    content=xml.find("Content").text
    return content
    
    
if __name__ == "__main__":
    while True:
        s = raw_input()
        if s == quit:
            break;
        print (sendData(s))
        