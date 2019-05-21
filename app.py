from modules.classifier_request import get_initial_classifiers, get_subsequent_classifier, fill_database

# TODO
'''
    Final round, <- points
      send back user preference info
      get restaurants based on tags,
      prioritize one with reviews 
      -> restaurants
'''

if __name__ == '__main__':
  print(get_initial_classifiers(user_preference={'Cuban', 'South African'}))
  print(get_subsequent_classifier(leading_classifier='Churros'))