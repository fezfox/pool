#!/usr/bin/python3
#-----------------------------------------------------------
#
#
# Author : Matt Hawkins
# Modified by: fezfox
#
#
#-----------------------------------------------------------
import time
import logging
import config as c
import poollib as p
import paho.mqtt.client as mqtt

# clear log
p.silentRemove(c.BASEPATH + '/logs/main.log')

logFormat = '%(asctime)s %(levelname)s:%(message)s'
logging.basicConfig(format=logFormat, filename=c.BASEPATH + '/logs/main.log', level=logging.DEBUG)
logging.info('Main start')

# Get the IDs of the DS18B20 temp sensors
mySensorIDs = p.getSensorIDs()

# Set number of seconds to wait between loops & number of loops to wait before sending data
loopDelay = c.LOOPDELAY
loopSendData = c.LOOPSENDDATA
loopCounter = c.LOOPSENDDATA - 1  # send on first loop

#setup MQTT broker details
broker_address = p.getIp()
client = mqtt.Client("P1")
client.username_pw_set("mqtt", c.MQTTPWORD)
client.connect(broker_address, 1883, 60)
client.loop_start()

if __name__ == '__main__':

    while True:

        # Read temperatures and send to Thingspeak
        # every 5 loops
        loopCounter += 1
        if loopCounter == loopSendData:
            temp1 = p.readTemps(mySensorIDs)
            logging.info('Read temperature')
            p.sendThingspeak(c.THINGSPEAKURL, c.THINGSPEAKKEY, 'field1', temp1)
            loopCounter = 0
            logging.info('Publish temperature')
            client.publish("pool/temperature", temp1)

        # Wait before doing it all again
        time.sleep(loopDelay)
