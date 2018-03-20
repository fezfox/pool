# Raspberry Pi Pool Temperature monitor

Borrowed heavily from and modified from
https://bitbucket.org/MattHawkinsUK/rpispy-pool-monitor/overview
https://www.raspberrypi-spy.co.uk/2017/07/pool-temperature-monitoring-and-pump-control-with-the-pi-zero-w/

I was recently very excited to finish building a pool in my home and not long after I decided I wanted a remote way of knowing the pool's temperature - much easier than dipping a toe in to decide if I wanted to swim! Research lead me to decide to use a Raspberry Pi as the core of this, and some adventures ensued. Here I'll summarise my experience, which may pave the path for others!

By the way, that picture isn't my pool - its the [Hotel Villa Honegg](https://villa-honegg.ch).

Things I'll be posting about:

#### A. Hardware
1. general thoughts about the raspberry pi
1. notes about interfacing the DS18B20 single wire temperature sensor, or "why I hate soldering"

#### B. Software
1. post the temperature to a local website using flask
2. posting the temperature to thinkspeak
3. connecting Home Assistant on your pi directly to the probe
4. passing data to home assistant on a second pi using MQTT publishing
5. homekit and its failures

#### C. Stuff you need
1. raspberry pi zero wh
2. power supply for pi
3. micro SD with raspbian (or noobs card)
4. DF robots DS18B20 Kit (or a DS18B20 waterproof temperature probe, a 4.7KOhm resistor, a soldering iron, and patience)
5. jumper wires
6. waterproof box if its going to be outside

My starting point was [Matt's great post](https://www.raspberrypi-spy.co.uk/2017/07/pool-temperature-monitoring-and-pump-control-with-the-pi-zero-w/) where he did something much more complicated, measuring air and water temperature, and controlling his pool pumps, all using the pi. All I wanted to do was measure the temperature, and ideally get remote access to the value, so I could be at work, and plan to dive in as soon as I got home!

### General thoughts about the raspberry pi
I'm more of a _software guy_ than a _hardware guy_. Not knowing what I'm about to tell you, I ended up using a soldering iron for the first time in decades, and learned I am still no good at it (and burned myself into the bargain). But here's the thing: _you don't have to use a soldering iron_.

I was after a pi with wifi, since the monitor lives outside dipped into the pool, so I purchased a [Raspberry Pi Zero W](https://core-electronics.com.au/raspberry-pi-zero-w-wireless.html).

![pi-zero](https://s3.amazonaws.com/fezfox-prd/2018/03/pi-zero.png)

However, I really suggest you get the [Raspberry Pi Zero WH](https://core-electronics.com.au/raspberry-pi-zero-wh.html) - this has *soldered headers* - little square pins that can connect to solderless jumper wires. These come in variable lengths and male and female connectors.

![pi-zero-wh](https://s3.amazonaws.com/fezfox-prd/2018/03/pi-zero-wh.jpg)

Its just so much easier to connect bits and pieces together in a plug-n-play way rather than roasting yourself with a soldering iron!

## The Temperature Probe
The DS18B20 single wire temperature probe is the standard probe to use for this sort of application as was recommended in Matt's post and others. All the articles I read described soldering this to the board and, to make matters worse, interposing a resistor. I managed to do this... but again, there's an easier way!

[DFRobot](https://www.dfrobot.com) who primarily build products for Arduino robots makes a [DS18B20 Kit](https://core-electronics.com.au/waterproof-ds18b20-kit.html). This kit includes:
1. the temperature probe itself
2. a resistor module that has the required resistor as well as connectors for jumper wires to go to the pi, and screw terminals for the probe wires

![kit0021-02-1](https://s3.amazonaws.com/fezfox-prd/2018/03/kit0021-02-1.jpg)

That's right! *No soldering!* So here's the completed monitor in its waterproof case. You can see the pi itself (green light means its on) wired up to the resistor module using jumper cables, then the probe wired into the screw terminals:

![probe-box](https://s3.amazonaws.com/fezfox-prd/2018/03/probe-box.jpg)

Power comes in and the probe goes out via waterproof [cable glands](https://en.wikipedia.org/wiki/Cable_gland).

Different probes have different colours for the wire, so you will need to refer to the [DFRobot kit page](https://core-electronics.com.au/waterproof-ds18b20-kit.html) for details. Mine were red (power), black (ground) and yellow (data). Essentially there are three wires that have to be connected to the pi:

1. 3.3V - GPIO Pin 1
2. GND - GPIO Pin 9
3. DATA - GPIO Pin 7

I recommend [this site](https://pinout.xyz/) for good diagrams of the pi GPIO pins.

If you *really* want to solder, the 4.7KOhm resistor goes between Pin 1 and Pin 7.

## Software setup
For the most part I followed Matt's article, but with some changes since my use-case was in some ways simpler - a single probe - but with added differences since I ended up publishing the temperature to a second pi running home assistant - more on that later.

####Setup ssh
The easiest way to use the pi is via SSH. Im assuming you've already got an SD card with Raspbian on it. Put that card into your computer however you do it and using a simple text editor create a blank file called `ssh` in the root. Then create another file called `wpa_supplicant.conf` with the following data:

```
country=us
update_config=1
ctrl_interface=/var/run/wpa_supplicant

network={
 scan_ssid=1
 ssid="YOUR_NETWORK_SSID"
 psk="YOUR_NETWORK_PASSWORD"
}
```

This means when you boot up your pi it will connect to your wifi, and you can ssh to it. You just need to know your pis IP address, and then you can call:
`ssh pi@YOUR_PI_IP_ADDRESS` and the default password is `raspberry`. Logging in will take you to the default non-root user "pi". This account's path is  `/home/pi/`.

#### Install packages
Once logged into the pi, update:
```
sudo apt-get update
sudo apt-get -y upgrade
```
That will take 10-20 minutes...then install these packages:
```
sudo apt-get -y install git
sudo apt-get install python3-gpiozero
sudo apt-get -y install python3-pip
sudo pip3 install flask
sudo pip3 install requests
sudo pip3 install paho-mqtt
sudo apt-get install mosquitto
sudo apt-get install mosquitto-clients
```

#### Clone the repo
My repo contains all the code for the methods I describe below to use the data from the temperature probe. Clone the git repo:
```
git clone https://github.com/fezfox/pool.git
```

navigate to it:
```
cd pool
```

make the launcher executable
```
chmod +x launcher.sh
```

#### Configure the one-wire sensor
The DS18b20 is a 'one-wire" sensor, and the pi needs to be configured to make that work:
```
sudo nano /boot/config.txt
```
Add the following line to the bottom
```
dtoverlay=w1-gpio,gpiopin=4
```

#### Setup cron
This will make the launcher code run everytime the pi reboots
```
sudo crontab -e
```
Add this line to the bottom
```
@reboot sh /home/pi/pool/launcher.sh > /home/pi/pool/logs/cronlog 2>&1
```

#### Reboot the pi
Rebooting the pi will start the web page and logger.
```
sudo reboot now
```

### Software
There are a range of things you can do once you've got a pi with a temperature probe attached. I'm going to describe 4 ways you could use the temperature data available from the probe. Note that I've borrowed heavily from Matt's code and  simplified it a little.

1. post to a local website using flask
1. post to a ThingSpeak channel - a free site that means you can then see your temperature online
1. read the GPIO pin directly with a Home Assistant install on the pi 
1. publish to a mosquitto channel, which can be picked up by home assistant running on another pi

### Post to a webpage on your local network using flask
After reboot, launcher will run `webmain.py` which will use flask to create a web page on your local website. This can be accessed by navigating to you pi's IP address followed by port 5000:
```
YOUR_PI_IP_ADDRESS:5000
```
You will need to login with the username "admin" and the password "splishsplosh". (Matt goes into how you can change this password in his post - myself I was not so concerned if someone wants to know my pool temperature!). You should see something like this:
![Screen-Shot-2018-03-11-at-11.47.22-pm](https://s3.amazonaws.com/fezfox-prd/2018/03/Screen-Shot-2018-03-11-at-11.47.22-pm.png)

If not check your logs. If you have any familiarity with writing webpages, you can edit the files found in "templates".

### Post to a ThingSpeak channel
ThingSpeak is a website that allows you to setup an account where you can post and graph data - it's an easy way to get access to your temperature data outside your local network. You need to first register at [ThingSpeak](https://www.thingspeak.com). After you've created your account you will see a tab called "API keys" - place the "Write API key" and insert it into the `config.py` file. You should then have something like this:

![Screen-Shot-2018-03-11-at-11.56.57-pm-1](https://s3.amazonaws.com/fezfox-prd/2018/03/Screen-Shot-2018-03-11-at-11.56.57-pm-1.png)

You can see my channel [here](https://thingspeak.com/channels/395163)

### Read the GPIO pin directly with Home Assistant
Initally I tried to use iOS HomeKit (more about that later) but in the end I found [Home Assistant](homeassistant.io) to be a more reliable solution (see the HA website for information on how to install on a pi). With Home Assistant on the pi with your temperature probe, you can read the GPIO pin directly and place the information on the Home Assistant dashboard.All you need to do is put the sensor in the `configuration.yaml` file like this:

```
sensor:
  - platform: onewire
    names:
      28-00xxxxxx: Pool
```

You need to find the identifier for your probe, which you can find by looking in the directory `/sys/bus/w1/devices/` directory of your pi, and there will be a directory with the name `28-00xxxxxx` (not literally - each probe has a unique number I've represented here with xxxxx).

Of interest, you can look inside this directory to read the temperature, which is how it is done with the python code described above. Reading this file will show you the temperature:
```
cat /sys/bus/w1/devices/28-00xxxxxx/w1-slave'
```

### Read the temperature and publish to a mosquitto channel
In my case, the pool probe is outside, and I have Home Assistant running on another pi altogether. So I wanted to get the temperature data from the one pi to the other. There are various ways this can be done, but I found using a mosquitto channel was the easiest way to do it.

The code in `poolmain.py`, as well as posting to ThingSpeak, also creates and publishes to a *MQTT broker*. This is the setup here

```
#setup MQTT broker details
broker_address = p.getIp()
client = mqtt.Client("P1")
client.username_pw_set("mqtt", c.MQTTPWORD)
client.connect(broker_address, 1883, 60)
client.loop_start()
```

In the loop you can see:
```
client.publish("pool/temperature", temp1)
```

You can test this by logging into the pi with another terminal window, and *subscribing* to this channel:
```
mosquitto_sub -v -t "pool/temperature"
```

Every 5 minutes you'll see this in your terminal window:
```
pool/temperature 27.1
```

Next, to read this from Home Assistant you need the following setup in your `configuration.yaml` file:

```
mqtt:
  broker: YOUR_POOL_PI_IP
  port: 1883
  client_id: pool-temperature
  username: mqtt
  password: YOUR_POOL_PI_PASSWORD
  
sensor:
  - platform: mqtt
    state_topic: "pool/temperature"
    name: "Pool Temperature"
    unit_of_measurement: "C"
```


### HomeKit/homebridge failures
Initially I wanted to use Apple IOS HomeKit for my interaction with my devices, for a few reasons
1. it already comes with a nice UI that is maintained and updated by Apple
2. by using an Apple TV on my local network I could (in theory!) access my data from anywhere outside my local network, without having to forward ports, get SSL certs or other stuff.

There's a node module called [homebridge](https://github.com/nfarina/homebridge) which I setup and got runnning, and built my own node modules for my temperature probe (and garage opener).

**HOWEVER** it was compeletely unreliable, both at home and out and about. For no reason whatsoever HomeKit (or homebridge - I don't know which) would suddenly not be able to connect to my devices... and then later it would. There's nothing more annoying than intermittent failures.

It was ultimately just not worth the trouble. Home Assistant is just as easy - or easier - to setup, and much more reliable - and **WAY** more powerful. So I would recommend against wasting your time with HomeKit/homebridge.



