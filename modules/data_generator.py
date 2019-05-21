from modules.mongo import criticalPointCollectionKey, adjacencyListCollectionKey
from modules.csv_converter import writeToCSV
from modules.data_parser import getAdjacencyList
from modules.classifier import populateCVS
from pymongo import MongoClient
from os import environ

businessFilePath = './files/business.json'
ignoreFilePath = './files/ignore.txt'
mongoURI = 'FEAST_MONGO'

LIST_KEY = 'list'
CUTOFFS_KEY = 'cutoffs'

def generateSourceFiles(businessFilePath=businessFilePath,ignoreFilePath=ignoreFilePath):
  mongoLink = environ.get(mongoURI)

  if mongoLink == None:
    print('FATAL ERROR: DATABASE NOT SET')
    return None

  client = MongoClient(mongoLink)
  database = client.get_database()
  criticalPointCollection = database[criticalPointCollectionKey]
  adjacencyListCollection = database[adjacencyListCollectionKey]

  adjacencyList = getAdjacencyList(businessFilePath, ignoreFilePath)
  csvFile = writeToCSV(adjacencyList)
  cutoffs = populateCVS()

  adjacencyListCollection.insert_one(adjacencyList)
  criticalPointCollection.insert_one(cutoffs)

  return {
    LIST_KEY: adjacencyList,
    CUTOFFS_KEY: cutoffs
  }
