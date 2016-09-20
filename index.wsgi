import sae
import os
import web

#def app(environ, start_response):
#    PATHINFO = environ["PATH_INFO"]
#    if re.search(r'^/geteviron'):
#        
#        response_body = ['%s: %s' % (key, value)  
#                        for key, value in sorted(environ.items())]  
#        response_body = '\n'.join(response_body)  
#    else:
#        response_body = 'hello'
#    status = '200 OK'
#    response_headers = [('Content-type', 'text/plain')]
#    start_response(status, response_headers)
#    
#    
#    return [response_body]



from weixinapp import WeixinInterface
from cronupdate import CronUpdate
from kvbackup import KVBackUp
from webcmd import WebCmd

urls = (
'/weixin','WeixinInterface',
'/cron/update','CronUpdate',
'/cron/kvbackup','KVBackUp'
'/webcmd','WebCmd'
)

app_root = os.path.dirname(__file__)
templates_root = os.path.join(app_root, 'templates')
render = web.template.render(templates_root)

app = web.application(urls, globals()).wsgifunc()        
application = sae.create_wsgi_app(app)

#application = sae.create_wsgi_app(app)