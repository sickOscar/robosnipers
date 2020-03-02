from .__world import __World as Real

class World:

    instance = None

    def __init__(self):
        raise Exception('Unable to init singleton')

    @classmethod
    def get_instance(cls, debug = False):
        if not World.instance:
            World.instance = Real(debug)
        return World.instance
