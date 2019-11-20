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

    nb_piste = len(pistes_data)
    # nb_piste = 5

    point_by_street = {}

    for piste in range(nb_piste):
        nb_point = len(pistes_data[piste]['geometry']['coordinates'])
        street_name = pistes_data[piste]['properties']['NOM_TOPOGRAPHIE']
        for point in range(nb_point):
            point_by_street[street_name] = []


    for piste in range(nb_piste):
        nb_point = len(pistes_data[piste]['geometry']['coordinates'])
        street_name = pistes_data[piste]['properties']['NOM_TOPOGRAPHIE']
        for point in range(nb_point):
            point_by_street[street_name].append(pistes_data[piste]['geometry']['coordinates'][point])

    for street in point_by_street.keys():
        nb_point = len(point_by_street[street])
        unique_points = []
        for point in range(nb_point - 1):
            if (point_by_street[street][point] != point_by_street[street][point+1]):
                unique_points.append(point_by_street[street][point])
        unique_points.append(point_by_street[street][nb_point-1])
        point_by_street[street] = unique_points

    topology_names = point_by_street.keys()

    point_list = []

    for topology_name in topology_names:
        nb_point = len(point_by_street[topology_name])
        for point in range(nb_point - 1):
            point_list.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": point_by_street[topology_name][point]
                },
                "properties": {
                    "NOM_TOPOGRAPIE": topology_name,
                    "linked_to": [point_by_street[topology_name][point + 1]]
                }
            })
        
        point_list.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": point_by_street[topology_name][nb_point - 1]
            },
            "properties": {
                "NOM_TOPOGRAPIE": topology_name,
                "linked_to": []
            }
        })

    pts_list = {}
    pts_list['points'] = point_list

    with open('point_list.json', 'w', encoding='utf-8-sig') as f:
        json.dump(pts_list, f, ensure_ascii=False)

    # point_dist = {}
    # point_dist['points'] = []

#     for piste in range(nb_piste):
#         nb_point = len(pistes_data[piste]['geometry']['coordinates'])
#         piste_id = pistes_data[piste]['properties']['ID']

#         for point in range(nb_point - 1):

#             long1 = pistes_data[piste]['geometry']['coordinates'][point][0]
#             lat1 = pistes_data[piste]['geometry']['coordinates'][point][1]
#             long2 = pistes_data[piste]['geometry']['coordinates'][point+1][0]
#             lat2 = pistes_data[piste]['geometry']['coordinates'][point+1][1]

#             point_dist['points'].append({
#                 "ID": "{}.{}".format(piste_id, point + 1),
#                 "dist_to_next": get_distance(long1, lat1, long2, lat2),
#                 "extract": "{}.{}".format(piste_id, point + 2)
#             })
        
#         point_dist['points'].append({
#                 "ID": "{}.{}".format(piste_id, nb_point),
#             })

# with open('point_dist.json', 'w', encoding='utf-8-sig') as f:
#     json.dump(point_dist, f, ensure_ascii=False)