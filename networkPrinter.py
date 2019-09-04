
from PIL import Image, ImageDraw, ImageFont

class networkPrinter(object):
	"""network Printer"""

	width = 1000
	height = width
	white = (255, 255, 255)
	draw = 0
	r = 25 # circle radius
	# xGap = 250
	black = (0,0,0)
	positions = []
	genome = None

	def exportGenome(self, genome, filename):
		self.genome = genome
		image = Image.new("RGB", (self.width, self.height), self.white)
		self.draw = ImageDraw.Draw(image)

		self.createPositionArray()
		self.drawLines()
		self.drawCircles()
		image.save(filename)

	# creates array containing [[id, x, y, color]...] for each node
	def createPositionArray(self):
		green = (141,233,105)
		blue = (61,90,108)
		
		yGap = 100
		x = 100
		layerCount = self.getlayerCount()
		xGap = (self.width - (2*x)) / layerCount

		# create hidden layers
		self.createHiddenLayerPositions(yGap, x + xGap, xGap)

		# create input layer
		yPos = self.getYStart(len(self.genome.inputNodes), yGap)
		for node in self.genome.inputNodes:
			self.positions.append([node.id, x, yPos, green])
			yPos += yGap

		# create output layer
		yPos = self.getYStart(len(self.genome.outputNodes), yGap)
		for node in self.genome.outputNodes:
			self.positions.append([node.id, self.width-x, yPos, blue])
			yPos += yGap
	
	# creates all positions for nodes in hidden layers
	def createHiddenLayerPositions(self, yGap, x, xGap):
		grey = (190,190,190)
		prevLayer = self.genome.inputNodes
		# save the ids to make sure we don't print them multiple times
		savedIds = []
		# go until there are no more layers
		while len(prevLayer) != 0:
			# get nodes for layer
			nodeLayer = []
			for node in prevLayer:
				nodeBonds = self.getBondsFromInNode(node)
				# check if bond exists
				if nodeBonds != None:
					for b in nodeBonds:
						# get out node
						outNode = b.outNode
						# if hidden layer then add
						if outNode.type == "h" and not outNode.id in savedIds:
							nodeLayer.append(outNode)
							savedIds.append(outNode.id)

			# create positions 
			yPos = self.getYStart(len(nodeLayer), yGap)
			for node in nodeLayer:
				self.positions.append([node.id, x, yPos, grey])
				yPos += yGap
			
			# prep for next layer
			x += xGap
			prevLayer = nodeLayer.copy()

	# Counts layers and determines gap
	def getlayerCount(self):
		layerCount = 0
		prevLayer = self.genome.inputNodes

		# loop until all layers found
		savedIds = []
		while len(prevLayer) != 0:
			layerCount += 1
			nodeLayer = []
			for node in prevLayer:
				nodeBonds = self.getBondsFromInNode(node)
				# check if bond exists
				if nodeBonds != None:
					for b in nodeBonds:
						# get out node
						outNode = b.outNode
						# if hidden layer then add
						if outNode.type == "h" and not outNode.id in savedIds:
							nodeLayer.append(outNode)
							savedIds.append(outNode.id)
			prevLayer = nodeLayer.copy()
		return layerCount

	def drawLines(self):
		bonds = self.genome.bonds.copy()
		for b in bonds:
			inPos = self.getNodePosById(b.inNode.id)
			outPos = self.getNodePosById(b.outNode.id)
			weight = round(abs(b.weight*3))

			if weight == 0:
				weight = 3

			color = self.black
			if b.weight < 0:
				color = (250, 70, 88)
			if b.enabled == False:
				color = (250, 250, 250)

			if inPos == None or outPos == None:
				print("***LINE DRAWING PROBLEM***")
			else:
				self.draw.line((inPos[1], inPos[2], outPos[1], outPos[2]), width=weight, fill=color)

	def drawCircles(self):
		for n in self.genome.nodes:
			p = self.getNodePosById(n.id)
			# draw circle
			self.draw.ellipse((p[1]-self.r, p[2]-self.r, p[1]+self.r, p[2]+self.r), fill=p[3])
			
			# draw text
			nodeId = str(p[0])
			idFont = ImageFont.truetype("arial.ttf", 16)
			w, h = self.draw.textsize(nodeId, idFont)
			self.draw.text((p[1]-(w/2), p[2]-(h/2)), nodeId, font=idFont, fill=self.black)

			# draw inputs
			inputStr = str(n.inputs)
			idFont = ImageFont.truetype("arial.ttf", 16)
			w, h = self.draw.textsize(inputStr, idFont)
			h = h+70
			w = w+25
			self.draw.text((p[1]-(w/2), p[2]-(h/2)), inputStr, font=idFont, fill=self.black)

	def getYStart(self, layerSize, gap):
		totalLength = layerSize*(2*self.r) + (layerSize-1)*(gap-(2*self.r))
		return (self.height - totalLength)/2 + self.r

	def getNodePosById(self, nodeId):
		for p in self.positions:
			if p[0] == nodeId:
				return p
	
	def getBondsFromInNode(self, node):
		nodeBonds = []
		for b in self.genome.bonds:
			if b.inNode.id == node.id:
				nodeBonds.append(b)
		
		if len(nodeBonds) != 0:
			return nodeBonds
		return None