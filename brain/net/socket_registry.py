
from .__registry import Registry

class SocketRegistry:

    instance = None

    @classmethod
    def get_instance(cls):
        if not SocketRegistry.instance:
            SocketRegistry.instance = Registry()
        return SocketRegistry.instance

    def __init__(self):
        raise Exception('Unable to call SocketRegistry construcotr')
