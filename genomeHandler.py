from genome import genome
from species import species
from networkPrinter import networkPrinter
import pickle

class genomeHandler(object):
    """genomeHandler"""

    INCOUNT = 0
    OUTCOUNT = 0
    GENOMES_PER_GEN = 0
    genomes = []
    InnovationNum = 0 # innovation number
    innovations = [] # saves innovations for a generation. [bond,bond...]
    currentGenome = None
    highestFitness = None
    # Species vars
    speciesArray = []
    THRESHOLD = 3
    C1 = 1
    C2 = 1
    C3 = .4

    def init(self, inCount, outCount, genomePerGen):
        self.INCOUNT = inCount
        self.OUTCOUNT = outCount
        self.GENOMES_PER_GEN = genomePerGen

        for i in range(0, self.GENOMES_PER_GEN):
            g = genome()
            self.innovations = g.init(inCount, outCount, True, self.innovations)
            self.genomes.append(g)
        self.currentGenome = self.genomes.pop(0)

# generation code
    # takes inputs from game and returns outputs 
    def feedInputs(self, inputs):
        return self.currentGenome.feedForward(inputs)

    # takes fitness for finished simulation
    def endSimulation(self, fitness):
        # save genome 
        genomeAndFitness = [self.currentGenome, fitness]

        if self.highestFitness == None or fitness > self.highestFitness:
            with open("bestSnake.py", 'wb') as f:
                pickle.dump(genomeAndFitness, f)
            #printer = networkPrinter()
            #printer.exportGenome(self.currentGenome, "bestGenome.jpg")

        result = False
        for s in self.speciesArray:
            result = s.checkAndAddGenome(genomeAndFitness)
            if result == True:
                break

        if result == False: # unable to add to species so create new species
            newSpecies = species()
            newSpecies.init(genomeAndFitness, self.THRESHOLD, self.C1, self.C2, self.C3)
            self.speciesArray.append(newSpecies)
        
        # assign new genome if one present
        if len(self.genomes) != 0:
            self.currentGenome = self.genomes.pop(0)
        else:
            self.startNextGen()

    # handles next generation. Speciates, breeds and mutates next gen
    def startNextGen(self):
        print("STARTING NEXT GEN")
        # determine how many offspring each species can have
        totalFitness = 0 # sum of all fitness scores from all species
        for s in self.speciesArray:
            totalFitness += s.getAvgFitness()

        print("Number of Species: ", len(self.speciesArray))
        # BREED
        for s in self.speciesArray:
            allocatedOffspring = int(round((s.getAvgFitness()/totalFitness) * self.GENOMES_PER_GEN ))
            print("Num of Offspring: ", allocatedOffspring)
            s.cullSpecies()
            for i in range(0,allocatedOffspring):
                self.genomes.append(s.createOffspring())
            # reset species for next gen
            s.assignRepAndReset()

        # MUTATE
        for g in self.genomes:
            self.innovations = g.mutationHandler(self.innovations)

        # Add current genome for next gen
        self.currentGenome = self.genomes.pop(0)

# def main():
#     g = genome()
#     g.init(3, 3)
#     g.mutationHandler()
#     g.mutationHandler()
#     g.mutationHandler()
#     g.printGenome()

#     printer = networkPrinter()
#     printer.exportGenome(g, "genome1.jpg")

#     inputs = [1, 0, -1]
#     output = g.feedForward(inputs)
#     print("Inputs:\n", inputs)
#     print("Outputs:\n", output)



# main()