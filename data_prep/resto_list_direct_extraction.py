import json
from pymongo import MongoClient
import bson

mongo_server_uri = "localhost"

MONGODB_PORT = 27017

mongo_client = MongoClient("{}:{}".format(mongo_server_uri, MONGODB_PORT))

db = mongo_client.appdb

with open('../docker_app/app/data/pistes_cyclables.json', 'r', encoding='utf-8-sig') as f:
    pistes_data = json.load(f)

# nb_piste = len(pistes_data)
nb_piste = 5
nearby_dist = 500
piste_length = 0
restau_nearby = {}

restau_min_dist = {}

# init restau_min_dist with retaurant ids and a maximum distance value
restau_ids = list(db.restaurant.find({},{'_id':1}))
for resto in range(len(restau_ids)):
    restau_min_dist[str(bson.objectid.ObjectId(restau_ids[resto]['_id']))] = {
        'nom': None,
        'adresse': None,
        'point_id': None,
        'min_dist': nearby_dist
    }


for piste in range(nb_piste):
    piste_length += pistes_data[piste]['properties']['LONGUEUR']

    nb_point = len(pistes_data[piste]['geometry']['coordinates'])
    piste_id = pistes_data[piste]['properties']['ID']

    for point in range(nb_point):

        point_coordinates = pistes_data[piste]['geometry']['coordinates'][point]

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
                restau_min_dist[resto_id]['point_id'] = '{}.{}'.format(piste_id, point + 1)
                restau_min_dist[resto_id]['min_dist'] = new_dist

# clean restau_min_dist from the empty values
restau_min_dist_keys = list(restau_min_dist.keys())
for key in restau_min_dist_keys:
    if restau_min_dist[key]['nom'] == None:
        del restau_min_dist[key]

with open('resto_min_dist_to_point.json', 'w', encoding='utf-8-sig') as f:
    json.dump(restau_min_dist, f, ensure_ascii=False)

