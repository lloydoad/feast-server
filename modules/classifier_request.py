from modules.data_generator import generate_source_files, business_filepath, ignore_filepath
from modules.classifier import LOWER_CUTOFF_KEY, UPPER_CUTOFF_KEY
from modules.data_parser import POPULARITY_KEY, ADJACENTS_KEY
from modules.mongo import getRecentList, getRecentPoints
from modules.csv_converter import KEY_INDEX
from random import randint, sample

ID_KEY = '_id'

def fill_database(classifiers=business_filepath, ignored_classifiers=ignore_filepath):
  if classifiers is None or ignored_classifiers is None:
    return generate_source_files()
  else:
    return generate_source_files(business_filepath=classifiers, ignore_filepath=ignored_classifiers)

def sort_classifiers(adjacency_list=None):
  if adjacency_list is None:
    return adjacency_list

  if ID_KEY in adjacency_list:
    del adjacency_list[ID_KEY]
  
  return sorted(adjacency_list.items(), key=lambda item: item[1][KEY_INDEX])

def get_classifier(adjacent_list=None, last_index=-1, start=0, end=0, previous_list=None):
  if adjacent_list is None or last_index == -1 or previous_list is None or not type(previous_list) == list:
    return None

  random_classifier = adjacent_list[randint(start, end)][0]
  while random_classifier in previous_list:
    random_classifier = adjacent_list[randint(start, end)][0]

  return random_classifier

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
  adjacency_list = getRecentList()
  cutoff_points = getRecentPoints()
  retval = []

  if adjacency_list is None or cutoff_points is None:
    return retval

  adjacency_list = attach_user_preference(default_list=adjacency_list, user_preference=user_preference)
  sorted_adjacency_list = sort_classifiers(adjacency_list=adjacency_list)

  upper_cutoff = cutoff_points[UPPER_CUTOFF_KEY]
  lower_cutoff = cutoff_points[LOWER_CUTOFF_KEY]
  last_index = len(sorted_adjacency_list) - 1
  iteration = [
    (0, lower_cutoff),
    ((lower_cutoff + 1), upper_cutoff),
    ((lower_cutoff + 1), upper_cutoff),
    ((lower_cutoff + 1), upper_cutoff),
    ((upper_cutoff + 1), last_index),
    ((upper_cutoff + 1), last_index)
  ]

  for passes in range(5):
    result = []
    for start,end in iteration:
      result.append(
        get_classifier(
          adjacent_list=sorted_adjacency_list,
          last_index=last_index,
          start=start,
          end=end,
          previous_list=result
        )
      )
    retval.append(result)

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
  adjacency_list = getRecentList()
  cutoff_points = getRecentPoints()
  retval = []

  if adjacency_list is None or cutoff_points is None:
    return retval
  if leading_classifier is None or leading_classifier not in adjacency_list:
    return retval

  subsequent_classifiers_list = [adjacent for adjacent in adjacency_list[leading_classifier][ADJACENTS_KEY]]
  length = len(subsequent_classifiers_list)
  list_start = cutoff_points[UPPER_CUTOFF_KEY]
  list_end = len(adjacency_list) - 2

  if length <= 10:
    return get_fallback_classifiers(
      available_classifiers=subsequent_classifiers_list, adjacency_list=adjacency_list,
      start=list_start, end=list_end
    )

  local_upper_cutoff = int((cutoff_points[UPPER_CUTOFF_KEY] / (list_end + 1)) * length)
  local_lower_cutoff = int((cutoff_points[LOWER_CUTOFF_KEY] / (list_end + 1)) * length)

  if (
    local_lower_cutoff - 0 < 1 or
    local_upper_cutoff - local_lower_cutoff < 3 or
    list_end - local_upper_cutoff < 2
  ):
    return get_fallback_classifiers(
      available_classifiers=subsequent_classifiers_list, adjacency_list=adjacency_list,
      start=list_start, end=list_end
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