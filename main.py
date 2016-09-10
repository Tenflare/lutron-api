import os
import telnetlib
import time
import requests
import time
from flask import Flask
from flask_restful import Resource, Api
import argparse

import sys



app = Flask(__name__)
api = Api(app)


_NEWLINE = '\n'

# This is ugly but for now we will poll all the devices we know about
# TODO dynamically populate this list

# 2,3,4,5 are the individual shades  - 6 represents a group configured in Lutron App
ACTIVE_SHADES = [2,3,4,5]

def get_lutron_host():
    """
    Helper to obtain LUTRON host

    :return: str lutron bridge IP address
    """
    # First we will attempt to get it from the current environment

    if not LUTRON_HOST:
        # If we don't have it yet - we will check command line arguments
        pass

    return None

LUTRON_HOST = os.getenv('LUTRON_HOST')

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
        print 'Attempting to connect to Lutron Hub'
        session.read_until("login:")
        session.write('lutron\r\n')
        session.read_until("password")
        session.write('integration\r\n')
        prompt = session.read_until('GNET')
        connection = True
    print "Successfully Logged in to Lutron Hub"
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

def send_lutron_command(session, command, integration, action, parameters):
    session.write('#{},{},{},{}\r\n'.format(command, integration, action, parameters or 0))
    return "OK"


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
    if isinstance(device_id, int):
        device_id = str(device_id)
    print "Getting Status for device_id={}".format(device_id)
    session.write('?OUTPUT,{},1\r\n'.format(device_id))
    prompt = session.expect(["OUTPUT,\d+,1,\d+.\d+"], 3)
    if prompt[1] is not None:
        prompt = prompt[1].string
        try:
            val =  int(float(prompt.split(',1,')[1].split('\r')[0]))
        except:
            val = 0
        return val
    else:
        return 0



@run_async
def set_level(session, id, level):
    session.write('#OUTPUT,{},1,{}\r\n'.format(id, level))
    time.sleep(2)


class Status(Resource):
    def get(self):
        session = login()

        resp = {'devices': {}}
        for id in ACTIVE_SHADES:
            value = get_status(session, device_id=id)
            entry = {"value": int(value)}
            resp['devices'][str(id)] = entry
        return resp

class DeviceStatus(Resource):
    def get(self, integration):
        session = login()
        resp = get_status(session, device_id=integration)
        print resp
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


class ShadesLevel(Resource):
    """
    This is a macro endpoint that sets a group of shades at the same level
    """
    def post(self, level):
        session = login()

        set_level(session, '2', level)
        set_level(session, '3', level)
        set_level(session, '4', level)
        set_level(session, '5', level)

        return {'status': level}

class ShadesStatus(Resource):
   def get(self):
        session = login()

        resp = {'devices': {}}
        for id in ACTIVE_SHADES:
            value = get_status(session, device_id=id)
            entry = {"value": int(value)}
            resp['devices'][str(id)] = entry
        return resp


class Command(Resource):
    """
    Generic API resource for interacting with Lutron devices.  The primary interface is via the  command for
    controlling on/off status of Lutron devices.

    Example Usages

    Start Lowering a Device Group

    #DEVICE,6,6,3
    /api/device/6/6/3

    Stop Lowering a Device Group
    #DEVICE,6,6,4
    /api/device/6/6/4

    Start Raising a Device Group

    #DEVICE,6,5,3
    /api/device/6/5/3

    Stop Lowering a Device Group

    #DEVICE,6,5,4
    /api/device/6/5/4

    #OUTPUT,3,1,100
    /api/output/3/1/100

    """

    def get(self, command, integration, action, parameters):
        return {
            'commnad': command,
            'integration': integration,
            'action': action,
            'parameters': parameters
        }

    def post(self, command, integration, action, parameters):
        session = login()
        send_lutron_command(session, command, integration, action, parameters)
        # Need better validation here, for now we assume the command worked
        return {
            'integration': integration,
            'action': action,
            'parameters': parameters
        }

# Macro endpoints
api.add_resource(ShadesStatus, '/shades')
api.add_resource(ShadesLevel, '/shades/<string:level>')
api.add_resource(ShadesOpen, '/shades/open')
api.add_resource(ShadesClose, '/shades/close')

# Expose Lutron commands directly as API
api.add_resource(Command, '/api/<string:command>/<string:integration>/<string:action>/<string:parameters>')
api.add_resource(Status, '/api/<string:command>/<string:integration>')
#api.add_resource(Status, '/api/output')

if __name__ == '__main__':

    app.run(host='0.0.0.0', debug=True)
