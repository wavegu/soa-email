SERVER_IP = '127.0.0.1'
SERVER_PORT = 7254

import leveldb
from constants import DB_PATH_ID_PERSON_JSON
from flask import g
from flask import Flask
server = Flask(__name__)


@server.before_request
def before_request():
    if 'DB_ID_PERSON_JSON' not in g:
        print 'init g'
        g.DB_ID_PERSON_JSON = leveldb.LevelDB(DB_PATH_ID_PERSON_JSON)
        print g.DB_ID_PERSON_JSON.Get('Jie Tang')