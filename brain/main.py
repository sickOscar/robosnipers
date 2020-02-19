

import asyncio
import threading
import time

from net.app_server import AppServer
from net.socket_registry import SocketRegistry
from net.mqtt_client import MqttClient

from physics.world import World

from simulator.simulator import Simulator


if __name__ == '__main__':

    # Physics
    world = World.get_instance()

    # MQTT
    mqtt_client = MqttClient(world)
    world.set_mqtt_client(mqtt_client)

    # Websocket registry
    registry = SocketRegistry.get_instance()

    simulator = Simulator(world, registry, mqtt_client)

    # FE websocket Server
    app = AppServer()
    app.start()

