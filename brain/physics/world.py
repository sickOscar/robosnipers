from .__world import __World as Real

class World:

    instance = None

    def __init__(self):
        raise Exception('Unable to init singleton')

    @classmethod
    def get_instance(cls):
        if not World.instance:
            World.instance = Real()
        return World.instance
