import json
from pymongo import MongoClient

mongo_server_uri = "localhost"

MONGODB_PORT = 27017

mongo_client = MongoClient("{}:{}".format(mongo_server_uri, MONGODB_PORT))

db = mongo_client.appdb

with open('pistes_boxes.json', 'r', encoding='utf-8-sig') as f:
    pistes_boxes = json.load(f)

with open('pistes_polygons.json', 'r', encoding='utf-8-sig') as f:
    pistes_polygons = json.load(f)

with open('../docker_app/app/data/pistes_cyclables.json', 'r', encoding='utf-8-sig') as f:
    pistes_data = json.load(f)

nb_restaurant = db.restaurant.find().count()
nb_piste = len(pistes_data)

resto_per_area_box = {}
resto_per_area_poly = {}

piste_IDs = [piste["properties"]["ID"] for piste in pistes_data]

for piste in range(nb_piste):

    nb_segment = len(pistes_data[piste]['geometry']['coordinates']) - 1
    
    for segment in range(nb_segment):

        polygon_coordinates = pistes_polygons[piste + segment]['geometry']['coordinates']

        restos_in_area_poly = list(db.restaurant.find({
                                        "loc": {
                                            "$geoWithin": {
                                                "$geometry": {
                                                    "type" : "Polygon",
                                                    "coordinates": polygon_coordinates
                                                }
                                            }
                                        }
                                    })
                                )

        # box_coordinates = pistes_boxes[piste + segment]['box']

        # restos_in_area_box = list(db.restaurant.find({"loc": 
        #                                             {"$within": {
        #                                                 "$box": box_coordinates
        #                                                 }
        #                                             }
        #                                         })
        #                                     )

        # resto_per_area_box["{}.{}".format(piste_IDs[piste], segment+1)] = restos_in_area_box

        resto_per_area_poly["{}.{}".format(piste_IDs[piste], segment+1)] = restos_in_area_poly

# with open('resto_per_area_box.json', 'w', encoding='utf-8-sig') as f:
#     json.dump(resto_per_area_box, f)

with open('resto_per_area_poly.json', 'w', encoding='utf-8-sig') as f:
    json.dump(resto_per_area_poly, f)