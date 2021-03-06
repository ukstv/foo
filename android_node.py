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
UI_HOST = '192.168.43.183'
UI_PORT = 3000
UI_ENDPOINT = '/endpoint'

print("I am U: " + U)


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

    zero_angle = current_angle.q()
    zero_angle.set(random.random())
    e.loc(zero_angle, u'current_angle')


def real():
    connection = Connection()
    h = env.Handler(angle_main)
    connection.configure_with(delegate=None, func=h)
    connection.start()

if __name__ == "__main__":
    real()
