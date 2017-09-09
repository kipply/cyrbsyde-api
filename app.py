#!flask/bin/python
from flask import Flask, request
from werkzeug.exceptions import BadRequest, NotImplemented
import requests

import googlemaps
# from datetime import datetime

app = Flask(__name__)

# gmaps = googlemaps.Client(key='AIzaSyDp4irqprDYWN5LviRYDJF4zfTi8ZMMObQ')

# Geocoding an address
# geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')

# Look up an address with reverse geocoding
# reverse_geocode_result = gmaps.reverse_geocode((40.714224, -73.961452))

# Request directions via public transit
# now = datetime.now()
# directions_result = gmaps.directions("Sydney Town Hall",
#                                      "Parramatta, NSW",
#                                      mode="transit",
#                                      departure_time=now)


@app.route('/api/getRideEstimate', methods=['GET'])
def get_estimate():
    print("Request:")
    data = request.args.to_dict()

    # Validate that all data points are valid (float lat/long value)
    for key in data.keys():
        print(data[key])
        try:
            float(data[key])
        except ValueError:
            raise BadRequest("Invalid lat/long value!")
    return 'hello, world!'


@app.route('/api/getWalkingDistance', methods=['GET'])
def get_tasks():
    raise NotImplemented("I haven't written this code yet")


@app.route('/api/getSearchSuggestions', methods=['GET'])
def get_suggestions():

    data = request.args.to_dict()

    r = requests.get('https://maps.googleapis.com/maps/api/place/textsearch/json?' +
                     'location=' + data['userLocation'] +
                     '&query=' + data['query'] +
                     '&key=AIzaSyDp4irqprDYWN5LviRYDJF4zfTi8ZMMObQ')

    newData = r.json()

    print(newData)
    print(newData['results'][0]['formatted_address'])

    return 'hello, world!'


if __name__ == '__main__':
    app.run(debug=True)
