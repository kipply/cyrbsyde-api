#!flask/bin/python
from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest, NotImplemented
import requests
#from gcpkey import *
import json
from config import *
import math

# from datetime import datetime

app = Flask(__name__)

config = Config()


@app.route('/api/getRideEstimate', methods=['GET'])
def get_estimate():
    data = request.args.to_dict()

    url = "https://api.lyft.com/v1/cost"

    payload = (
        '?start_lat=' + data['start_lat'] +
        '&start_lng=' + data['start_long'] +
        '&end_lat=' + data['end_lat'] +
        '&end_lng=' + data['end_long']
    )

    header = {
        'Authorization': config.LYFT_AUTH_HEADER
    }

    r = requests.get(url + payload, headers=header)

    results = r.json()['cost_estimates']

    returned_dict = {}

    for item in results:
        returned_dict[item['ride_type']] = {
            'display_name': item['display_name'],
            'lemgth': item['estimated_duration_seconds'],
            'distance': item['estimated_distance_miles'],
            'cost_min': item['estimated_cost_cents_min'],
            'cost_max': item['estimated_cost_cents_max'],
        }

    return jsonify(returned_dict)


@app.route('/api/getSearchResults', methods=['GET'])
def get_results():

    data = request.args.to_dict()

    r = requests.get('https://maps.googleapis.com/maps/api/place/textsearch/json?' +
                     'location=' + data['userLocation'] +
                     '&query=' + data['query'] +
                     '&key=' + config.GMAPS_KEY)

    results = r.json()['results']

    returned_list = []

    for item in results:
        returned_list.append(
            {
                'name': item['name'],
                'address': item['formatted_address'],
                'coords': item['geometry']['location']
            }
        )

    return jsonify(returned_list[:3])


@app.route('/api/getDirections', methods=['GET'])
def get_directions():

    data = request.args.to_dict()

    r = requests.get('https://maps.googleapis.com/maps/api/directions/json?' +
                     '&origin=' + data['origin'].replace(" ", "+") +
                     '&destination=' + data['destination'].replace(" ", "+") +
                     '&mode=' + data['mode'] +
                     '&key=' + config.GMAPS_KEY)

    results = r.json()

    return jsonify(results)

'''
gets other possible spots for pickup. if user is nowhere near a street, it returns an empty json.
'''
@app.route('/api/getOtherPickupSpots', methods=['GET'])
def get_other_spots():
    data = request.args.to_dict()

    orig_lat = float(data['lat'])
    orig_lon = float(data['lon'])

    r = requests.get('https://roads.googleapis.com/v1/nearestRoads?' + 
                     'key=' + config.GMAPS_ROADS_KEY +
                     '&points=' + str(orig_lat) + ',' + str(orig_lon))

    if len(r.json()) == 0:
        return jsonify(r.json())

    placeId = r.json()['snappedPoints'][0]['placeId']
    road_lat = float(r.json()['snappedPoints'][0]['location']['latitude'])
    road_lon = float(r.json()['snappedPoints'][0]['location']['longitude'])

    match = False

    cross_lat = 0.0
    cross_lon = 0.0
    factor = 1.0

    while not match:
        cross_lat = ((factor + 1) * road_lat) - orig_lat
        cross_lon = ((factor + 1) * road_lon) - orig_lon
        tempR = requests.get('https://roads.googleapis.com/v1/nearestRoads?' + 
                     'key=' + config.GMAPS_ROADS_KEY +
                     '&points=' + str(cross_lat) + ',' + str(cross_lon))
        if (placeId == tempR.json()['snappedPoints'][0]['placeId']):
            match = True
        else:
            factor /= 2

    results = {
        "other_side": {
            "latitude": cross_lat,
            "longitude": cross_lon
        }
    }

    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)
