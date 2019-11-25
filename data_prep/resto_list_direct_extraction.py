import json
from pymongo import MongoClient
import bson

mongo_server_uri = "localhost"

MONGODB_PORT = 27017

mongo_client = MongoClient("{}:{}".format(mongo_server_uri, MONGODB_PORT))

db = mongo_client.appdb

with open('point_list.json', 'r', encoding='utf-8-sig') as f:
    point_list = json.load(f)

nb_point = len(point_list['points'])
# nb_piste = 5
nearby_dist = 500
restau_nearby = {}

restau_min_dist = {}

# init restau_min_dist with retaurant ids and a maximum distance value
restau_ids = list(db.restaurant.find({},{'_id':1}))
for resto in range(len(restau_ids)):
    restau_min_dist[str(bson.objectid.ObjectId(restau_ids[resto]['_id']))] = {
        'nom': None,
        'adresse': None,
        'min_dist': nearby_dist,
        'point': {}
    }


for point in range(nb_point):

    point_id = point_list['points'][point]['properties']['ID']

    point_coordinates = [
        point_list['points'][point]['geometry']['coordinates']['longitude'],
        point_list['points'][point]['geometry']['coordinates']['latitude']
    ]

    restau_around = list(db.restaurant.aggregate([{ 
                                            "$geoNear": {
                                                "near": point_coordinates,
                                                "distanceField": "distance",
                                                "spherical": "true",
                                                "distanceMultiplier": 6378100
                                            }},
                                            {"$project": 
                                                {"_id":1, "properties.nom":1, "properties.adresse":1, "distance":1}
                                            }
                                        ])
                                    )

    for resto in range(len(restau_around)):
        resto_id = str(bson.objectid.ObjectId(restau_around[resto]['_id']))

        current_min_dist = restau_min_dist[resto_id]['min_dist']
        new_dist = restau_around[resto]['distance']

        if new_dist < current_min_dist:
            restau_min_dist[resto_id]['nom'] = restau_around[resto]['properties']['nom']
            restau_min_dist[resto_id]['adresse'] = restau_around[resto]['properties']['adresse']
            restau_min_dist[resto_id]['point'] = {
                "ID" : point_list['points'][point]['properties']['ID'],
                "NOM_TOPOGRAPHIE" : point_list['points'][point]['properties']['NOM_TOPOGRAPIE'],
                "coordinates": {
                    'longitude': point_coordinates[0],
                    'latitude': point_coordinates[1]
                }
            }
            restau_min_dist[resto_id]['min_dist'] = new_dist

# clean restau_min_dist from the empty values
restau_min_dist_keys = list(restau_min_dist.keys())
for key in restau_min_dist_keys:
    if restau_min_dist[key]['nom'] == None:
        del restau_min_dist[key]

restau_min_dist_keys = list(restau_min_dist.keys())
restaurants_point = {}
restaurants_point['restaurants'] = []
for key in restau_min_dist_keys:
    restaurants_point['restaurants'].append(restau_min_dist[key])

with open('resto_min_dist_to_point.json', 'w', encoding='utf-8-sig') as f:
    json.dump(restaurants_point, f, ensure_ascii=False)

