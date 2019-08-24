
const adjacencyList = require('../files/AdjacencyList.json');

const getRandom = (min, max) => {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

const sortAdjacencyList = (adjacencyList, sortedList) => {

  let lastIndex = 0;

  for (let [key, value] of Object.entries(adjacencyList)) {
    sortedList[value.index] = key;
    lastIndex = Math.max(lastIndex, value.index);
  }

  return lastIndex;
}

const getSections = (lowerCutoff, upperCutoff, lastIndex) => {
  return [
    [0, lowerCutoff],
    [lowerCutoff + 1, upperCutoff],
    [lowerCutoff + 1, upperCutoff],
    [lowerCutoff + 1, upperCutoff],
    [upperCutoff + 1, lastIndex],
    [upperCutoff + 1, lastIndex]
  ];
}

const attachPreference = (defaultList = {}, preference = []) => {
  
  if(preference.length == 0 || defaultList.length == 0)
    return defaultList;

  let result = {};
  let index = 0;
  let ref = [];

  for(let [key, value] of Object.entries(defaultList)) {
    ref.push(value);
    if(!(preference.includes(value)))
      result[index++] = value;
  }

  for(key in preference)
    if(ref.includes(preference[key]))
      result[index++] = preference[key];

  return result;
}

const getSampleInRange = (start, end, source, count) => {
  let indices = [];

  for(let a = 0; a < count; a++) {
    let pick = getRandom(start, end);
    while(indices.includes(pick))
      pick = getRandom(start, end);
    indices.push(pick);
  }
  
  return indices.map( pos => {
    return source[pos];
  })
}

exports.getInitialClassifiers = (cutoff, preference = []) => {

  let sortedList = {};
  let picks = [];

  let adjacencyListClone = JSON.parse(JSON.stringify(adjacencyList));

  const choiceListCount = 5;
  const lastIndex = sortAdjacencyList(adjacencyListClone, sortedList);
  const sections = getSections(cutoff.lowerCutOff, cutoff.upperCutOff, lastIndex);
  
  sortedList = attachPreference(sortedList, preference);

  for(let pass = 0; pass < choiceListCount; pass++) {

    let choices = [];

    sections.forEach( row => {
      const start = row[0];
      const end = row[1];

      let infiniteLoopSentinel = 1000;
      let choiceIndex = getRandom(start, end);

      while(choices.includes(sortedList[choiceIndex])) {
        infiniteLoopSentinel -= 1;
        choiceIndex = getRandom(start, end);

        if(infiniteLoopSentinel <= 0) {
          console.log("FATAL ERROR: CONVERGING LIST")
          return choices;
        }
      }

      choices.push(sortedList[choiceIndex]);
    });

    picks.push(choices);
  }
  
  return picks;
}

exports.getSubsequentClassifiers = (cutoff, leadingClassifier, error = {}) => {

  if(!(leadingClassifier in adjacencyList)) {
    error.message = "Initial classifier not in dataset";
    return null;
  }

  let subsequentClassifiers = []
  adjacencyList[leadingClassifier].adjacents.forEach ( name => subsequentClassifiers.push(name) );

  const length = subsequentClassifiers.length;
  const absoluteUpperCutoff = Object.keys(adjacencyList).length - 2;
  // const absoluteLowerCutoff = cutoff.upperCutOff;
  const localUpperCutoff = ((cutoff.upperCutOff) / (absoluteUpperCutoff + 1) * length);
  const localLowerCutoff = ((cutoff.lowerCutOff) / (absoluteUpperCutoff + 1) * length);

  if(length < 6) {
    const supportOptions = this.getInitialClassifiers(cutoff)[0];
    let remaining = 6 - length, index = 5;
    
    while(remaining > 0) {
      subsequentClassifiers.push(supportOptions[index--]);
      remaining--;
    }
    
    return subsequentClassifiers;
  }

  if(length == 6)
    return subsequentClassifiers;

  if(
    length <= 10 ||
    localLowerCutoff < 1 ||
    localUpperCutoff - localLowerCutoff < 3 ||
    absoluteUpperCutoff - localUpperCutoff < 2
  ) {
    return getSampleInRange(0, length - 1, subsequentClassifiers, 6);
  }

  subsequentClassifiers.sort((a, b) => {
    return adjacencyList[a].popularity - adjacencyList[b].popularity;
  });

  const lessLikely = getSampleInRange(0, localLowerCutoff - 1, subsequentClassifiers, 1);
  const common = getSampleInRange(localLowerCutoff, localUpperCutoff - 1, subsequentClassifiers, 3);
  const mostLikely = getSampleInRange(localUpperCutoff, length - 1, subsequentClassifiers, 2);

  return [].concat(lessLikely).concat(common).concat(mostLikely);
}