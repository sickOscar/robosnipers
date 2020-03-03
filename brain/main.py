
import sys
import getopt
import asyncio
import threading
import time

from net.app_server import AppServer
from net.socket_registry import SocketRegistry
from net.mqtt_client import MqttClient

from physics.world import World

from simulator.simulator import Simulator
import argparse

if __name__ == '__main__':

    try:
        parser = argparse.ArgumentParser(description="Robolaser Brain")
        parser.add_argument('--debug', help="starts pygame debug rendering", action="store_true")
        args = parser.parse_args()

        # Physics
        world = World.get_instance(debug=args.debug)

        # MQTT
        mqtt_client = MqttClient(world)
        world.set_mqtt_client(mqtt_client)

        # Websocket registry
        registry = SocketRegistry.get_instance()

        simulator = Simulator(
            world=world, 
            socket_registry=registry, 
            mqtt_client=mqtt_client
            )

        # FE websocket Server
        app = AppServer()
        app.start()

    except KeyboardInterrupt:
        sys.exit(0)
