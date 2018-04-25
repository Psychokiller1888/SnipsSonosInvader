#!/usr/bin/python
# -*- coding: utf-8 -*-

# Psycho - 2018

from datetime import datetime
import json
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import socket
import soco
from soco.snapshot import Snapshot
import subprocess
import time

_CORE_PLACEMENT = 'office'
_LANGUAGE = 'en-US'

#------------------------------------#
_RUNNING = True

_INTENT_INVADE	= 'hermes/intent/Psychokiller1888:sonosInvade'
_INTENT_LEAVE	= 'hermes/intent/Psychokiller1888:sonosRetreat'
_INTENT_TIME	= 'hermes/intent/Psychokiller1888:getLocalTime'

_myIp = '0.0.0.0'
_speakOnSonos = False

def onConnect(client, userdata, flags, rc):
	_mqttClient.subscribe(_INTENT_INVADE)
	_mqttClient.subscribe(_INTENT_LEAVE)
	_mqttClient.subscribe(_INTENT_TIME)
	publish.single('hermes/feedback/sound/toggleOn', payload=json.dumps({'siteId': 'default'}),
				   hostname='localhost', port=1883)


def onMessage(client, userdata, message):
	global _speakOnSonos
	payload = json.loads(message.payload)
	siteId = payload['siteId']
	sessionId = payload['sessionId']

	if message.topic == _INTENT_INVADE:
		_speakOnSonos = True
		endTalk(sessionId=sessionId, text='Ok, speaking to you through your Sonos when possible!', client=siteId)

	elif message.topic == _INTENT_LEAVE:
		_speakOnSonos = False
		endTalk(sessionId=sessionId, text='Ok, I won\'t use your Sonos anymore', client=siteId)

	elif message.topic == _INTENT_TIME:
		hours = datetime.now().strftime('%I')
		minutes = datetime.now().strftime('%M')
		part = datetime.now().strftime('%p')

		hours = hours.lstrip('0')
		minutes = minutes.lstrip('0')

		if minutes != '' and int(minutes) < 10:
			minutes = 'oh {}'.format(minutes)

		t = '{} {} {}'.format(hours, minutes, part)
		endTalk(sessionId=sessionId, text='It is {}'.format(t), client=siteId)


def endTalk(sessionId, text='', client='default'):
	global _speakOnSonos

	where = client
	if where == 'default':
		where = _CORE_PLACEMENT

	if not _speakOnSonos or (_speakOnSonos and not where in sonosPlayerList):
		if text != '':
			_mqttClient.publish('hermes/dialogueManager/endSession', json.dumps({
				'sessionId': sessionId,
				'text': text
			}))
		else:
			_mqttClient.publish('hermes/dialogueManager/endSession', json.dumps({
				'sessionId': sessionId
			}))
	else:
		_mqttClient.publish('hermes/dialogueManager/endSession', json.dumps({
			'sessionId': sessionId
		}))

		if text != '':
			speakOnSonos(text, client)


def stop():
	global _RUNNING
	_RUNNING = False


def speakOnSonos(text, client):
	subprocess.call(['/home/pi/sonosInvader/snipsTalk.sh', _LANGUAGE, text])
	speak(client)


def speak(room):
	global sonosPlayerList, _myIp

	for place, player in sonosPlayerList.iteritems():
		if (room.lower() == 'default' and place == _CORE_PLACEMENT.lower()) or room.lower() == place.lower():

			# Taking a snapshot of the current state allows use to easily pause the currently playing track on the device before speaking on it and restore the music later
			snapshot = Snapshot(player)
			snapshot.snapshot()

			if isPlaying(player):
				player.pause()
				time.sleep(0.5)

			player.volume = 50
			player.play_uri('x-file-cifs://{}/share/snipsTalk.wav'.format(_myIp), title='Snips')

			# Sonos can be sleeping. We have to loop until detecting a playing state or sometimes it might fail speaking, ending before it even started
			while player.get_current_transport_info()['current_transport_state'] != 'PLAYING':
				time.sleep(0.1)

			# Once we started playing the sound, loop until it's finished
			while player.get_current_transport_info()['current_transport_state'] == 'PLAYING':
				time.sleep(0.1)

			# Restore the state we were before speaking on the player
			snapshot.restore()


def isPlaying(player):
	return player.get_current_transport_info()['current_transport_state'] == 'PLAYING' or player.get_current_transport_info()['current_transport_state'] == 'TRANSITIONING'


def getIp():
	global _myIp
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(('8.8.8.8', 80))
	_myIp = s.getsockname()[0]
	s.close()
	print('- My ip: {}'.format(_myIp))


if __name__ == '__main__':
	print('Starting')

	getIp()

	sonosPlayerList = {}
	for zone in soco.discover():
		sonosPlayerList[zone.player_name.lower()] = zone

	_mqttClient = mqtt.Client()
	_mqttClient.on_connect = onConnect
	_mqttClient.on_message = onMessage
	_mqttClient.connect('localhost', 1883)
	_mqttClient.loop_start()

	try:
		while _RUNNING:
			time.sleep(0.1)
		raise KeyboardInterrupt
	except KeyboardInterrupt:
		pass
	finally:
		_mqttClient.loop_stop()
