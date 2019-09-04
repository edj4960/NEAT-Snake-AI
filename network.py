import random
import math
import pickle

class network(object):
    """Neural Network"""

    def init(self):
        global inputSize, W, B, outputs, genFile, bestFile, highScore, snakeIndex, RANGE
        global bsW, bsB, allOutputs, Snakes, SNAKE_PER_GEN, deadSnakes, currentGen
        Snakes = []
        deadSnakes = []
        W = [] #Weights
        B = [] #Biases
        bsW = [] #best snake weights
        bsB = [] #best snake baises
        snakeIndex = 0
        highScore = 0
        outputs = [0,0,0]
        currentGen = "currentGen" # Read every snake from file and run
        nextGen = "nextGen" # save result of every snake to be processed
        bestFile = "MVP"
        SNAKE_PER_GEN = 25
        
        #attempts to grab a highscore from the best file
        try:
            with open(bestFile, 'rb') as f:
                 highScore, bsW, bsB = pickle.load(f)
        except:
            pass

        # attempt to load from currentGen 
        try:
            with open(currentGen, 'rb') as f:
                 Snakes = pickle.load(f)
            W = Snakes[snakeIndex][0]
            B = Snakes[snakeIndex][1]
        except:
            # otherwise make 50 random snakes to use
            for i in range(0, SNAKE_PER_GEN):
                wb = self.createSnake()
                toSave = [wb[0], wb[1]]
                Snakes.append(toSave)
                #with open(currentGen, 'a+') as f:
                #    pickle.dump(toSave, f)

            with open(currentGen, 'wb') as f:
                pickle.dump(Snakes, f)

            W = Snakes[snakeIndex][0]
            B = Snakes[snakeIndex][1]

    def createSnake(self):
        weights = []
        baises = []
        weights.append(self.createWeightLayer(400,200))
        baises.append(self.createBaisLayer(200))
        # weights.append(self.createWeightLayer(200,200))
        # baises.append(self.createBaisLayer(200))
        weights.append(self.createWeightLayer(200,4))
        baises.append(self.createBaisLayer(4))

        return [weights, baises]

    def save(self, score):
        global highScore, snakeIndex, SNAKE_PER_GEN, W, B, deadSnakes, bestFile, bsW, bsB
        
        # check if new highscore and update the MVP file
        if score > highScore:
            print('NEW HIGH SCORE!')
            highScore = score
            toSave = [highScore, W, B]
            bsW = W
            bsB = B
            with open(bestFile, 'wb') as f:
                pickle.dump(toSave, f)

        # append current snake to next gen file
        toSave = [score, W, B]
        if snakeIndex == 0: 
            # if first snake then restart array of dead snakes
            deadSnakes = []
        deadSnakes.append(toSave)

        snakeIndex += 1
        if snakeIndex < len(Snakes):
            W = Snakes[snakeIndex][0]
            B = Snakes[snakeIndex][1]
        else:
            snakeIndex = 0
            print("New Generation")
            self.nextGen()

    def nextGen(self):
        global SNAKE_PER_GEN, W, B, Snakes, deadSnakes, snakeIndex, currentGen, bsB, bsW, highScore
        chosenSnakes = [] # snakes chosen to reproduce
        #with open(nextGen, 'rb') as f:
        #     deadSnakes = pickle.load(f)

        # sorting the snakes from greatest to crappiest 
        deadSnakes = sorted(deadSnakes, key=lambda x: x[0], reverse=True)
        
        # choose the best 5 and 2 other random to be used in reproducing
        chosenSnakes = deadSnakes[0:5]
        best = [highScore, bsW, bsB]
        chosenSnakes.append(best)
        chosenSnakes.append(best)
        chosenSnakes.append(deadSnakes[random.randint(5, len(deadSnakes) - 1)])
        #chosenSnakes.append(deadSnakes[random.randint(5, SNAKE_PER_GEN - 1)])
        
        # randSnake = self.createSnake()
        # randSnake.insert(0, 0)
        # chosenSnakes.append(randSnake)

        # restart Snakes
        Snakes = []

        # start reproducing process
        for i in range(0, SNAKE_PER_GEN):
            rdm = random.randint(0,len(chosenSnakes)-1)
            mSnake = chosenSnakes[rdm]
            r = list(range(0, rdm)) + list(range(rdm+1, len(chosenSnakes)-1)) 
            fSnake = chosenSnakes[random.choice(r)]
           
           # create baby snake
            babySnake = self.reproduce(mSnake, fSnake)
            
            # add baby snake to Snakes
            toSave = [babySnake[1], babySnake[2]]
            Snakes.append(toSave)

        with open(currentGen, 'wb') as f:
            pickle.dump(Snakes, f)

        # start next generation
        W = Snakes[snakeIndex][0]
        B = Snakes[snakeIndex][1]

    # takes male and female snake and returns baby snake
    def reproduce(self, m, f):
        # create baby and assign starting values from f
        baby = f.copy()

        #grab weights of each
        bW = baby[1]
        fW = f[1]
        mW = m[1]

        for i in range(0, len(bW)):
            for j in range(0, len(bW[i])):
                for k in range(0, len(bW[i][j])):
                    value = 0
                    if random.randint(0, 1) == 1:
                        value = fW[i][j][k]
                    else:
                        value = mW[i][j][k]
                    bW[i][j][k] = value

        #grab baises of each
        bB = baby[2]
        fB = f[2]
        mB = m[2]
        for i in range(0, len(bB)):
            for j in range(0, len(bB[i])):
                value = 0
                if random.randint(0, 1) == 1:
                    value = fB[i][j]
                else:
                    value = mB[i][j]
                bB[i][j] = value

        return baby

    def avgReproduce(self, m, f):
        # create baby and assign starting values from f
        baby = f.copy()

        score = f[0]
        # if score <= 0:
        #     baby[1] = m.copy()
        #     bB = bB.copy()
        # elif m[0] <=0:
            

        #grab weights of each
        bW = baby[1]
        fW = f[1]
        mW = m[1]

        for i in range(0, len(bW)):
            for j in range(0, len(bW[i])):
                for k in range(0, len(bW[i][j])):
                    bW[i][j][k] = fW[i][j][k] - ((fW[i][j][k] - ((fW[i][j][k]+mW[i][j][k])/2)) * (m[0]/score))

        #grab baises of each
        bB = baby[2]
        fB = f[2]
        mB = m[2]

        for i in range(0, len(bW)):
            for j in range(0, len(bW[i])):
                bB[i][j] = fB[i][j] - ((fB[i][j] - ((fB[i][j]+mB[i][j])/2)) * (m[0]/score))

        return baby

    def createBaisLayer(self, size):
        nGroup = []
        for i in range(0, size):
            nGroup.append(random.uniform(-1,1))
        return nGroup

    def createWeightLayer(self, iSize, oSize):
        weights = []
        for i in range(0, oSize):
            wGroup = []
            for j in range(0, iSize):
                wGroup.append(random.uniform(-1,1))
            weights.append(wGroup)
        return weights

    def makeChoice(self, inputs):
        nodes = inputs.copy()
        allOutputs = []
        allOutputs.append(inputs)
        for i in range(len(W)):
            nodes = self.layerChoice(W[i], B[i], nodes)
            allOutputs.append(nodes)
        return nodes

    def layerChoice(self, ws, bs, nodes):
        os = []
        for i in range(0, len(ws)):
            wGroup = ws[i]
            os.append(0)
            for j in range(0, len(wGroup)):
                os[i] += nodes[j] * wGroup[j]
            os[i] += bs[i]
            os[i] = 1 / (1 + math.exp(-os[i]))
        return os

    #def backProp(self, ideal):
    #    global allOutputs, W, B, LR
    #    oIndex = 0
    #    errors = []

    #    for i in range(0, len(W)):
    #        weights = W[i]
    #        oIndex -= 1
    #        for j in range(0, len(weights)):
    #            wGroup = weights[j]
    #            out = allOutputs[oIndex][j]
    #            if i == 0:
    #                errors.append(ideal[j] - out) # Need to compute error
    #            else:
    #                errors = self.getCombined(wGroup, )
    #            for k in range(0, len(wGroup)):
    #                wGroup[k] += LR * errors[k] * (out*(1-out)) * allOutputs[oIndex-1][k]

    #    for i in range(0, len(B)):
    #        baises = B[i]
    #        for j in range(0, len(baises)):
    #            mutation = random.uniform(-RANGE, RANGE)
    #            baises[bp2] += mutation

    #def getCombined(self, wGroup, index, error):
    #    combined = 0
    #    for j in range(0, len(wGroup)):
    #        combined += wGroup[index] * error
    #    return combined