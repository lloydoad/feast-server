from modules.classifier_request import get_initial_classifiers, get_subsequent_classifier, fill_database
from modules.search import find_restaurants, KEY_DATA, KEY_CODE, KEY_MESSAGE, ERROR_QUERY, CODE_ERROR
from flask import Flask, request, Response, json, jsonify
from modules.data_generator import generate_source_files
import airbrake

app = Flask(__name__)
logger = airbrake.getLogger()
app.config['DEBUG'] = True

ROUTE_INDEX = '/'
ROUTE_SETUP = '/setup'
ROUTE_ADDON = '/addon'
ROUTE_RESTAURANTS = '/restaurants'

METHOD_GET = 'GET'

KEY_CLASSIFIERS = 'classifiers'
KEY_CLASSIFIERS_ALT = 'classifiers[]'
KEY_LATITUDE = 'latitude'
KEY_LONGITUDE = 'longitude'

CODE_SUCCESS = 200

def getJsonResponse(code=CODE_SUCCESS, message=ERROR_QUERY):
  response = jsonify(message)
  response.status_code = code
  return response

def send_response(responseObj):
  if responseObj[KEY_CODE] == CODE_SUCCESS:
    return getJsonResponse(message=responseObj[KEY_DATA])
  else:
    return getJsonResponse(code=CODE_ERROR, message=responseObj[KEY_MESSAGE])

def get_classifiers():
  attempt = request.args.getlist(KEY_CLASSIFIERS)

  if(attempt is None or not isinstance(attempt, list) or len(attempt) == 0):
    attempt = request.args.getlist(KEY_CLASSIFIERS_ALT)
  
  if(attempt is None or not isinstance(attempt, list) or len(attempt) == 0):
    return None

  print(attempt)
  
  return attempt

@app.route(ROUTE_INDEX, methods=[METHOD_GET])
def index():
  return 'Feast Server Live'

@app.route(ROUTE_SETUP, methods=[METHOD_GET])
def get_initial_classifier():
  classifiers = get_classifiers()
  # request.args.getlist(KEY_CLASSIFIERS)

  if(
    classifiers is None or 
    not isinstance(classifiers, list)
  ):
    return getJsonResponse(code=CODE_ERROR)

  user_preference = set()
  for classifier in classifiers:
    user_preference.add(classifier)

  results = get_initial_classifiers(user_preference=user_preference)
  return send_response(results)

@app.route(ROUTE_ADDON, methods=[METHOD_GET])
def get_following_classifier():
  classifiers = get_classifiers()
  # request.args.getlist(KEY_CLASSIFIERS)

  if(classifiers is None):
    return getJsonResponse(code=CODE_ERROR)

  initial_classifier = str(classifiers[0]).lower().capitalize()
  results = get_subsequent_classifier(leading_classifier=initial_classifier)
  return send_response(results)

@app.route(ROUTE_RESTAURANTS, methods=[METHOD_GET])
def get_restaurants():
  classifiers = get_classifiers()
  #  request.args.getlist(KEY_CLASSIFIERS)
  longitude = request.args.get(KEY_LONGITUDE)
  latitude = request.args.get(KEY_LATITUDE)

  if(
    classifiers is None or 
    longitude is None or
    latitude is None or
    not isinstance(classifiers, list) or
    len(classifiers) == 0
  ):
    return getJsonResponse(code=CODE_ERROR)

  try:
    latitude = float(latitude)
    longitude = float(longitude)
  except ValueError:
    return getJsonResponse(code=CODE_ERROR)
  tags = [val.lower() for val in classifiers]

  results = find_restaurants(tags=tags, latitude=latitude, longitude=longitude)
  return send_response(results)

if __name__ == '__main__':
  logger.error('Airbrake monitoring initialized')
  app.run()