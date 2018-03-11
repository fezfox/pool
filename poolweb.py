#!/usr/bin/python3
#-----------------------------------------------------------
#    ___  ___  _ ____
#   / _ \/ _ \(_) __/__  __ __
#  / , _/ ___/ /\ \/ _ \/ // /
# /_/|_/_/  /_/___/ .__/\_, /
#                /_/   /___/
#
#     Pool Monitor System
#          poolweb.py
#
# This is the web front-end script.
#
# It serves a status page and allows users to set the
# pump mode and edit the schedule.
#
# Author : Matt Hawkins
# Date   : 05/07/2017
#
# Addtional details here:
# http://www.raspberrypi-spy.co.uk/
#
#-----------------------------------------------------------
import time
import datetime
import logging
import hashlib
import config as c
import poollib as p
from flask import Flask, flash, redirect, request, render_template, url_for, session, escape

app = Flask(__name__)
app.secret_key = c.FLASKSECRET

# clear log
p.silentremove(c.BASEPATH + '/logs/web.log')

logFormat = '%(asctime)s %(levelname)s:%(message)s'
logging.basicConfig(format=logFormat, filename=c.BASEPATH + '/logs/web.log', level=logging.DEBUG)
logging.info('Web start')


@app.route('/')
def index():

    if 'username' in session:
        mySensorIDs = p.getSensorIDs()
        temp1 = p.readTemps(mySensorIDs)

        timeStamp = '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
        data = {'t1': temp1, 'ts': timeStamp, 'user': escape(session['username'])}
        return render_template('index.html', data=data)
    else:
        return redirect(url_for('login'))


@app.route('/debug/')
def debug():

    mySensorIDs = p.getSensorIDs()
    temp1 = p.readTemps(mySensorIDs)

    timeStamp = '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
    data = {'id1': mySensorIDs[0],
            't1': temp1,
            'ts': timeStamp
            }
    return render_template('debug.html', data=data)


@app.route('/logs')
def logs():
    f = open(c.BASEPATH + '/logs/temp.log', 'r')
    logs = p.tail(f, 100)

    data = {'logs': logs}

    return render_template('logs.html', data=data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get username and password from submitted form
        userName = escape(request.form['username'])
        passWord = escape(request.form['password'])
        # Convert password to hash and compare to stored hash
        passWordHash = hashlib.sha256(passWord.encode('utf-8')).hexdigest()
        if userName == c.USERNAME and passWordHash == c.USERHASH:
            session['username'] = 'admin'
            return redirect(url_for('index'))
        else:
            time.sleep(2)
            session.pop('username', None)
            flash('Sorry. Better luck next time.', 'danger')
    else:
        flash('Please enter your details.', 'info')
    return render_template('login.html')


@app.route('/logout')
def logout():
    # Remove username from the session
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
