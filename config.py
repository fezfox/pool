#!/usr/bin/python3
#-----------------------------------------------------------
#
#
# Author : Matt Hawkins
# Modified by: fezfox
#
#
#-----------------------------------------------------------


BASEPATH = '/home/pi/pool'

# Set the number of seconds between each loop.
# This determines how often the system checks the status of the pump.
LOOPDELAY = 60
# Set the number of loops that pass before data is sent to Thingspeak
LOOPSENDDATA = 5

# Default username and password hash "splishsplosh"
# Use hashgenerator.py in utils to create hash for your password
USERNAME = 'admin'
USERHASH = 'c7f9e589934a99848f2dba75a70b49dca6149988730389671d730e9376701adf'

# Flask needs a secret key or phrase to handle login cookie
FLASKSECRET = '7e8031df78fd55cba971df8d9f5740be'

# Thinkspeak details for public channel
# to publish temperature data
# Enter your key below :
THINGSPEAKKEY = ''
THINGSPEAKURL = 'https://api.thingspeak.com/update'


# MQTT settings
# enter the MQTT password
MQTTPWORD = ''
