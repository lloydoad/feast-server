from modules.mongo import criticalpoint_collection_key, adjacencylist_collection_key
from modules.csv_converter import writeToCSV
from modules.data_parser import get_adjacencylist
from modules.classifier import populateCVS
from pymongo import MongoClient
from os import environ

LIST_KEY = 'list'
CUTOFFS_KEY = 'cutoffs'

business_filepath = './files/business.json'
ignore_filepath = './files/ignore.txt'
mongoURI = 'FEAST_MONGO'

def generate_source_files(business_filepath=business_filepath, ignore_filepath=ignore_filepath):
  mongoLink = environ.get(mongoURI)

  if mongoLink is None:
    print('FATAL ERROR: DATABASE NOT SET')
    return None
  
  if business_filepath is None or ignore_filepath is None:
    print('FATAL ERROR: FILEPATHS ARE INVALID')
    return None

  client = MongoClient(mongoLink)
  database = client.get_database()
  criticalpoint_collection = database[criticalpoint_collection_key]
  adjacencylist_collection = database[adjacencylist_collection_key]

  adjacencylist = get_adjacencylist(business_filepath, ignore_filepath)
  csv_file = writeToCSV(adjacencylist)
  cutoffs = populateCVS()

  adjacencylist_collection.insert_one(adjacencylist)
  criticalpoint_collection.insert_one(cutoffs)

  return {
    LIST_KEY: adjacencylist,
    CUTOFFS_KEY: cutoffs
  }
