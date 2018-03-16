#!/usr/bin/python3
#-----------------------------------------------------------
#
#
# Author : Matt Hawkins
# Modified by: fezfox
#
#
#-----------------------------------------------------------

import os
import errno
import datetime
import requests
import config as c
import socket


def getIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def silentRemove(filename):
    try:
        os.remove(filename)
    except OSError as e:  # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise  # re-raise exception if a different error occurred


def sendThingspeak(url, key, field1, temp1):
    if url == '' or key == '':
        return

  # Send event to internet site
    payload = {'api_key': key, 'field1': temp1}
    try:
        r = requests.post(url, data=payload, timeout=5)
        if r.status_code == 200:
            print("Sent data to Thingspeak")
        else:
            print("Error sending data to Thingspeak (status code:"+str(r.status_code)+")")
    except:
        print("Error sending data to Thingspeak")


def saveTempToFile(temp):
    try:
        f = open(c.BASEPATH + "/logs/temp.log", 'a')
        timeStamp = '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
        f.write(timeStamp + ' ' + temp + '\n')
        f.close()
    except:
        print("Problem saving temperature")


def loadTempFromFile():
    try:
        f = open(c.BASEPATH + "/logs/temp.log", 'r')
        line = f.readlines()[-1]  # read last line
        f.close()
        line = line.replace('\n', '')
        a = line.rsplit(' ', 1)
        temp = a[1]

    except:
        print("Problem loading temperature")
        temp = '0'

    return temp


def readTemps(sensorID):
    t1 = '{:.1f}'.format(getTemp(sensorID[0])/float(1000))

    return t1


def getTemp(id):
    try:
        mytemp = ''
        filename = 'w1_slave'

        f = open('/sys/bus/w1/devices/' + id + '/' + filename, 'r')
        line = f.readline()  # read 1st line
        line = line.replace('\n', '')
        crc = line.rsplit(' ', 1)

        if crc[1] == 'YES':
            line = f.readline()  # read 2nd line
            f.close()
            line = line.replace('\n', '')
            mytemp = line.rsplit('t=', 1)
            temp = mytemp[1]
            saveTempToFile(temp)
        else:
            temp = loadTempFromFile()

        return int(temp)

    except:
        return 99999


def getSensorIDs():
    sensorIDs = []

    try:
        for item in os.walk('/sys/bus/w1/devices/'):
            dirs = item[1]
            for dir in dirs:
                if dir[:3] == '28-':
                    sensorIDs.append(dir)
    except:
        sensorIDs = ['NOTFOUND']
    if len(sensorIDs) == 0:
        sensorIDs = ['NOTFOUND']
    return sensorIDs


# Tail a file and get X lines from the end
def tail(f, lines=20, _buffer=4098):

    # place holder for the lines found
    lines_found = []

    # block counter will be multiplied by buffer
    # to get the block size from the end
    block_counter = -1

    # loop until we find X lines
    while len(lines_found) < lines:
        try:
            f.seek(block_counter * _buffer, os.SEEK_END)
        except IOError:  # either file is too small, or too many lines requested
            f.seek(0)
            lines_found = f.readlines()
            break

        lines_found = f.readlines()

        # decrement the block counter to get the
        # next X bytes
        block_counter -= 1

    return lines_found[-lines:]