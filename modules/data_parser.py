import json

CATEGORY_KEY = 'categories'
FOOD_KEY = 'Food'
RESTAURANTS_KEY = 'Restaurants'

POPULARITY_KEY = 'popularity'
ADJACENTS_KEY = 'adjacents'
ADJACENTS_LENGTH_KEY = 'adjacentsLength'

def getIgnoreKeySet(ignoreKeySetFile):
  ignoreKeySet = []

  with open(ignoreKeySetFile) as ignoreKeySetData:
    for line in ignoreKeySetData:
      ignoreKeySet.append(line.strip())
  
  return ignoreKeySet

def addParent(tag, adjacencyList, ignoreKeySet):
  if tag in ignoreKeySet:
    return

  if tag in adjacencyList:
    adjacencyList[tag][POPULARITY_KEY] += 0.2
  else:
    adjacencyList[tag] = {
      POPULARITY_KEY: 0.12,
      ADJACENTS_KEY: [],
      ADJACENTS_LENGTH_KEY: 0
    }

def addChild(parentTag, childTag, adjacencyList, ignoreKeySet):
  if parentTag in adjacencyList and childTag not in ignoreKeySet:
    if childTag not in adjacencyList[parentTag][ADJACENTS_KEY]:
      adjacencyList[parentTag][ADJACENTS_KEY].append(childTag)
      adjacencyList[parentTag][ADJACENTS_LENGTH_KEY] += 1

def addListToAdjacencyList(listInput, adjacencyList, ignoreKeySet):
  length = len(listInput)

  for i in range(0, length):
    for j in range(i + 1, length):
      parentTag = listInput[i]
      childTag = listInput[j]

      addParent(parentTag, adjacencyList, ignoreKeySet)
      addParent(childTag, adjacencyList, ignoreKeySet)

      addChild(parentTag, childTag, adjacencyList, ignoreKeySet)
      addChild(childTag, parentTag, adjacencyList, ignoreKeySet)

def getAdjacencyList(businessInfoFile, ignoreKeySetFile):
  ignoreKeySet = getIgnoreKeySet(ignoreKeySetFile)
  adjacencyList = {}
  
  with open(businessInfoFile) as businessInfoFileData:
    for line in businessInfoFileData:
      dataLine = json.loads(line)
      categories = dataLine.get(CATEGORY_KEY)

      if categories is None:
        continue
      
      if RESTAURANTS_KEY in categories and FOOD_KEY in categories:
        restaurantClassifiers = [classifier.strip() for classifier in str(categories).split(',')]
        addListToAdjacencyList(restaurantClassifiers, adjacencyList, ignoreKeySet)

  return adjacencyList

