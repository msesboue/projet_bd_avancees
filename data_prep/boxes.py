import json
import math

with open('../docker_app/app/data/pistes_cyclables.json', 'r', encoding='utf-8-sig') as f:
    file_pistes_data = json.load(f)

dx = 500
dy = 500
r_earth = 6378000

boxes = []
polygons = []

# nb_pistes = len(file_pistes_data)
nb_pistes = 5

piste_OBJECTIDs = [piste_id["properties"]["ID"] for piste_id in file_pistes_data]

for piste in range(nb_pistes):
    type_piste = file_pistes_data[piste]['properties']['TYPE']
    for segment in range(len(file_pistes_data[piste]['geometry']['coordinates']) - 1):
        segment_name = "{}.{}".format(piste_OBJECTIDs[piste], segment + 1)
        box_name = "box_{}.{}".format(piste_OBJECTIDs[piste], segment)
        
        # on récupère les coordonnées des deux point qui forment le segement
        long1 = file_pistes_data[piste]['geometry']['coordinates'][segment][0]
        lat1 = file_pistes_data[piste]['geometry']['coordinates'][segment][1]
        long2 = file_pistes_data[piste]['geometry']['coordinates'][segment + 1][0]
        lat2 = file_pistes_data[piste]['geometry']['coordinates'][segment + 1][1]

        delta_long1 = (dx / r_earth) * (180 / math.pi) / math.cos(lat1 * math.pi/180)
        delta_lat1 =  (dy / r_earth) * (180 / math.pi)
        delta_long2 = (dx / r_earth) * (180 / math.pi) / math.cos(lat2 * math.pi/180)
        delta_lat2 = delta_lat1
        
        # on calcul les points du rectangle
        top_left = [
            long1 - delta_long1, 
            lat1 + delta_lat1
        ]
        top_right = [
            long2 + delta_long2, 
            lat2 + delta_lat2
        ]
        bottom_right = [
            long2 + delta_long2, 
            lat2 - delta_lat2
        ]
        bottom_left = [
            long1 - delta_long1, 
            lat1 - delta_lat1
        ]

        # boxes.append({
        #     "type": "segment",
        #     "properties": {
        #         "ID": segment_name,
        #         "segment_type": type_piste
        #     },
        #     "geometry": {
        #             "type": "LineString",
        #             "coordinates": [[long1, lat1], [long2, lat2]]
        #     }
        # })

        polygons.append({
            "type": "Feature",
            "properties": {
                "segment_id": segment_name,
                "ID": file_pistes_data[piste]['properties']['ID']
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[top_left, top_right, bottom_right, bottom_left, top_left]]
            }
        })

        boxes.append({
            "type": "box_{}".format(dx),
            "properties": {
                "segment_id": segment_name,
                "ID": file_pistes_data[piste]['properties']['ID']
            },
            "box": [bottom_left, top_right]
        })

with open('pistes_boxes.json', 'w', encoding='utf-8-sig') as f:
    json.dump(boxes, f)

with open('pistes_polygons.json', 'w', encoding='utf-8-sig') as f:
    json.dump(polygons, f)