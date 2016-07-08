import telnetlib
import time
import requests
import time
from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

_NEWLINE = '\n'


def open(session):
    session.write('#OUTPUT,2,1,100\r\n')
    time.sleep(2)
    session.write('#OUTPUT,3,1,100\r\n')
    time.sleep(2)
    session.write('#OUTPUT,4,1,100\r\n')
    time.sleep(2)
    session.write('#OUTPUT,5,1,100\r\n')
    time.sleep(2)

def close(session):
    session.write('#OUTPUT,5,1,0\r\n')
    time.sleep(2)
    session.write('#OUTPUT,4,1,0\r\n')
    time.sleep(2)
    session.write('#OUTPUT,3,1,0\r\n')
    time.sleep(2)
    session.write('#OUTPUT,2,1,0\r\n')
    time.sleep(2)


class ShadesOpen(Resource):
    def post(self):
        connection = False
        session = telnetlib.Telnet('192.168.10.26', 23)
        while connection is False:
            session.read_until("login:")
            session.write('lutron\r\n')
            session.read_until("password")
            session.write('integration\r\n')
            prompt = session.read_until('GNET')
            print prompt
            print 'think we are logged in'
            connection = True

        open(session)

        return {'status': 'open'}



class ShadesClose(Resource):
    def post(self):
        connection = False
        session = telnetlib.Telnet('192.168.10.26', 23)
        while connection is False:
            session.read_until("login:")
            session.write('lutron\r\n')
            session.read_until("password")
            session.write('integration\r\n')
            prompt = session.read_until('GNET')
            print prompt
            print 'think we are logged in'
            connection = True

        close(session)

        return {'status': 'closed'}

api.add_resource(ShadesOpen, '/shades/open')
api.add_resource(ShadesClose, '/shades/close')


if __name__ == '__main__':
    app.run(debug=True)
