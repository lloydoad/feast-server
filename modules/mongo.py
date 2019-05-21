from pymongo import MongoClient, DESCENDING
from os import environ

FATAL_DATABASE_NON_CONNECT = 'DATABASE CONNECTION FAIL'

mongoURI = 'FEAST_MONGO'
criticalPointCollectionKey = 'DistributionCutoffs'
adjacencyListCollectionKey = 'AdjacencyList'

mongoLink = environ.get(mongoURI)
criticalPointCollection = None
adjacencyListCollection = None

if not mongoLink == None:
  client = MongoClient(mongoLink)
  database = client.get_database()
  criticalPointCollection = database[criticalPointCollectionKey]
  adjacencyListCollection = database[adjacencyListCollectionKey]

def getRecentList():
  if adjacencyListCollection == None:
    print(FATAL_DATABASE_NON_CONNECT)
    return None
  
  return adjacencyListCollection.find_one({}, sort=[( '_id', DESCENDING )])

def getRecentPoints():
  if criticalPointCollection == None:
    print(FATAL_DATABASE_NON_CONNECT)
    return None
  
  return criticalPointCollection.find_one({}, sort=[( '_id', DESCENDING )])
