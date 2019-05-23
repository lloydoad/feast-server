from json import load
from os import environ
from string import Template
import requests

KEY_STATUS = 'status'
KEY_QUERY = 'query'
KEY_DATA = 'data'
KEY_SEARCH = 'search'
KEY_BUSINESS = 'business'
KEY_YELP_TOKEN = 'YELP_API_KEY'

# Response Keys
KEY_DATA = 'data'
KEY_CODE = 'status'
KEY_MESSAGE = 'response_text'

YELP_TOKEN = environ.get(KEY_YELP_TOKEN)
YELP_GRAPH_FILE_PATH = './files/yelp_graphql.json'
YELP_URL = 'https://api.yelp.com/v3/graphql'
YELP_LIMIT = 8

CODE_ERROR = 404

ERROR_QUERY = 'Invalid Query'
ERROR_LOADING = 'Invalid GraphQL File'
ERROR_GENERAL = 'API Error'
ERROR_MISSING_TOKEN = 'Missing Token'

def response( data=[], response_code=200, response_text='SUCCESS'):
  return {
    KEY_CODE: response_code,
    KEY_MESSAGE: response_text,
    KEY_DATA: data
  }

def find_restaurants( tags=[], latitude=0, longitude=0):
  """
  :param tags: String list of classifiers
  :param latitude: float
  :param longitude: float
  :return: list of eligible restaurants
  """
  retval = []
  
  if tags is None or latitude is None or longitude is None:
    return response(response_code=CODE_ERROR, response_text=ERROR_QUERY)
  elif not isinstance(tags, list):
    return response(response_code=CODE_ERROR, response_text=ERROR_QUERY)
  elif not (isinstance(latitude, float) and isinstance(longitude, float)):
    return response(response_code=CODE_ERROR, response_text=ERROR_QUERY)
  elif len(tags) == 0:
    return response(response_code=CODE_ERROR, response_text=ERROR_QUERY)
  elif YELP_TOKEN is None:
    return response(response_code=CODE_ERROR, response_text=ERROR_MISSING_TOKEN)

  with open(YELP_GRAPH_FILE_PATH) as yelp_graph_file:
    yelp_graph_data = load(yelp_graph_file)
    query = Template(yelp_graph_data[KEY_QUERY])

    headers = { 'Authorization': ('Bearer %s' % YELP_TOKEN)}
    categories = ','.join(tags)

    query = { KEY_QUERY: query.substitute( lat=latitude, lon=longitude, cat=categories, limit=YELP_LIMIT) }
    
    results = requests.post( url=YELP_URL, json=query, headers=headers )

    if not results.status_code == 200:
      print(results.json())
      return response(response_code=CODE_ERROR, response_text=ERROR_GENERAL)
    
    businesses = results.json().get(KEY_DATA).get(KEY_SEARCH).get(KEY_BUSINESS)
    for business in businesses:
      retval.append(business)

    return response(data=retval)
  
  return response(response_code=CODE_ERROR, response_text=ERROR_LOADING)
  
