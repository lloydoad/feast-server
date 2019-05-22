from pymongo import MongoClient, DESCENDING
from os import environ

FATAL_DATABASE_NON_CONNECT = 'DATABASE CONNECTION FAIL'

mongo_url = 'FEAST_MONGO'
criticalpoint_collection_key = 'DistributionCutoffs'
adjacencylist_collection_key = 'AdjacencyList'

mongoLink = environ.get(mongo_url)
criticalpoint_collection = None
adjacencylist_collection = None

if not mongoLink == None:
  client = MongoClient(mongoLink)
  database = client.get_database()
  criticalpoint_collection = database[criticalpoint_collection_key]
  adjacencylist_collection = database[adjacencylist_collection_key]

def get_recentlist():
  if adjacencylist_collection == None:
    print(FATAL_DATABASE_NON_CONNECT)
    return None
  
  return adjacencylist_collection.find_one({}, sort=[( '_id', DESCENDING )])

def get_recentpoints():
  if criticalpoint_collection == None:
    print(FATAL_DATABASE_NON_CONNECT)
    return None
  
  return criticalpoint_collection.find_one({}, sort=[( '_id', DESCENDING )])
