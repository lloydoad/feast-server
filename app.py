from modules.classifier_request import get_initial_classifiers, get_subsequent_classifier, fill_database
from flask import Flask, request, Response, json, jsonify
from modules.data_generator import generate_source_files
from modules.search import find_restaurants

app = Flask(__name__)
app.config['DEBUG'] = True

# 3 routes
# setup? user_preference:list => set(list)
# addon? classifier:string
# get_restaurants? classifiers:list, latitude, longitude

if __name__ == '__main__':
  print(find_restaurants(tags=['italian','pizza'], latitude=28.595050, longitude=-81.220470))
  # print(get_initial_classifiers(user_preference={'Cuban', 'South African'}))
  # print(get_subsequent_classifier(leading_classifier='Pizza'))

  # print(generate_source_files())