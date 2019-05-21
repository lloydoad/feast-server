from modules.data_parser import ADJACENTS_KEY, ADJACENTS_LENGTH_KEY, POPULARITY_KEY
import csv

savePath = './files/classifier.csv'
TITLE_INDEX = 'Index'
TITLE_CLASSIFIER = 'Classifier'
TITLE_POPULARITY = 'Popularity'
TITLE_ADJACENTS = 'Adjacents'
KEY_INDEX = 'index'

def writeToCSV(adjacencyListInput):
  sortedAdjacencyList = sorted(adjacencyListInput.items(), key=lambda row: row[1][ADJACENTS_LENGTH_KEY])
  index = 0

  with open(savePath, mode='w') as classifierInfoFile:
    classifier_writer = csv.writer(classifierInfoFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    classifier_writer.writerow(['Index', 'Classifier', 'Popularity', 'Adjacents'])
    for key,value in sortedAdjacencyList:
      classifier_writer.writerow([index, key, value[POPULARITY_KEY], value[ADJACENTS_LENGTH_KEY]])
      adjacencyListInput[key][KEY_INDEX] = index
      index += 1

    return classifierInfoFile
  return None