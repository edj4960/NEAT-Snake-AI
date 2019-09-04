import random
from bond import bond
from node import node

class genome(object):
    """genome"""
    
    def __init__(self):
        self.bonds = []
        self.nodes = []
        self.inputNodes = []
        self.outputNodes = []
        self.idCount = 0
        self.storedInnovations = []

    def init(self, inputs, outputs, rdm, innovations):
        # Create Input and Output nodes
        self.createNodeGroup(inputs, 'i')
        self.createNodeGroup(outputs, 'o')
        self.storedInnovations = innovations

        if rdm == False:
            return

        # Randomly make bonds from inputs to outputs or to hidden nodes
        while(len(self.bonds) == 0):
            for n in self.inputNodes:
                if random.randint(0,1) == 1:
                    output = random.choice(self.outputNodes)
                    if not self.doesBondExist(n, output):
                        output.inputs += 1
                        b = bond()
                        b.init(n, output, random.uniform(-1, 1), True)
                        b = self.createBondFromInnovation(b, False)
                        self.bonds.append(b)
        
        return self.storedInnovations

    # Takes inputs and creates outputs
    def feedForward(self, inputs):
        # Check that inputs match
        if len(inputs) != len(self.inputNodes):
            print("***ERROR: INVALID AMOUNT OF INPUTS***")
            print("SAVED INPUTS: ", len(self.inputNodes))
            print("GIVEN INPUTS: ", len(inputs))


        # initialize input values
        for i in range(0, len(self.inputNodes)):
            self.inputNodes[i].value = inputs[i]
            self.inputNodes[i].ready = True
        
        # set any node with 0 inputs to ready
        for n in self.nodes:
            if n.inputs == 0:
                n.ready = True

        # go through every bond and do calculations
        simBonds = self.bonds.copy()
        while len(simBonds) != 0:
            b = simBonds[0]
            if b.enabled == False:
                del simBonds[0]
            else:
                inNode = b.inNode
                outNode = b.outNode
                # if input is ready
                if inNode.ready == True:
                    #print("Bond: " + str(inNode.id) + " -> " + str(outNode.id))
                    #print("Value: " + str(inNode.value) + " Weight: " + str(b.weight))
                    # feed forward and remove bond
                    outNode.insertWeight(inNode.value * b.weight)
                    del simBonds[0]
                else:
                    # else move bond to bottom of list
                    simBonds += [simBonds.pop(0)]
        
        # create outputs
        outputs = []
        for o in self.outputNodes:
            outputs.append(o.value)
        
        # Simulation finished, reset nodes
        for node in self.nodes:
            node.reset()
        
        return outputs
    
    def createNodeGroup(self, amount, type):
        for i in range(0, amount):
            n = node()
            n.init(random.uniform(-1, 1), self.idCount, type)
            self.idCount += 1
            self.nodes.append(n)

            if type == 'i':
                self.inputNodes.append(n)
            elif type == 'o':
                self.outputNodes.append(n)

# MUTATIONS
    # rate for each type of mutation
    mutationRates = [2,2,2,2]

    # Handles the mutation of the genome
    def mutationHandler(self, innovations):
        self.storedInnovations = innovations
        for i in range(0, self.mutationRates[0]):
            self.pointMutate(.5)
        for i in range(0, self.mutationRates[1]):
            self.linkMutate()
        for i in range(0, self.mutationRates[2]):
            self.nodeMutate()
        for i in range(0, self.mutationRates[1]):
            self.enableDisableMutate()

        # update mutation rates
        for i in range(0, 4):
            self.mutationRates[i] += random.randint(-1,1)
            if self.mutationRates[i] < 0:
                self.mutationRates[i] = 0
            elif self.mutationRates[i] > 2:
                self.mutationRates[i] = 2

        return self.storedInnovations

    # randomly updates a weight or bias
    def pointMutate(self, step):
        # mutate weights
        b = random.choice(self.bonds)
        b.weight += random.uniform(-step, step)

        # mutate baises 
        node = random.choice(self.nodes)
        node.bias += random.uniform(-step, step)

    # Randomly adds a new connection to the network with a random weight between -2 and 2
    def linkMutate(self):
        inNode = None
        outNode = None

        itrCount = 0 # make sure the while loop ends if no more connections can be made
        while(inNode is None or outNode is None) and itrCount <= len(self.nodes)**2:
            node1 = random.choice(self.nodes)
            node2 = random.choice(self.nodes)
            itrCount += 1
            if node1.id != node2.id and self.compatibleNodes(node1, node2) == True:         
                if node2.type == "i" or node1.type == "o":
                    inNode = node2
                    outNode = node1
                else:
                    inNode = node1
                    outNode = node2

        if inNode is not None:
            b = bond()
            b.init(inNode, outNode, random.uniform(-2,2), True)
            b = self.createBondFromInnovation(b, False)
            self.bonds.append(b)

            # check that no loop exists
            if self.bondCreatesLoop([b.inNode.id], b.inNode, b.outNode):
                tempNode = b.inNode
                b.inNode = b.outNode
                b.outNode = tempNode
            # self.printBond(b)
            # increment inputs for out node
            b.outNode.inputs += 1
        else:
            print("***Could not complete link mutation***")

    # Disables a connection and creates the same connection with a node inbetween
    def nodeMutate(self):
        # choose a random ENABLED bond and disable it
        b = None
        itrCount = 0
        while(b == None) and itrCount <= len(self.nodes)**2:
            itrCount += 1
            b = random.choice(self.bonds)
            if b.enabled == False:
                b = None

        if b == None:
            return

        b.enabled = False
        inNode = b.inNode
        outNode = b.outNode

        # create middle node
        middleNode = node()
        middleNode.init(0, self.idCount, "h")
        self.idCount += 1
        middleNode.inputs = 1
        self.nodes.append(middleNode)

        # create bond from inNode to middleNode
        b1 = bond()
        b1.init(inNode, middleNode, 1, True)
        b1 = self.createBondFromInnovation(b1, True)
        middleNode = b1.outNode
        self.bonds.append(b1)

        # create bond from middleNode to outNode
        b2 = bond()
        b2.init(middleNode, outNode, b.weight, True)
        b2 = self.createBondFromInnovation(b2, False)
        self.bonds.append(b2)

    # randomly enables or disables connections
    def enableDisableMutate(self):
        b = random.choice(self.bonds)
        if b.enabled == False:
            b.enabled = True
            b.outNode.inputs += 1
        else:
            b.enabled = False
            b.outNode.inputs -= 1

# UTILITIES
    # returns innovations from inputs
    def getInputInnovations(self):
        innovations = []
        for n in self.inputNodes:
            nBonds = self.getBondsFromInNode(n)
            if nBonds != None:
                for b in nBonds:
                    innovations.append(b.innovation)
        return innovations

    # returns innovations from middle layers
    def getMiddleInnovations(self):
        innovations = []
        for n in self.nodes:
            nBonds = self.getBondsFromInNode(n)
            if nBonds != None:
                for b in nBonds:
                    # check that innovation is not already added and not from an input
                    if not b.innovation in innovations and b.inNode.type != 'i':
                        innovations.append(b.innovation)
        return innovations

    # takes two nodes and ensures they are compatible
    def compatibleNodes(self, n1, n2):
        if (n1.type == 'i' and n2.type == 'i') or (n1.type == 'o' and n2.type == 'o'):
            return False
        
        if self.doesBondExist(n1.id, n2.id) == True:
            return False

        return True

    # takes the ids of two nodes and returns if they have a current bond
    def doesBondExist(self, n1, n2):
        for bond in self.bonds:
            inID = bond.inNode.id
            outID = bond.outNode.id
            if (inID == n1 or outID == n1) and (inID == n2 or outID == n2):
                return True
        return False

    # goes through network and finds if loop is created
    def bondCreatesLoop(self, previousNodes, inNode, outNode):
        # check if out node is in list
        if outNode.id in previousNodes:
            return True 
        # add out node to list
        previousNodes.append(outNode.id)
        # make out node the new in node
        inNode = outNode

        # iterate through bonds
        nodeBonds = self.getBondsFromInNode(inNode)
        if nodeBonds != None:
            for b in nodeBonds:
                result = self.bondCreatesLoop(previousNodes, inNode, b.outNode)
                if result == True:
                    return True

        return False

    def printGenome(self):
        print("Genome Info\nBonds:")
        for bond in self.bonds:
            self.printBond(bond)

        print("Nodes:")
        for node in self.nodes:
            print("Id: ", node.id)
            print("Bias: ", node.bias)
            print("Inputs: ", node.inputs)
            print()
    
    def printBond(self, bond):
        print("Innovation: ", bond.innovation)
        print("In Node:", bond.inNode.id)
        print("Out Node:", bond.outNode.id)
        print("Weight: ", bond.weight)
        print("Enabled: ", bond.enabled)
        print()

    def getBondsFromInNode(self, node):
        nodeBonds = []
        for b in self.bonds:
            if b.inNode.id == node.id:
                nodeBonds.append(b)
        
        if len(nodeBonds) != 0:
            return nodeBonds
        return None
    
    def hasNode(self, nodeId):
        for n in self.nodes:
            if n.id == nodeId:
                return True
        return False

    def hasInnovation(self, iNum):
        for b in self.bonds:
            if b.innovation == iNum:
                return True
        return False

    # Takes in new bond/node information, assigns an innovation number and returns bond
    def createBondFromInnovation(self, b, isNew):
        # grab only unique innovations
        innovations = []
        for i in self.storedInnovations:
            found = False
            for bnd in self.bonds:
                if i.innovation == bnd.innovation:
                    found = True
            if found == False:
                innovations.append(i)

        # 
        for i in innovations:
            if isNew == True: # Adding new node
                if i.inNode.id == b.inNode.id:
                    b.outNode.id = i.outNode
                    b.innovation = i.innovation
                    return b
            else: # just a bond
                if i.inNode.id == b.inNode.id and i.outNode.id == b.outNode.id:
                    b.innovation = i.innovation
                    return b

        # no matching innovation found. Add innovation
        b.innovation = self.findNextInnoNumber()
        self.storedInnovations.append(b)
        return b        

    def findNextInnoNumber(self):
        maxI = 0
        for i in self.storedInnovations:
            if i.innovation > maxI:
                maxI = i.innovation
        maxI += 1
        return maxI