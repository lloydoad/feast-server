from modules.classifier_request import get_initial_classifiers, get_subsequent_classifier, fill_database
from modules.search import find_restaurants, KEY_DATA, KEY_CODE, KEY_MESSAGE, ERROR_QUERY, CODE_ERROR
from flask import Flask, request, Response, json, jsonify
from modules.data_generator import generate_source_files

app = Flask(__name__)
app.config['DEBUG'] = True

ROUTE_SETUP = '/setup'
ROUTE_ADDON = '/addon'
ROUTE_RESTAURANTS = '/restaurants'

METHOD_GET = 'GET'

KEY_CLASSIFIERS = 'classifiers'
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

@app.route(ROUTE_SETUP, methods=[METHOD_GET])
def get_initial_classifier():
  classifiers = request.args.get(KEY_CLASSIFIERS)

  if(
    classifiers is None or 
    not isinstance(classifiers, list) or
    len(classifiers) == 0
  ):
    return getJsonResponse(code=CODE_ERROR)

  user_preference = set()
  for classifier in classifiers:
    user_preference.add(classifier)

  results = get_initial_classifiers(user_preference=user_preference)
  return send_response(results)

@app.route(ROUTE_ADDON, methods=[METHOD_GET])
def get_subsequent_classifier():
  classifiers = request.args.get(KEY_CLASSIFIERS)

  if(
    classifiers is None or 
    not isinstance(classifiers, list) or
    len(classifiers) == 0
  ):
    return getJsonResponse(code=CODE_ERROR)

  results = get_subsequent_classifier(leading_classifier=classifiers[0])
  return send_response(results)

@app.route(ROUTE_RESTAURANTS, methods=[METHOD_GET])
def get_restaurants():
  classifiers = request.args.get(KEY_CLASSIFIERS)
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

  results = find_restaurants(tags=classifiers, latitude=latitude, longitude=longitude)
  return send_response(results)

if __name__ == '__main__':
  app.run()