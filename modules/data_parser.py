import json

CATEGORY_KEY = 'categories'
FOOD_KEY = 'Food'
RESTAURANTS_KEY = 'Restaurants'
POPULARITY_KEY = 'popularity'
ADJACENTS_KEY = 'adjacents'
ADJACENTS_LENGTH_KEY = 'adjacentsLength'

def get_ignore_keyset(ignore_keyset_file):
  ignore_keyset = []

  with open(ignore_keyset_file) as ignore_keyset_data:
    for line in ignore_keyset_data:
      ignore_keyset.append(line.strip())
  
  return ignore_keyset

def add_parent(tag, adjacencylist, ignore_keyset):
  if tag in ignore_keyset:
    return

  if tag in adjacencylist:
    adjacencylist[tag][POPULARITY_KEY] += 0.2
  else:
    adjacencylist[tag] = {
      POPULARITY_KEY: 0.12,
      ADJACENTS_KEY: [],
      ADJACENTS_LENGTH_KEY: 0
    }

def add_child(parent_tag, child_tag, adjacencylist, ignore_keyset):
  if parent_tag in adjacencylist and child_tag not in ignore_keyset:
    if child_tag not in adjacencylist[parent_tag][ADJACENTS_KEY]:
      adjacencylist[parent_tag][ADJACENTS_KEY].append(child_tag)
      adjacencylist[parent_tag][ADJACENTS_LENGTH_KEY] += 1

def add_list_to_adjacencylist(list_input, adjacencylist, ignore_keyset):
  length = len(list_input)

  for i in range(0, length):
    for j in range(i + 1, length):
      parentTag = list_input[i]
      childTag = list_input[j]

      add_parent(parentTag, adjacencylist, ignore_keyset)
      add_parent(childTag, adjacencylist, ignore_keyset)

      add_child(parentTag, childTag, adjacencylist, ignore_keyset)
      add_child(childTag, parentTag, adjacencylist, ignore_keyset)

def get_adjacencylist(business_info_file, ignore_keyset_file):
  ignore_keyset = get_ignore_keyset(ignore_keyset_file)
  adjacencylist = {}
  
  with open(business_info_file) as business_info_Data:
    for line in business_info_Data:
      data_line = json.loads(line)
      categories = data_line.get(CATEGORY_KEY)

      if categories is None:
        continue
      
      if RESTAURANTS_KEY in categories and FOOD_KEY in categories:
        restaurant_classifiers = [classifier.strip() for classifier in str(categories).split(',')]
        add_list_to_adjacencylist(restaurant_classifiers, adjacencylist, ignore_keyset)

  return adjacencylist

