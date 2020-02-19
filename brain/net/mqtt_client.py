import paho.mqtt.client as mqtt
import threading

class MqttClient:

    def __init__(self, world):

        self.world = world

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect("localhost", 1883, 60)

        t = threading.Thread(target=self.init_client, daemon=True)
        t.start()

        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded interface and a
        # manual interface.
        # client.loop_forever()
    
    def init_client(self):
        self.client.loop_forever()

    def publish(self, topic, payload):
        try:
            self.client.publish(topic, payload)
        except Exception as e:
            print('Unable to pubish message, on topic ' + topic)

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        try:
            print("Connected with result code "+str(rc))

            # Subscribing in on_connect() means that if we lose the connection and
            # reconnect then subscriptions will be renewed.
            self.client.subscribe("#")
        except Exception as e:
            print(e)

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        try:
            self.handle_message(msg)
            # print(msg.topic+" "+str(msg.payload))
        except Exception as e:
            print(e)

    def handle_message(self, msg):
        #
        # msg.topic
        # msg.payload
        #
        # print(str(msg.topic))
        if str(msg.topic).startswith('subscribe'):

            agent_id = msg.topic.split('/')[1]

            print('A new agent wants to subscribe with id ' + agent_id)
            self.world.add_agent(agent_id)
            return True

        if str(msg.topic).startswith('command'):
            print('Command received')
            self.world.handle_remote_command(msg)
            return True

