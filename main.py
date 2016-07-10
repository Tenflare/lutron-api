import telnetlib
import time
import requests
import time
from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

_NEWLINE = '\n'

LUTRON_HOST = '192.168.10.26'
LUTRON_PORT = 23
LUTRON_USERNAME = 'lutron'
LUTRON_PASSWORD = 'integration'


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
        func_hl = Thread(target=func, args=args, kwargs=kwargs)
        func_hl.start()
        return func_hl

    return async_func


def login():
    connection = False
    session = telnetlib.Telnet(LUTRON_HOST, LUTRON_PORT)
    while connection is False:
        session.read_until("login:")
        session.write('lutron\r\n')
        session.read_until("password")
        session.write('integration\r\n')
        prompt = session.read_until('GNET')
        connection = True
    return session


@run_async
def open(session):
    """
    Helper function to "cascade" the opening/closing of shades
    :param session: telnetlib.Telnet authenticated session
    :return:
    """
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
    """
    Helper function to "cascade" the opening/closing of shades
    :param session: telnetlib.Telnet authenticated session
    :return:
    """
    session.write('#OUTPUT,5,1,0\r\n')
    time.sleep(2)
    session.write('#OUTPUT,4,1,0\r\n')
    time.sleep(2)
    session.write('#OUTPUT,3,1,0\r\n')
    time.sleep(2)
    session.write('#OUTPUT,2,1,0\r\n')
    time.sleep(2)


def get_status(session, device_id='3'):
    """
    Return the status of a device
    :param session: telnetlib.Telnet authenticated session
    :return:
    """
    session.write('?OUTPUT,{},1'.format(device_id))
    prompt = session.read_until('~OUTPUT,{},1,'.format(device_id))
    return int(float(prompt.split(',1,')[1].split('\r')[0]))


@run_async
def set_level(session, level):
    session.write('#OUTPUT,2,1,{}\r\n'.format(level))
    time.sleep(2)
    session.write('#OUTPUT,3,1,{}\r\n'.format(level))
    time.sleep(2)
    session.write('#OUTPUT,4,1,{}\r\n'.format(level))
    time.sleep(2)
    session.write('#OUTPUT,5,1,{}\r\n'.format(level))
    time.sleep(2)


class Status(Resource):
    def get(self):
        session = login()
        resp = get_status(session)

        return {'status': resp}


class ShadesOpen(Resource):
    def post(self):
        session = login()
        open(session)

        return {'status': 'open'}


class ShadesClose(Resource):
    def post(self):
        session = login()
        close(session)

        return {'status': 'closed'}


class Shades(Resource):
    def post(self, level):
        session = login()
        if int(level) == 50:
            set_level(session, level)
            return {'status': 'closed'}
        elif int(level) <= 99:

            close(session)
            return {'status': 'open'}

        else:
            open(session)

        return {'status': level}


api.add_resource(Shades, '/shades/<string:level>')
api.add_resource(ShadesOpen, '/shades/open')
api.add_resource(ShadesClose, '/shades/close')
api.add_resource(Status, '/shades/status')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
