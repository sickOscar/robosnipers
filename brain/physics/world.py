from .__world import __World as Real

class World:

    instance = None

    def __init__(self):
        raise Exception('Unable to init singleton')

    @classmethod
    def get_instance(cls, cli_args):
        if not World.instance:
            World.instance = Real(cli_args)
        return World.instance
