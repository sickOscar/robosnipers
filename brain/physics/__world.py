import Box2D
import json
import pygame
from pygame.locals import (QUIT, KEYDOWN, K_ESCAPE)
import threading
import time

from .agent import Agent


class __World:

    def __init__(self):
        # load map
        self.map = self.load_map()
        # load world
        self.load_world(self.map)
        # load agents
        self.agents = {}

        self.debug_objects = []

        run_thread = threading.Thread(target=self.run_game, daemon=True)
        run_thread.start()

        self.sensors_running = True
        sensor_thread = threading.Thread(target=self.send_sensor_data, daemon=True)
        sensor_thread.start()

    def run_game(self):

        # --- constants ---
        # Box2D deals with meters, but we want to display pixels,
        # so define a conversion factor:
        PPM = 5  # pixels per meter
        TARGET_FPS = 60
        TIME_STEP = 1.0 / TARGET_FPS
        SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 680

        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
        pygame.display.set_caption('Robolaser')
        clock = pygame.time.Clock()

        colors = {
            Box2D.b2.staticBody: (255, 255, 255, 255),
            Box2D.b2.dynamicBody: (127, 127, 127, 255),
        }

        running = True
        while running:
            # Check the event queue
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    # The user closed the window or pressed escape
                    running = False

            screen.fill((0, 0, 0, 0))

            # Draw the world
            for body in self.world.bodies:
                # The body gives us the position and angle of its shapes
                for fixture in body.fixtures:
                    # The fixture holds information like density and friction,
                    # and also the shape.
                    shape = fixture.shape

                    # Naively assume that this is a polygon shape. (not good normally!)
                    # We take the body's transform and multiply it with each
                    # vertex, and then convert from meters to pixels with the scale
                    # factor.
                    vertices = [(body.transform * v) * PPM for v in shape.vertices]

                    # But wait! It's upside-down! Pygame and Box2D orient their
                    # axes in different ways. Box2D is just like how you learned
                    # in high school, with positive x and y directions going
                    # right and up. Pygame, on the other hand, increases in the
                    # right and downward directions. This means we must flip
                    # the y components.
                    vertices = [(v[0], SCREEN_HEIGHT - v[1]) for v in vertices]

                    pygame.draw.polygon(screen, colors[body.type], vertices)

            # Draw debug objects 
            for debug_object in self.world.debug_objects:
                
                if debug_object['type'] == 'segment':

                    p1 = debug_object['props']['p1']
                    p2 = debug_object['props']['p2']

                    p1_translated = (p1[0] * PPM, SCREEN_HEIGHT - p1[1] * PPM)
                    p2_translated = (p2[0] * PPM, SCREEN_HEIGHT - p2[1] * PPM)

                    pygame.draw.aaline(
                        screen, 
                        (255, 0, 0), 
                        p1_translated, 
                        p2_translated
                    )


            for agent in self.agents:
                self.agents[agent].update()

            # Make Box2D simulate the physics of our world for one step.
            # Instruct the world to perform a single step of simulation. It is
            # generally best to keep the time step and iterations fixed.
            # See the manual (Section "Simulating the World") for further discussion
            # on these parameters and their implications.
            self.world.Step(TIME_STEP, 10, 10)

            self.world.debug_objects = []

            for agent in self.agents:
                self.agents[agent].raycast()

            # Flip the screen and try to keep at the target FPS
            pygame.display.flip()
            clock.tick(TARGET_FPS)


    def load_map(self):
        f = open('../assets/map.json', 'r')
        return json.loads(f.read())

    def load_world(self, map):
        
        self.world = Box2D.b2World(gravity=(0,0), doSleep=True)

        self.world.debug_objects = []

        for obstacle_spec in map['obstacles']:
            self.create_obstacle(obstacle_spec)


    def create_obstacle(self, obstacle_spec):

        obstacle_body_def = Box2D.b2BodyDef()
        obstacle_body_def.position = (0, 0)

        obstacle_body = self.world.CreateBody(obstacle_body_def)

        v = []
        for vertex in obstacle_spec['vertices']:
            v.append((vertex[0], vertex[1]))

        obstacle_box = Box2D.b2PolygonShape(vertices=v)
        obstacle_box_fixture = Box2D.b2FixtureDef(shape=obstacle_box)

        obstacle_body.CreateFixture(obstacle_box_fixture)
        

    def get_status(self):
        states = []
        for agent in self.agents:
            states.append({
                "x": 0,
                "y": 0
            })

    def add_agent(self, agent_id):
        try:
            if agent_id in self.agents:
                print("Recycling agent " + agent_id)
            else:
                print("Adding agent " + agent_id)
                self.agents[agent_id] = Agent(self.world, agent_id)
        except Exception as e:
            print(e)

    def handle_remote_command(self, message):

        topic_tokens = str(message.topic).split('/')
        agent_id = topic_tokens[1]
        command = topic_tokens[2]
        payload = message.payload.decode('utf-8')
        print(payload)
        

        print("Executing " + command + " on agent " + agent_id + " " + payload)

        if not self.agents[agent_id]:
            print("Unknown agent")
            return False

        active_agent = self.agents[agent_id]

        if command == 'move':
            active_agent.move()

        if command == 'turn':
            active_agent.turn(payload)

        if command == 'rear':
            active_agent.rear()

        if command == 'stop':
            active_agent.stop()

    def set_mqtt_client(self, client):
        self.mqtt_client = client

    def send_sensor_data(self):
        while self.sensors_running:

            time.sleep(.2)

            for agent_id in self.agents:
                agent = self.agents[agent_id]

                front_left = agent.sensors['front_left'] or 200
                front_right = agent.sensors['front_right'] or 200
                rear = agent.sensors['rear'] or 200

                payload = "|".join((str(front_left), str(front_right), str(rear)))
                topic = "/".join(("sensors", agent_id, "proximity"))

                self.mqtt_client.publish(topic, payload)

                

            