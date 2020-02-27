import Box2D
import math

# from physics import Tire, RayCastClosestCallback

from .tire import Tire
from .raycast_closest_callback import RayCastClosestCallback

from .const import (
    AGENT_WIDTH, AGENT_HEIGHT, 
    TARGET_COLLISION_GROUP,
    REAR_TIRE_JOINT_X,
    REAR_TIRE_JOINT_Y,
    FRONT_TIRE_JOINT_X,
    FRONT_TIRE_JOINT_Y,
    DEFAULT_STARTING_POSITION
)


class Agent:

    vertices = [
        (AGENT_WIDTH / 2, 0),
        (AGENT_WIDTH / 2, AGENT_HEIGHT),
        (-AGENT_WIDTH / 2, AGENT_HEIGHT),
        (-AGENT_WIDTH / 2, 0)
    ]

    tire_anchors = [
        (-REAR_TIRE_JOINT_X, REAR_TIRE_JOINT_Y),
        (REAR_TIRE_JOINT_X, REAR_TIRE_JOINT_Y),
        (-FRONT_TIRE_JOINT_X, FRONT_TIRE_JOINT_Y),
        (FRONT_TIRE_JOINT_X, FRONT_TIRE_JOINT_Y)
    ]


    def __init__(self, world, id, 
        position=DEFAULT_STARTING_POSITION, 
        vertices=None, 
        density=0.1, 
        **tire_kws):
        
        self.id = id
        self.world = world

        self.direction = []

        self.sensors = {
            "front_left": None,
            "front_right": None,
            "rear": None
        }

        if vertices is None:
            vertices = Agent.vertices

        # MAIN BODY
        self.body = world.CreateDynamicBody(position=position)
        self.body.CreatePolygonFixture(vertices=vertices, density=density)
        self.body.userData = {'obj': self}
        
        self.tires = [Tire(self, **tire_kws) for i in range(4)]

        anchors = Agent.tire_anchors

        joints = self.joints = []
        for tire, anchor in zip(self.tires, anchors):
            j = world.CreateRevoluteJoint(bodyA=self.body,
                                          bodyB=tire.body,
                                          localAnchorA=anchor,
                                          # center of tire
                                          localAnchorB=(0, 0),
                                          enableMotor=False,
                                          maxMotorTorque=1000,
                                          enableLimit=True,
                                          lowerAngle=0,
                                          upperAngle=0,
                                          )

            tire.body.position = self.body.worldCenter + anchor
            joints.append(j)

    def update(self, hz=60.0):
        for tire in self.tires:
            tire.update_friction()

        for tire in self.tires:
            tire.update_drive(self.direction)

        # control steering
        lock_angle = math.radians(30.)
        # from lock to lock in 0.5 sec
        turn_speed_per_sec = math.radians(160.)
        turn_per_timestep = turn_speed_per_sec / hz
        desired_angle = 0.0

        if 'left' in self.direction:
            desired_angle = lock_angle
        elif 'right' in self.direction:
            desired_angle = -lock_angle

        front_left_joint, front_right_joint = self.joints[2:4]
        angle_now = front_left_joint.angle
        angle_to_turn = desired_angle - angle_now

        # TODO fix b2Clamp for non-b2Vec2 types
        if angle_to_turn < -turn_per_timestep:
            angle_to_turn = -turn_per_timestep
        elif angle_to_turn > turn_per_timestep:
            angle_to_turn = turn_per_timestep

        new_angle = angle_now + angle_to_turn
        # Rotate the tires by locking the limits:
        front_left_joint.SetLimits(new_angle, new_angle)
        front_right_joint.SetLimits(new_angle, new_angle)


    def raycast(self):

        sensor_length = 150

        ## FRONT LEFT
        front_left_point1 = self.body.GetWorldPoint(Box2D.b2Vec2(-AGENT_WIDTH / 2, AGENT_HEIGHT))
        angle = self.body.angle + (math.pi / 2) + 0.0
        front_left_d = (sensor_length * math.cos(angle), sensor_length * math.sin(angle))
        front_left_point2 = front_left_point1 + front_left_d

        self.sensors["front_left"] = self.raycast_single_sensor(front_left_point1, front_left_point2)

        ## FRONT RIGHT
        front_right_point1 = self.body.GetWorldPoint(Box2D.b2Vec2(AGENT_WIDTH / 2, AGENT_HEIGHT))
        angle = self.body.angle + (math.pi / 2) - 0.0
        front_right_d = (sensor_length * math.cos(angle), sensor_length * math.sin(angle))
        front_right_point2 = front_right_point1 + front_right_d

        self.sensors["front_right"] = self.raycast_single_sensor(front_right_point1, front_right_point2)

        ## REAR
        rear_point1 = self.body.GetWorldPoint(Box2D.b2Vec2(0, 0))
        angle = self.body.angle - (math.pi / 2)
        rear_d = (sensor_length * math.cos(angle), sensor_length * math.sin(angle))
        rear_point2 = rear_point1 + rear_d

        self.sensors["rear"] = self.raycast_single_sensor(rear_point1, rear_point2)

        self.raycast_camera(
            self.body.GetWorldPoint(Box2D.b2Vec2(0, AGENT_HEIGHT)),
            math.pi / 2,
            50
        )

            
    def raycast_single_sensor(self, start_point, end_point):
        self.world.debug_objects.append({
            "type": "segment",
            "props": {
                "p1": start_point,
                "p2": end_point
            }
        })

        callback = RayCastClosestCallback()
        self.world.RayCast(callback, start_point, end_point)

        if callback.hit:
            result_vec = Box2D.b2Vec2(
                callback.point.x - start_point.x,
                callback.point.y - start_point.y,
            )
            return result_vec.length
            
        return None


    def raycast_camera(self, start_point, view_field_angle, length):

        samples = 20
        starting_angle = view_field_angle / 2
        increment = view_field_angle / samples

        contacts = []
        min_angle = None
        max_angle = None

        min_vec = None
        max_vec = None

        for index in range(0, samples):
            angle = self.body.angle + starting_angle + (increment * index)
            d = (length * math.cos(angle), length * math.sin(angle))
            point_2 = start_point + d

            self.world.debug_objects.append({
                "type": "segment",
                "props": {
                    "p1": start_point,
                    "p2": point_2
                }
            })

            callback = RayCastClosestCallback(TARGET_COLLISION_GROUP)
            self.world.RayCast(callback, start_point, point_2)

            if callback.hit:

                if min_angle is not None:
                    min_angle = min(min_angle, angle)
                else:
                    min_angle = angle

                if max_angle is not None:
                    max_angle = max(max_angle, angle)
                else:
                    max_angle = angle

                result_vec = Box2D.b2Vec2(
                    callback.point.x - start_point.x,
                    callback.point.y - start_point.y,
                )

                if angle is min_angle:
                    min_vec = result_vec

                if angle is max_angle:
                    max_vec = result_vec

               

        # if len(contacts) > 0:
        #     print('SEE TARGET')

            # target_vector = max_vec.Normalize() - min_vec.Normalize()

            # print(target_vector)
            # print(min_angle, max_angle)

    def get_status_string(self):
        tokens = [
            str(self.id),
            self.body.position[0],
            self.body.position[1],
            self.body.angle
        ]
        return "|".join(str(t) for t in tokens)

    def move(self):
        self.direction = ["up"]

    def turn(self, direction):
        self.direction = ['up', direction]

    def rear(self):
        self.direction = ['down']

    def stop(self):
        self.direction = []