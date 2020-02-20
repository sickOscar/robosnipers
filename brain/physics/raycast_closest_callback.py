import Box2D
from .const import TARGET_COLLISION_GROUP

class RayCastClosestCallback(Box2D.b2RayCastCallback):
    """This callback finds the closest hit"""

    def __repr__(self):
        
        return 'Closest hit'

    def __init__(self, group=None, **kwargs):
        Box2D.b2RayCastCallback.__init__(self, **kwargs)
        self.group = group
        self.fixture = None
        self.hit = False

    def ReportFixture(self, fixture, point, normal, fraction):
        '''
        Called for each fixture found in the query. You control how the ray
        proceeds by returning a float that indicates the fractional length of
        the ray. By returning 0, you set the ray length to zero. By returning
        the current fraction, you proceed to find the closest point. By
        returning 1, you continue with the original ray clipping. By returning
        -1, you will filter out the current fixture (the ray will not hit it).
        '''
        self.hit = True
        self.fixture = fixture
        self.point = Box2D.b2Vec2(point)
        self.normal = Box2D.b2Vec2(normal)
        
        # se ho specificato un gruppo particolare nel costruttore
        # e la fixture non appartiene a quel gruppo, non ho una hit
        if self.hit:
            if self.group and self.fixture.filterData.groupIndex is not self.group:
                self.hit = False
        
        # NOTE: You will get this error:
        #   "TypeError: Swig director type mismatch in output value of
        #    type 'float32'"
        # without returning a value
        return fraction