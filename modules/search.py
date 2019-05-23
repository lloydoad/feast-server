from os import environ
from string import Template
import requests

KEY_STATUS = 'status'
KEY_DATA = 'data'
KEY_SEARCH = 'search'
KEY_BUSINESS = 'business'
KEY_YELP_TOKEN = 'YELP_API_KEY'

YELP_TOKEN = environ.get(KEY_YELP_TOKEN)
YELP_URL = ''

def find_restaurants(tags=[], latitude=0, longitude=0):
  """
  :param tags: String list of classifiers
  :param latitude: float
  :param longitude: float
  :return: list of eligible restaurants
  """
  retval = []
  
  if tags is None or latitude is None or longitude is None:
    return retval
  elif not isinstance(tags, list):
    return retval
  elif not (isinstance(latitude, float) and isinstance(longitude, float)):
    return retval
  elif len(tags) == 0:
    return retval
  elif YELP_TOKEN is None:
    return retval

  headers = { 'Authorization': ('Bearer %s' % YELP_TOKEN)}
  url = 'https://api.yelp.com/v3/graphql'
  categories = ','.join(tags)
  queryTemplate = Template(
  '''
  {
    search(latitude: $lat, longitude: $lon, radius: 40000, categories: "$cat", limit: 8) 
    { 
      business 
      { 
        name 
        rating 
        price
        review_count 
        hours 
        { 
          is_open_now open 
          { 
            start 
            end 
          } 
        } 
        reviews 
        { 
          text 
          rating 
          url 
        } 
        location 
        { 
          address1 
          city 
          state 
          country 
        } 
      } 
    }
  }
  '''
  ) 
  query = { 'query': queryTemplate.substitute( lat=latitude, lon=longitude, cat=categories) }
  results = requests.post( url=url, json=query, headers=headers )

  if not results.status_code == 200:
    return retval
  
  businesses = results.json().get(KEY_DATA).get(KEY_SEARCH).get(KEY_BUSINESS)
  for business in businesses:
    retval.append(business)
  
  return retval
  
