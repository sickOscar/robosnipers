
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

def print_help():
    print("""
Robolaser Brain

Options:
    -h, --help      print this help
    --debug     starts pygame debug rendering
    
    """)


if __name__ == '__main__':

    try:
        arguments, values = getopt.getopt(sys.argv[1:], ['h'], ['help'])
        for currentArgument, currentValue in arguments:
            if currentArgument in ("-h", "--help"):
                print_help()
                sys.exit(0)

    except getopt.error as err:
        pass
        # output error, and return with an error code
        #print (str(err))
        #sys.exit(2)

    # Physics
    world = World.get_instance(cli_args=sys.argv)

    # MQTT
    mqtt_client = MqttClient(world)
    world.set_mqtt_client(mqtt_client)

    # Websocket registry
    registry = SocketRegistry.get_instance()

    simulator = Simulator(
        world=world, 
        socket_registry=registry, 
        mqtt_client=mqtt_client,
        cli_args=sys.argv)

    # FE websocket Server
    app = AppServer()
    app.start()

