import math


class Servo:


    def __init__(self, agent):

        self.world = agent.world

        position = (0,0)
        density = 0.1
        dimensions = (2, 2)

        self.tracking = False

        self.lower_limit = -(math.pi / 2)
        self.upper_limit = math.pi / 2
        self.direction = 'left'

        self.body = self.world.CreateDynamicBody(position=position)
        self.body.CreatePolygonFixture(box=dimensions, density=density)
        self.body.userData = {
            'obj': self,
            'color': (255, 100, 127, 255)
        }

    def set_joint(self, joint):
        self.joint = joint


    def update(self):
        if self.tracking is True:
            self.track()
        else:
            # radar routine
            self.radar()


    def radar(self):
        servo_angle = self.joint.angle
        
        if self.direction is 'left' and servo_angle > self.lower_limit :
            self.joint.SetLimits(servo_angle - 0.01, servo_angle - 0.01)

        if self.direction is 'right' and servo_angle < self.upper_limit:
            self.joint.SetLimits(servo_angle + 0.01, servo_angle + 0.01)

        if servo_angle >= self.upper_limit:
            self.direction = 'left'
        
        if servo_angle <= self.lower_limit:
            self.direction = 'right'

    def track(self):
        print('TRACKING')