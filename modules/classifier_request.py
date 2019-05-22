from modules.data_generator import generate_source_files, business_filepath, ignore_filepath
from modules.classifier import LOWER_CUTOFF_KEY, UPPER_CUTOFF_KEY
from modules.data_parser import POPULARITY_KEY, ADJACENTS_KEY
from modules.mongo import get_recentlist, get_recentpoints
from modules.csv_converter import KEY_INDEX
from random import randint, sample

ID_KEY = '_id'

def fill_database(classifiers=business_filepath, ignored_classifiers=ignore_filepath):
  if classifiers is None or ignored_classifiers is None:
    return generate_source_files()
  else:
    return generate_source_files(business_filepath=classifiers, ignore_filepath=ignored_classifiers)

def attach_user_preference(default_list=None, user_preference=None):
  if default_list is None or user_preference is None:
    return default_list
  elif len(default_list) == 0 or len(user_preference) == 0:
    return default_list

  new_adjacency_list = {}
  index = 0

  for key in default_list:
    if key not in user_preference and not key == ID_KEY:
      new_adjacency_list[key] = default_list[key]
      new_adjacency_list[key][KEY_INDEX] = index
      index += 1

  for key in user_preference:
    if key in default_list:
      new_adjacency_list[key] = default_list[key]
      new_adjacency_list[key][KEY_INDEX] = index
      index += 1

  return new_adjacency_list

def get_initial_classifiers(user_preference=None):
  """
  :param user_preference: list of user preference and popularity to adjacency list, eg ['churros','pizza']
  :return: List of 5 sets
  """
  adjacency_list = get_recentlist()
  cutoff_points = get_recentpoints()
  choice_list_count = 5
  retval = []

  if adjacency_list is None or cutoff_points is None:
    return retval

  adjacency_list = attach_user_preference(default_list=adjacency_list, user_preference=user_preference)

  index_sorted_adjacencylist = {}
  last_index = 0
  for key,value in adjacency_list.items():
    index_sorted_adjacencylist[value[KEY_INDEX]] = key
    last_index = max(last_index, value[KEY_INDEX])

  upper_cutoff = cutoff_points[UPPER_CUTOFF_KEY]
  lower_cutoff = cutoff_points[LOWER_CUTOFF_KEY]
  iteration = [
    (0, lower_cutoff),
    ((lower_cutoff + 1), upper_cutoff),
    ((lower_cutoff + 1), upper_cutoff),
    ((lower_cutoff + 1), upper_cutoff),
    ((upper_cutoff + 1), last_index),
    ((upper_cutoff + 1), last_index)
  ]

  for passes in range(choice_list_count):
    choices = []
    infinite_loop_sentinel = 1000

    for start, end in iteration:
      choice = index_sorted_adjacencylist[randint(start, end)]

      while choice in choices:
        infinite_loop_sentinel -= 1
        choice = index_sorted_adjacencylist[randint(start, end)]
        if infinite_loop_sentinel <= 0:
          print('FATAL ERROR: CSV FILE CURRUPTED')
          return retval
      
      choices.append(choice)
    
    retval.append(choices)

  return retval

def get_fallback_classifiers(available_classifiers=None, adjacency_list=None, start=0, end=0):
  """
  :param available_classifiers: String list of adjacenst
  :param adjacency_list: Passed down adjacency list
  :param start: Start of cutoff
  :param end: End of cutoff
  :return: subsequent classifier list
  """
  if available_classifiers is None or adjacency_list is None or start == 0 or end == 0:
    return available_classifiers

  desired_length = 6
  length = len(available_classifiers)

  if length >= desired_length:
    return sample(available_classifiers, k=desired_length)

  new_classifiers = available_classifiers
  remaining_amount = desired_length - length
  sample_indices = sample(range(int(start), int(end)), k=remaining_amount)

  for key,value in adjacency_list.items():
    if not key == ID_KEY and value[KEY_INDEX] in sample_indices:
      new_classifiers.append(key)

  return new_classifiers

def get_subsequent_classifier(leading_classifier=None):
  """
  :param leading_classifier: string, eg 'churros'
  :return: one set
  """
  adjacency_list = get_recentlist()
  cutoff_points = get_recentpoints()
  retval = []

  if adjacency_list is None or cutoff_points is None:
    return retval
  if leading_classifier is None or leading_classifier not in adjacency_list:
    return retval

  subsequent_classifiers_list = [adjacent for adjacent in adjacency_list[leading_classifier][ADJACENTS_KEY]]
  length = len(subsequent_classifiers_list)
  absolute_upper_cutoff = len(adjacency_list) - 2
  absolute_lower_cutoff = cutoff_points[UPPER_CUTOFF_KEY]
  local_upper_cutoff = int((cutoff_points[UPPER_CUTOFF_KEY] / (absolute_upper_cutoff + 1)) * length)
  local_lower_cutoff = int((cutoff_points[LOWER_CUTOFF_KEY] / (absolute_upper_cutoff + 1)) * length)

  if (
    length <= 10 or
    local_lower_cutoff - 0 < 1 or
    local_upper_cutoff - local_lower_cutoff < 3 or
    absolute_upper_cutoff - local_upper_cutoff < 2
  ):
    return get_fallback_classifiers(
      available_classifiers=subsequent_classifiers_list, adjacency_list=adjacency_list,
      start=absolute_lower_cutoff, end=absolute_upper_cutoff
    )

  subsequent_classifiers_dict = {}
  for key in subsequent_classifiers_list:
    subsequent_classifiers_dict[key] = adjacency_list[key][POPULARITY_KEY]
  subsequent_classifiers_dict = sorted(subsequent_classifiers_dict.items(), key=lambda item: item[1])
  subsequent_classifiers_list = [adjacent_tuple[0] for adjacent_tuple in subsequent_classifiers_dict]

  samples = [index for index in sample(range(0,local_lower_cutoff), k=1)]
  samples += [index for index in sample(range(local_lower_cutoff,local_upper_cutoff), k=3)]
  samples += [index for index in sample(range(local_upper_cutoff, length), k=2)]
  for index in samples:
    retval.append(subsequent_classifiers_list[index])

  return retval