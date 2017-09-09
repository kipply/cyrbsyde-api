#!flask/bin/python
from flask import Flask, jsonify
import googlemaps
from datetime import datetime

app = Flask(__name__)

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]

gmaps = googlemaps.Client(key='AIzaSyDp4irqprDYWN5LviRYDJF4zfTi8ZMMObQ')

# Geocoding an address
geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')

# Look up an address with reverse geocoding
reverse_geocode_result = gmaps.reverse_geocode((40.714224, -73.961452))

# Request directions via public transit
now = datetime.now()
directions_result = gmaps.directions("Sydney Town Hall",
                                     "Parramatta, NSW",
                                     mode="transit",
                                     departure_time=now)


@app.route('/api/getWalkingDistance', methods=['GET'])
def get_tasks():
    return directions_result

if __name__ == '__main__':
    app.run(debug=True)
