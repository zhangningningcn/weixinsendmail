
import web
import sendmail
web.config.debug = True  


class CronUpdate():
    
    def GET(self):
        sendmail.sendMail()
    def POST(self):
        sendmail.sendMail()