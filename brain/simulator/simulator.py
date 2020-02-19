import threading
import time

class Simulator:

    def __init__(self, world, socket_registry, mqtt_client):
        
        self.world = world
        self.socket_registry = socket_registry
        self.mqtt_client = mqtt_client

        t = threading.Thread(target=self.tick, daemon=True)
        t.start()
    
    def tick(self):
        running = True
        while running:
            # check sensors for every agent
            # print('simulating')
            # send status via Websocket
                
            # send sensor data via MQTT
            time.sleep(1)
