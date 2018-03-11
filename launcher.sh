#!/bin/sh
# launcher.sh
# navigate to home directory, then to this directory, then execute python script
cd /home/pi/pool
python3 /home/pi/pool/poolmain.py &
python3 /home/pi/pool/poolweb.py &