
const classifier = require("./source/classifier");
const cutoffs = require("./files/CutOffs.json");

const functions = require('firebase-functions');
const express = require('express');

const app = express();

const PREFERENCE_QUERY_PARAMETER = 'classifiers';

app.get('/timestamp', (req, res) => {
  res.send(`${Date.now()}`);
});

app.get('/setup', (req, res) => {
  let parameters = [];

  if(req.query[PREFERENCE_QUERY_PARAMETER] != null) {
    parameters = req.query[PREFERENCE_QUERY_PARAMETER];
    console.log("Setup classifiers requested with " + parameters.length + " params");
  } else {
    console.log("Setup classifiers requested");
  }
  
  let picks = classifier.getInitialClassifiers(cutoffs, parameters);

  res.status(200).json(picks);
});

app.get('/addon', (req, res) => {
  let parameters = [];

  if(req.query[PREFERENCE_QUERY_PARAMETER] == null) {
    console.log("Bad request query");
    res.status(404).json('No preference specified');
    return
  } else {
    parameters = req.query[PREFERENCE_QUERY_PARAMETER];
  }

  if(parameters instanceof Array && parameters.length == 0) {
    res.status(404).json('Bad request query');
    return;
  }

  if(parameters instanceof Array)
    parameters = parameters[0];

  let errors = {};
  console.log(`Add-on to ${parameters} requested`);
  const results = classifier.getSubsequentClassifiers(cutoffs, parameters, errors);

  if(results == null) {
    res.status(404).json(errors.message);
    return;
  } else {
    res.status(200).json(results);
    return;
  }
})

app.get('/restaurants', (req, res) => {
  res.status(400).json('Route has been deprecated. Please use other map APIs for this feature');
})

exports.app = functions.https.onRequest(app);
