import telnetlib
import time
import requests
import time
from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

_NEWLINE = '\n'

def run_async(func):
	"""
		run_async(func)
			function decorator, intended to make "func" run in a separate
			thread (asynchronously).
			Returns the created Thread object

			E.g.:
			@run_async
			def task1():
				do_something

			@run_async
			def task2():
				do_something_too

			t1 = task1()
			t2 = task2()
			...
			t1.join()
			t2.join()
	"""
	from threading import Thread
	from functools import wraps

	@wraps(func)
	def async_func(*args, **kwargs):
		func_hl = Thread(target = func, args = args, kwargs = kwargs)
		func_hl.start()
		return func_hl

	return async_func

@run_async
def open(session):
    session.write('#OUTPUT,2,1,100\r\n')
    time.sleep(2)
    session.write('#OUTPUT,3,1,100\r\n')
    time.sleep(2)
    session.write('#OUTPUT,4,1,100\r\n')
    time.sleep(2)
    session.write('#OUTPUT,5,1,100\r\n')
    time.sleep(2)

@run_async
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
            connection = True

        close(session)

        return {'status': 'closed'}

class Shades(Resource):
    def post(self, level):
        connection = False
        session = telnetlib.Telnet('192.168.10.26', 23)
        while connection is False:
            session.read_until("login:")
            session.write('lutron\r\n')
            session.read_until("password")
            session.write('integration\r\n')
            prompt = session.read_until('GNET')
            connection = True
        if int(level) < 99:
            close(session)
            return {'status': 'closed'}
        else:

            open(session)
            return {'status': 'open'}




api.add_resource(Shades, '/shades/<string:level>')

api.add_resource(ShadesOpen, '/shades/open')
api.add_resource(ShadesClose, '/shades/close')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
