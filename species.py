
import random
from genome import genome
import statistics 

class species(object):
    """species"""

    def __init__(self):
        self.genomeArray = [] # [[genome, fitness]...]
        self.repArray = None
        self.repInputInnovations = []
        self.repMiddleInnovations = []
        self.threshold = 0
        self.c1 = 0
        self.c2 = 0
        self.c3 = 0

    def init(self, genomeAndFitness, threshold, c1, c2, c3):
        self.threshold = threshold
        self.c1 = c1
        self.c2 = c2
        self.c3 = c3
        self.repArray = genomeAndFitness
        self.genomeArray.append(genomeAndFitness)

        # get innovations from genome
        self.repInputInnovations = genomeAndFitness[0].getInputInnovations()
        self.repMiddleInnovations = genomeAndFitness[0].getMiddleInnovations()

    # checks if genome is part of species and adds.
    # returns true if added or false if not
    def checkAndAddGenome(self, genomeAndFitness):
        # check if genome is compatible
        inInnovations = genomeAndFitness[0].getInputInnovations()
        midInnovations = genomeAndFitness[0].getMiddleInnovations()

        inDiff = self.diffBetweenInnovations(self.repInputInnovations, inInnovations)
        midDiff = self.diffBetweenInnovations(self.repMiddleInnovations, midInnovations)
        wDiff = self.diffBetweenWeights(self.repArray[0].bonds, genomeAndFitness[0].bonds)

        n = len(self.repArray[0].bonds)
        if len(genomeAndFitness[0].bonds) > n:
            n = len(genomeAndFitness[0].bonds)

        diff = (self.c1*inDiff)/n + (self.c2*midDiff)/n + (self.c3*wDiff)

        if diff <= self.threshold:
            self.genomeArray.append(genomeAndFitness)
            return True
        return False

    def cullSpecies(self):
        avgFitness = self.getAvgFitness()
        fitnessArray = []
        for genomeAndFitness in self.genomeArray:
            fitnessArray.append(genomeAndFitness[1])

        if len(fitnessArray) > 1:
            stdev = statistics.stdev(fitnessArray)

            newGenomeArray = []
            for i in range(0, len(self.genomeArray)):
                genomeAndFitness = self.genomeArray[i]
                if genomeAndFitness[1] >= avgFitness - stdev:
                    newGenomeArray.append(genomeAndFitness)

            self.genomeArray = newGenomeArray

    def createOffspring(self):
        g1 = random.choice(self.genomeArray)
        g2 = random.choice(self.genomeArray)

        baby = genome()
        baby.inputNodes = g1[0].inputNodes
        baby.outputNodes = g1[0].outputNodes

        babyBonds = []
        babyNodes = []
        idCount = len(g1[0].inputNodes) + len(g1[0].outputNodes) - 2
        # find all similar bonds
        g1Extra = []
        for b1 in g1[0].bonds:
            added = False
            for b2 in g2[0].bonds:
                if b1.innovation == b2.innovation:
                    added = True
                    # choose a random innovation
                    if random.randint(0,1) == 1:
                        babyBonds.append(b1)
                    else:
                        babyBonds.append(b2)
                    
                    # add node if type "h"
                    if not baby.hasNode(b1.inNode.id):
                        babyNodes.append(b1.inNode)
                        idCount += 1
                    if not baby.hasNode(b1.outNode.id):
                        babyNodes.append(b1.outNode)
                        idCount += 1
            if added == False:
                g1Extra.append(b1)

        # if g1 fitness is best then add all innovations from g1
        if g1[1] > g2[1] or g1[1] == g2[1]:
            for b in g1Extra:
                babyBonds.append(b)
                if not baby.hasNode(b.inNode.id):
                    babyNodes.append(b.inNode)
                    idCount += 1
                if not baby.hasNode(b.outNode.id):
                    babyNodes.append(b.outNode)
                    idCount += 1
        
        if g2[1] > g1[1] or g1[1] == g2[1]:
            # grab extra innovations for g2 and add them
            g2Extra = []
            for b2 in g2[0].bonds:
                if not g1[0].hasInnovation(b2.innovation):
                    g2Extra.append(b2)

            for b in g2Extra:
                babyBonds.append(b)
                if not baby.hasNode(b.inNode.id):
                    babyNodes.append(b.inNode)
                    idCount += 1
                if not baby.hasNode(b.outNode.id):
                    babyNodes.append(b.outNode)
                    idCount += 1

        baby.bonds = babyBonds
        baby.nodes = babyNodes
        baby.idCount = idCount

        return baby

    def assignRepAndReset(self):
        # randomly choose new rep
        self.rep = random.choice(self.genomeArray)
        self.repInputInnovations = self.rep[0].getInputInnovations()
        self.repMiddleInnovations = self.rep[0].getMiddleInnovations()

        # reset genome array
        self.genomeArray = []
        self.genomeArray.append(self.rep)

    # takes in two innovations and return how many differences are found
    def diffBetweenInnovations(self, inno1, inno2):
        difference = 0
        # check from inno1
        for num in inno1:
            if not num in inno2:
                difference += 1
        # check from inno2
        for num in inno2:
            if not num in inno1:
                difference += 1
        return difference

    def diffBetweenWeights(self, bonds1, bonds2):
        wDiff = 0
        for b1 in bonds1:
            for b2 in bonds2:
                if b1.innovation == b2.innovation:
                    wDiff += abs(b1.weight - b2.weight)
        return wDiff

    def getAvgFitness(self):
        total = 0
        for genomeAndFitness in self.genomeArray:
            total += genomeAndFitness[1]
        return total / len(self.genomeArray)