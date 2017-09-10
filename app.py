#!flask/bin/python
from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest, NotImplemented
import requests
import json
from config import *
import math

# from datetime import datetime

app = Flask(__name__)

config = Config()


def get_estimate(data):

    url = "https://api.lyft.com/v1/cost"

    payload = (
        '?start_lat=' + str(data['start_lat']) +
        '&start_lng=' + str(data['start_lon']) +
        '&end_lat=' + str(data['end_lat']) +
        '&end_lng=' + str(data['end_lon'])
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
            'length': item['estimated_duration_seconds'],
            'distance': item['estimated_distance_miles'],
            'cost_min': item['estimated_cost_cents_min'],
            'cost_max': item['estimated_cost_cents_max'],
        }

    return returned_dict


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


def get_directions(data):

    r1 = requests.get('https://maps.googleapis.com/maps/api/directions/json?' +
                      '&origin=' + data['origin'] +
                      '&destination=' + data['destination'] +
                      '&mode=transit' +
                      '&key=' + config.GMAPS_KEY)

    transit_results = r1.json()

    r2 = requests.get('https://maps.googleapis.com/maps/api/directions/json?' +
                      '&origin=' + data['origin'] +
                      '&destination=' + data['destination'] +
                      '&mode=walking' +
                      '&key=' + config.GMAPS_KEY)

    walking_results = r2.json()

    if transit_results['status'] == "OK":
        transit_time = transit_results['routes'][0]['legs'][0]['duration']
    else:
        transit_time = "NOT FOUND"

    if walking_results['status'] == "OK":
        walking_time = walking_results['routes'][0]['legs'][0]['duration']
    else:
        walking_time = "NOT FOUND"

    return {
        'transit_time': transit_time,
        'walking_time': walking_time
    }

# gets other possible spots for pickup. if user is nowhere near a street, it returns an empty json.


def get_other_spots(data):

    orig_lat = float(data['lat'])
    orig_lon = float(data['lon'])

    r = requests.get('https://roads.googleapis.com/v1/nearestRoads?' + 
                     'key=' + config.GMAPS_ROADS_KEY +
                     '&points=' + str(orig_lat) + ',' + str(orig_lon))

    if len(r.json()) == 0:
        return jsonify(r.json())

    place_id = r.json()['snappedPoints'][0]['placeId']
    road_lat = float(r.json()['snappedPoints'][0]['location']['latitude'])
    road_lon = float(r.json()['snappedPoints'][0]['location']['longitude'])

    match = False

    cross_lat = 0.0
    cross_lon = 0.0
    factor = 1.0

    while not match:
        cross_lat = ((factor + 1) * road_lat) - orig_lat
        cross_lon = ((factor + 1) * road_lon) - orig_lon
        temp_r = requests.get('https://roads.googleapis.com/v1/nearestRoads?' +
                              'key=' + config.GMAPS_ROADS_KEY +
                              '&points=' + str(cross_lat) + ',' + str(cross_lon))
        try:
            if place_id == temp_r.json()['snappedPoints'][0]['placeId']:
                match = True            
            else:
                factor /= 2
        except KeyError:
            factor /= 2

    results = [
        {
            "latitude": orig_lat,
            "longitude": orig_lon
        },
        {
            "latitude": cross_lat,
            "longitude": cross_lon
        }
    ]

    return results


@app.route('/api/getCombinedData', methods=['GET'])
def get_combined_data():
    data = request.args.to_dict()

    dest_lat = data['dest_lat']
    dest_lon = data['dest_lon']

    pickup_dict = get_other_spots({
        'lat': data['lat'],
        'lon': data['lon']
    })

    pickup_spots = []

    for key in pickup_dict:
        pickup_spots.append(pickup_dict[key])

    return_list = []

    for i in pickup_spots:
        spot_lat = i['latitude']
        spot_lon = i['longitude']

        lyft_data = get_estimate({
            'start_lat': spot_lat,
            'start_lon': spot_lon,
            'end_lat': dest_lat,
            'end_lon': dest_lon
        })

        time_data = get_directions({
            'origin': str(spot_lat) + ',' + str(spot_lon),
            'destination': str(dest_lat) + ',' + str(dest_lon)
        })

        return_list.append({
            'spot': {
                'spot_lat': spot_lat,
                'spot_lon': spot_lon
            },
            'lyft_data': lyft_data['lyft'],
            'time_data': time_data
        })

    return jsonify(return_list)


if __name__ == '__main__':
    app.run(debug=True)
