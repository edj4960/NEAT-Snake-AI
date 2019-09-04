from node import node

class bond(object):
    """bond"""

    def __init__(self):
        self.innovation = 0
        self.inNode = None
        self.outNode = None
        self.weight = 0
        self.enabled = False

    def init(self, inNode, outNode, weight, enabled):
        self.inNode = inNode
        self.outNode = outNode
        self.weight = weight
        self.enabled = enabled