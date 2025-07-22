# python 3.11

import random,datetime
import paho.mqtt.client as mqtt


broker = 'vps1.tomkat.in'
port = 1883
base_topic = "esphome/em1/sensor/"
# topic = "$SYS/#"
# Generate a Client ID with the publish prefix.
client_id = f'publish-{random.randint(0, 1000)}'
username = 'test'
password = 'test001'



# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(topic)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

# def get_message():
#     mqttc.

## MAIN
# mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
# mqttc.on_connect = on_connect
# mqttc.on_message = on_message
# mqttc.connect(broker ,1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
import paho.mqtt.subscribe as subscribe

def get_message(key):
    msg = subscribe.simple(base_topic+key+'/state', hostname=broker)
    result = str(msg.payload.decode())
    return result

def get_messages():
    data = {}

    key = 'time'
    now = datetime.datetime
    value = now.now()
    data[key] = value

    key = 'voltage'
    value = get_message(key)
    data[key] = value

    key = 'current'
    value = get_message(key)
    data[key] = value

    key = 'power'
    value = get_message(key)
    data[key] = value

    return data
    # print("%s %s" % (msg.topic, msg.payload))

# get_messages()
# mqttc.loop_forever()