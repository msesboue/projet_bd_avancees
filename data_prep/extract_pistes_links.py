import json
from pymongo import MongoClient
import bson
from math import sin, cos, sqrt, atan2, radians

def get_distance(long1, lat1, long2, lat2):

    # approximate radius of earth in meter
    R = 6378100

    long1 = radians(long1)
    lat1 = radians(lat1)
    long2 = radians(long2)
    lat2 = radians(lat2)

    dlong = long2 - long1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlong / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    return distance

if __name__ == "__main__":
    
    mongo_server_uri = "localhost"

    MONGODB_PORT = 27017

    mongo_client = MongoClient("{}:{}".format(mongo_server_uri, MONGODB_PORT))

    db = mongo_client.appdb

    with open('../docker_app/app/data/pistes_cyclables.json', 'r', encoding='utf-8-sig') as f:
        pistes_data = json.load(f)

    # print(get_distance(-71.22898828705745, 46.80935156161798, -71.227863, 46.8131)) # doit être égal à 425.9880...

    # nb_piste = len(pistes_data)
    nb_piste = 5
    point_dist = {}
    point_dist['points'] = []

    for piste in range(nb_piste):
        nb_point = len(pistes_data[piste]['geometry']['coordinates'])
        piste_id = pistes_data[piste]['properties']['ID']

        for point in range(nb_point - 1):

            long1 = pistes_data[piste]['geometry']['coordinates'][point][0]
            lat1 = pistes_data[piste]['geometry']['coordinates'][point][1]
            long2 = pistes_data[piste]['geometry']['coordinates'][point+1][0]
            lat2 = pistes_data[piste]['geometry']['coordinates'][point+1][1]

            point_dist['points'].append({
                "ID": "{}.{}".format(piste_id, point + 1),
                "dist_to_next": get_distance(long1, lat1, long2, lat2),
                "extract": "{}.{}".format(piste_id, point + 2)
            })
        
        point_dist['points'].append({
                "ID": "{}.{}".format(piste_id, nb_point),
            })

with open('point_dist.json', 'w', encoding='utf-8-sig') as f:
    json.dump(point_dist, f, ensure_ascii=False)