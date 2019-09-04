import math

class node(object):
    """node"""

    def __init__(self):
        self.id = 0
        self.bias = 0
        self.type = ""

        # Simulation variables
        self.inputs = 0 # amount of nodes that input into node
        self.value = 0 # current value during simulation
        self.ready = False # if node can contribute as an output
        self.inserted = 0 # amount of nodes that have given their values during simulation

    def init(self, bias, id, type):
        self.bias = bias
        self.id = id
        self.type = type # either (i)nput, (o)utput, or (h)idden

    # adds input from one node into value and checks if all inputs have been added
    def insertWeight(self, value):
        self.value += value
        #print("New Value: ", self.value)
        self.inserted += 1
        if self.inserted >= self.inputs:
            #print("Entering Sigmoid Value: " + str(value + self.bias))
            self.value = self.sigmoid(value + self.bias)
            self.ready = True
            #print("Completed Value: " + str(self.value))
        #print("")

    # sets node to original state to start new simulation
    def reset(self):
        self.value = 0
        self.inserted = 0
        ready = False

    def sigmoid(self, x):
        return 1 / (1 + math.exp(-x))
