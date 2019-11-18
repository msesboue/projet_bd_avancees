import json
from pymongo import MongoClient
from bson.son import SON

mongo_server_uri = "localhost"

MONGODB_PORT = 27017

mongo_client = MongoClient("{}:{}".format(mongo_server_uri, MONGODB_PORT))

db = mongo_client.appdb

with open('../docker_app/app/data/pistes_cyclables.json', 'r', encoding='utf-8-sig') as f:
    pistes_data = json.load(f)

nb_piste = len(pistes_data)
nearby_dist = 500
piste_length = 0
restau_nearby = {}

for piste in range(nb_piste):
    piste_length += pistes_data[piste]['properties']['LONGUEUR']

    nb_point = len(pistes_data[piste]['geometry']['coordinates'])
    piste_id = pistes_data[piste]['properties']['ID']

    for point in range(nb_point):

        point_coordinates = pistes_data[piste]['geometry']['coordinates'][point]

        restau_around = list(db.restaurant.find({
                                            "geometry":
                                            { "$near" :
                                                {
                                                    "$geometry": { "type": "Point",  "coordinates": point_coordinates },
                                                    "$maxDistance": nearby_dist
                                                }
                                            }
                                        }, {"_id":0, "properties.nom":1, "properties.adresse":1}))

        restau_nearby['{}.{}'.format(piste_id, point + 1)] = [restau['properties'] for restau in restau_around]

with open('resto_around_point.json', 'w', encoding='utf-8-sig') as f:
    json.dump(restau_nearby, f, ensure_ascii=False)

