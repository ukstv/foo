#!/usr/bin/env python

from shapiro import env
import time
import socket
import uuid
import threading
from connection import Connection
import httplib, urllib
import json
import random

U = unicode(str(uuid.uuid4()))
UI_HOST = 'localhost'
UI_PORT = 3000
UI_ENDPOINT = '/endpoint'

print("I am U: " + U)


def post(dict_data):
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    body = json.dumps(dict_data)
    conn = httplib.HTTPConnection(UI_HOST, UI_PORT)
    conn.request("POST", UI_ENDPOINT, body, headers)
    response = conn.getresponse()
    print response.status, response.reason
    data = response.read()
    print(data)
    conn.close()


def angle_main(e):
    angles = e.glob(env.LWWDict(), u'angles')
    initial_average = env.LWWValue()
    initial_average.set(0)
    average_angle = e.glob(initial_average, u'average_angle')
    current_angle = e.loc(env.LWWValue(), u'current_angle')

    def add_current_to_angles(current, all):
        next_all = all.clone()
        next_all.update(U, current)
        return next_all
    e.fold(current_angle, angles, add_current_to_angles, 'ADD_CURRENT_TO_ANGLES')

    def calculate_average_angle(all_angles, snk):
        count = len(all_angles.value)
        s = sum(all_angles.values().itervalues())
        avg_angle = snk.clone()
        avg_angle.set(float(s) / float(count))
        return avg_angle
    e.fold(angles, average_angle, calculate_average_angle, 'CALCULATE_AVERAGE_ANGLE')

    def send_all_angles(all_angles, all_angles_sink):
        payload = {
            'angles': all_angles.values(),
            'average_angle': e.globals.get(u'average_angle').value
        }
        post(payload)
        return all_angles
    e.fold(angles, angles, send_all_angles, 'SEND_ON_ALL_ANGLES')

    def send_all_angles(average_angle, all_angles_sink):
        payload = {
            'angles': e.globals.get(u'angles').values(),
            'average_angle': e.globals.get(u'average_angle').value
        }
        post(payload)
        return all_angles_sink
    e.fold(average_angle, angles, send_all_angles, 'SEND_ON_AVERAGE_ANGLE')


def real():
    connection = Connection()
    h = env.Handler(angle_main)
    connection.configure_with(delegate=None, func=h)
    connection.start()

if __name__ == "__main__":
    real()
