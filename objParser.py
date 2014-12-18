objFile = open('pear.obj', 'r')
finalTexture = open('finalTexture.txt', 'w')
finalVertex = open('finalVertex.txt', 'w')


vertexList = []
textureList = []

finalVertexList = []
finalTextureList = []

for line in objFile:
	split = line.split()
	#if blank line, skip
	if not len(split):
		continue
	if split[0] == "v":
		vertexList.append(split[1:])
	elif split[0] == "vt":
		textureList.append(split[1:])
	elif split[0] == "f":
		count=1
		firstSet=[]
		secondSet=[]
		firstTextureSet=[]
		secondTextureSet = []
		while count<5:
			removeSlash = split[count].split('/')
			if count == 1:
				firstSet.append(vertexList[int(removeSlash[0])-1])
				secondSet.append(vertexList[int(removeSlash[0])-1])
				firstTextureSet.append(textureList[int(removeSlash[1])-1])
				secondTextureSet.append(textureList[int(removeSlash[1])-1])
			elif count == 2:
				firstSet.append(vertexList[int(removeSlash[0])-1])
				firstTextureSet.append(textureList[int(removeSlash[1])-1])
			elif count == 3:
				firstSet.append(vertexList[int(removeSlash[0])-1])
				secondSet.append(vertexList[int(removeSlash[0])-1])
				firstTextureSet.append(textureList[int(removeSlash[1])-1])
				secondTextureSet.append(textureList[int(removeSlash[1])-1])
			elif count == 4:
				secondSet.append(vertexList[int(removeSlash[0])-1])
				secondTextureSet.append(textureList[int(removeSlash[1])-1])

			count+=1
		finalVertexList.append(firstSet)
		finalVertexList.append(secondSet)
		finalTextureList.append(firstTextureSet)
		finalTextureList.append(secondTextureSet)



vertexCount = 0
for item in finalVertexList:
	for cordinateTrio in item:
		for cordinate in cordinateTrio:
			finalVertex.write(str(cordinate)+'f*x, ')
	vertexCount += 1

textureCount = 0
for item in finalTextureList:
	for cordinateTrio in item:
		for cordinate in cordinateTrio:
			finalTexture.write(str(cordinate)+'f, ')
	textureCount += 1

print ("Total vertices: " + str(vertexCount*3))
print ("Total texture cordinates: " + str(vertexCount*2))

objFile.close()
finalTexture.close()
finalVertex.close()