import threading
import time
import asyncio

class Simulator:

    def __init__(self, world, socket_registry, mqtt_client):
        
        self.world = world
        self.socket_registry = socket_registry
        self.mqtt_client = mqtt_client

        loop = asyncio.new_event_loop()
        t = threading.Thread(target=self.tick, args=(loop,), name="Socket", daemon=True)
        t.start()
    
    def tick(self, loop):

        asyncio.set_event_loop(loop)

        running = True
        while running:

            string_tokens = [self.world.agents[agent_id].get_status_string() for agent_id in self.world.agents]

            message = '+'.join(string_tokens)
            # print(message)
            self.socket_registry.broadcast(message)

            # check sensors for every agent
            # print('simulating')
            # send status via Websocket
                
            # send sensor data via MQTT
            time.sleep(1 / 30)
