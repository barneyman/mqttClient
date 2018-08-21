import paho.mqtt.client as mqtt 
import time
import http.client
import json
import subprocess
from bjfHA import bjfHA


def HandleCommand(object, command):
	data = json.load(open('config.json'))
	myHA=bjfHA('/home/pi/HA/config.json')
	print(object, command)
	if "commands" in data:
		commands=data["commands"]
		if object in commands and command in commands[object]:
			# work out if it's a mood or a command
			if 'mood' in commands[object][command]:
				myHA.setMood(commands[object][command]['mood'])
			else:
				# iterate thru commands
				for each in commands[object][command]['commands']:
					myHA.sendCommand(each['device'],each['command'])

			#for each in commands[object][command]:
			#	commandType=each['type']
			#	if commandType=="http":
			#		print (each['host'],each['url'])
			#		conn=http.client.HTTPConnection(each['host'])
			#		conn.request(url=each['url'], method="GET")
			#	if commandType=="lirc":
			#		print (each['irc_send'])
			#		subprocess.call(["irsend", "SEND_ONCE", each['irc_send']['remote'], each['irc_send']['command']])

	


def on_message(mosq, obj, msg):
	print ("on_message:: this means  I got a message from broker for this topic")
	print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

	topic=msg.topic.split("/")

	if len(topic)==3:
		HandleCommand(topic[2], msg.payload.decode('utf8'))

	return



def on_connect(client, userdata, flags, rc):
	print ("on_connect:: Connected with result code "+ str ( rc ) )
	for feed in userdata:
		print ("subscribing to ",feed)
		client.subscribe (feed,1 )

def on_disconnect(client, obj, rc):
	print ("on_disconnect:: DisConnected with result code "+ str ( rc ) )
	print(client.reconnect());



def on_publish(mosq, obj, mid):
    print("mid: " + str(mid))
    print ("")

def on_subscribe(mosq, obj, mid, granted_qos):
    print("This means broker has acknowledged my subscribe request")
    print("Subscribed: " + str(mid) + " QoS " + str(granted_qos))

def on_log(mosq, obj, level, string):
    print(  string)


def ConnectLoop():
	data = json.load(open('config.json'))
	config=data["config"]

	mqttfeeds=config["feeds"]
	print (mqttfeeds)

	client_name=config["clientName"]
	hostname=config["host"]
	user=config["user"]
	pwd=config["pwd"]
	hostport=config["port"]

	print(client_name,hostname,user,pwd,hostport)

	client = mqtt.Client(client_name, userdata=mqttfeeds)

	print(client)

	client.username_pw_set(user, pwd)

	client.on_message = on_message
	client.on_connect = on_connect
	client.on_publish = on_publish
	client.on_subscribe = on_subscribe
	client.on_disconnect = on_disconnect

	# Uncomment to enable debug messages
	# client.on_log = on_log

	# B64 encoded
	client.tls_set("adafruit_ca.crt")
	client.connect(hostname, port=hostport)

	client.loop_forever()

	print("out of loop")


if True:
	try:
		ConnectLoop()
	except Exception as e:
		print ("exception, hup ",e)


