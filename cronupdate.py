"""
cron调用此文件，检查是否有需要发送的邮件
"""
import web
import sendmail
web.config.debug = True  


class CronUpdate():
    
    def GET(self):
        sendmail.sendMail()
    def POST(self):
        sendmail.sendMail()