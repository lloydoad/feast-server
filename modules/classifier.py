from modules.data_parser import ADJACENTS_LENGTH_KEY
from modules.csv_converter import savePath, TITLE_ADJACENTS, TITLE_INDEX
import pandas, math, functools, operator

TITLE_DISTRIBUTION = 'Distribution'
TITLE_JUMP = 'Jump'

LOWER_CUTOFF_KEY = 'lowerCutoff'
UPPER_CUTOFF_KEY = 'upperCutoff'

LOWER_SPREAD = 0.2
MIDDLE_SPREAD = 0.675
TOP_SPREAD = 12.5

FIRST_CUTOFF = 0.000101
SECOND_CUTOFF = 0.00035

# Just copied from stack overflow :)
def normpdf(x, mean, sd):
  var = float(sd)**2
  denom = (2*math.pi*var)**.5
  num = math.exp(-(float(x)-float(mean))**2/(2*var))
  return num/denom

def calculateDistribution(sheet, mean, standardDev):
  for indx,row in sheet.iterrows():
    adjacent = row.get(TITLE_ADJACENTS)
    distribution = normpdf(adjacent, mean, standardDev)
    sheet.at[indx, TITLE_DISTRIBUTION] = distribution

def calculateJumps(sheet, count):
  for indx,row in sheet.iterrows():
    if indx == count:
      sheet.at[indx, TITLE_JUMP] = 1
    else:
      topDist = row.get(TITLE_DISTRIBUTION)
      bottomDist = sheet.iloc[indx + 1].get(TITLE_DISTRIBUTION)
      sheet.at[indx, TITLE_JUMP] = abs(bottomDist - topDist)

def getRealCutoff(sheet, start, end, cutoff):
  results = []
  first_indx = 0
  firstValue = 0
  isFirstSet = False

  for index in range(int(start), int(end) + 1):
    row = sheet.iloc[index]
    jump = row.get(TITLE_JUMP)

    if jump >= cutoff:
      results.append(index * index * jump)
      if not isFirstSet:
        isFirstSet = True
        first_indx = index
        firstValue = index * index * jump

  count = len(results)
  if count == 0:
    return end

  total = functools.reduce(operator.add,results)
  mean = total / count
  return (first_indx * mean) / firstValue

def populateCVS():
  sheet = pandas.read_csv(savePath)
  
  # Calculate distributions
  mean = sheet[TITLE_ADJACENTS].mean()
  standardDev = sheet[TITLE_ADJACENTS].std()
  calculateDistribution(sheet, mean, standardDev)

  # GET Groupings
  count = sheet.count().get(TITLE_INDEX)
  lowerGroupExpectedEnd = round(LOWER_SPREAD * count) 
  middleGroupExpectedEnd = round(MIDDLE_SPREAD * count) + lowerGroupExpectedEnd

  # Calculate Jumps
  calculateJumps(sheet, count - 1)

  # Get significant jumps
  lowerCutoff = getRealCutoff(sheet, 0, lowerGroupExpectedEnd, FIRST_CUTOFF)
  upperCutoff = getRealCutoff(sheet, lowerGroupExpectedEnd + 1, middleGroupExpectedEnd, SECOND_CUTOFF)
  
  # Save to disk
  sheet.to_csv(savePath)

  return {
    UPPER_CUTOFF_KEY: round(upperCutoff),
    LOWER_CUTOFF_KEY: round(lowerCutoff)
  }
