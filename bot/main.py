import paho.mqtt.client as mqtt
import sys
import time
import threading

""" MQTT Protocol

- SEND

subscribe/BOT_ID {empty payload} -- add your bot to the world


command/BOT_ID/move {empty payload} -- move your bot forward
command/BOT_ID/rear {empty payload} -- move your bot downward
command/BOT_ID/turn {"left" or "right"} -- turn your bot
command/BOT_ID/stop {empty payload} -- stops bot engine


- RECEIVE

sensors/BOT_ID/proximity "{front_left}|{front_right}|{rear}" --- proximity sensors readings in cm


"""


BOT_ID = "asdasd"
CAR = {}


def best_direction():
    proximity = CAR["proximity"]
    okdir = []
    for p in proximity:
        if p < 10:
            status = False
        else:
            status = True
        okdir.append(status)
    print(okdir)
    if proximity[0] > 10 and proximity[1] > 10:
        if okdir[0] and proximity[0] > proximity[1]:
            return ("turn","left")
        if okdir[1] and proximity[1] > proximity[0]:
            return ("turn","right")
        if okdir[0] and okdir[1]:
            return ("move",None)
    return ("rear",None)

def drive(client):
    while True:
        if not "proximity" in CAR:
            time.sleep(0.05)
            continue

        direction,payload = best_direction()
        client.publish('/'.join(('command', BOT_ID, direction)),payload)
        if direction == "rear":
            while CAR["proximity"][0] < 20 and CAR["proximity"][1] < 20:
                time.sleep(0.1)
        else:
            time.sleep(0.1)



# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    try:

        print("Connected with result code {rc}")

        client.publish('/'.join(('subscribe', BOT_ID)))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe("/".join(("sensors", BOT_ID, "#")))

        # t = threading.Thread(target=drive, args=(client,), daemon=True)
        # t.start()

    except Exception as e:
        print(e)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    try:
        if str(msg.topic).startswith("$SYS/broker"):
            return handle_system_message(msg)

        if str(msg.topic).startswith("sensors/"):
            return handle_sensor_data(msg)

        print("Unhandled message")
    except Exception as e:
        print("Unexpected error:", e)
    

def handle_system_message(message):
    # DO NOTHING
    return None

def handle_sensor_data(message):
    action = message.topic.split("/")[-1]
    payload = message.payload.decode('utf8')
    if action == "proximity":
        CAR["proximity"] = [float(p) for p in payload.split("|")]
        # print(action,CAR["proximity"])
    return None

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()