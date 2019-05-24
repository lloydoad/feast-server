# FEAST SERVER
An API Manager for iOS Feast application.
* Parses Yelp Open Dataset to get wide range of restaurant classification options
* Converts data to applicable bell curve to determine most relevant options per use case
* Makes various API requests to provide valid restaurants based on provided classifiers

## Routes
#### Base URL
URL: ```not deployed```

#### Classifiers and Avalailable Restaurants
| Route                           | Query (Required)               | Purpose                                         |
| -------------                   |:-------------                  | :-------------                                  |
|```/setup?```                    | ```classifiers:[String]```     | Returns initial classifier suggestions to user .These classifiers are used to skew search results in case of specified user preferences |
|```/addon?```                    | ```classifiers:[String]```     | Returns an array of relevant classifiers closely related to the request. This narrows down search critirea. Note: only the first value of this array is used. |
|```/restaurants?```              | ```classifiers:[String], longitude:Float, latitude:Float```     | Returns a list of restaurants matching provided classifiers within 40000 meters of users geographical latitude and longitude. For example: ```/restaurants?classifiers=pizza&latitude=28.5949131&longitude=-81.2204206```|
