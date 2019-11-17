import json
from pymongo import MongoClient

mongo_server_uri = "localhost"

MONGODB_PORT = 27017

mongo_client = MongoClient("{}:{}".format(mongo_server_uri, MONGODB_PORT))

db = mongo_client.appdb

nb_restaurant = db.restaurant.find().count()
nb_piste = db.pistes.find().count()

resto_per_area = {}

raw_piste_OBJECTIDs = list(db.pistes.find({}, {"_id":0, "properties.OBJECTID": 1}))
piste_OBJECTIDs = [piste_id["properties"]["OBJECTID"] for piste_id in raw_piste_OBJECTIDs]

for piste_obj_id in piste_OBJECTIDs:

    print("piste nb {}".format(piste_obj_id))

    nb_segment = len(list(db.pistes.find({"properties.OBJECTID": piste_obj_id}, {"_id":0, "geometry.coordinates":1}))[0]["geometry"]["coordinates"]) - 1
    
    print("nb_segment = {}".format(nb_segment))
    
    for segment in range(nb_segment):

        print("segment = {}".format(segment + 1))
        print("{}.{}".format(piste_obj_id, segment+1))
        print("piste nb {}".format(piste_obj_id))
        box_coordinates = list(db.pistes_boxes.find({"properties.segment_id": "{}.{}".format(piste_obj_id, segment + 1)}))[0]["geometry"]["coordinates"]

        print(box_coordinates)

        restos_in_area = list(db.restaurant.find({
                                        "loc": {
                                            "$geoWithin": {
                                                "$geometry": {
                                                    "type" : "Polygon",
                                                    "coordinates": box_coordinates
                                                }
                                            }
                                        }
                                    })
                                )

        resto_per_area["{}.{}".format(piste_obj_id, segment+1)] = restos_in_area

with open('resto_per_area.json', 'w', encoding='utf-8-sig') as f:
    json.dump(resto_per_area, f)



# box = list(db.pistes_boxes.find({"properties.segment_id": "1.1"}))[0]["geometry"]["coordinates"]

# box[0]['properties']['segment_id']

# len(list(db.pistes.find({"properties.OBJECTID": 1}, {"_id":0, "geometry.coordinates":1}))[0]["geometry"]["coordinates"])