from flask import Flask
from apis import api
from cheroot.wsgi import Server as WSGIServer,PathInfoDispatcher
from flask_jwt_extended import JWTManager
import logging
import os

LOGGINGFORMAT = '%(asctime)-15s %(levelname)-8s %(name)-8s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=LOGGINGFORMAT, datefmt='%d-%b-%y %H:%M:%S')

mapp=Flask(__name__)
mapp.secret_key = os.getenv('tokenkey')


mapp.config['PROPAGATE_EXCEPTIONS'] = True

mapp.config['JWT_SECRET_KEY']=os.getenv('tokenkey')
mapp.config['JWT_DECODE_AUDIENCE']=os.getenv('usc')
#mapp.config['JWT_ENCODE_AUDIENCE']='testapp'
api.init_app(mapp)


jwt = JWTManager(mapp)




#host multiple instances
d=PathInfoDispatcher({'/':mapp})
# Get port from environment variable or default to 80
port = int(os.getenv('PORT', 80))
server=WSGIServer(('0.0.0.0', port),d)
#docker run -d -p 8088:8088 -t nginx
#start web server
try:
      server.start()
except KeyboardInterrupt:
      server.stop()