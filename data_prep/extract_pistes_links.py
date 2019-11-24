import json
from math import sin, cos, sqrt, atan2, radians
from shapely.geometry import LineString

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

    return 

def get_intersection_point(seg1_long1, seg1_lat1, 
                           seg1_long2, seg1_lat2,
                           seg2_long1, seg2_lat1, 
                           seg2_long2, seg2_lat2,
                           ):
    segment1 = LineString([(seg1_long1, seg1_lat1), (seg1_long2, seg1_lat2)])
    segment2 = LineString([(seg2_long1, seg2_lat1), (seg2_long2, seg2_lat2)])
    intersection = segment1.intersection(segment2)
    if intersection.geom_type == 'Point':
        return [intersection.x, intersection.y]
    else:
        return False

def get_intersection_points(point_by_street):
    
    topo_id = 0
    topology_names = point_by_street.keys()
    intersection_points = []

    for topology_name in topology_names:
        nb_point = len(point_by_street[topology_name])
        topo_id += 1
        for point in range(nb_point - 1):
            seg1_long1 = point_by_street[topology_name][point][0]
            seg1_lat1 = point_by_street[topology_name][point][1]
            seg1_long2 = point_by_street[topology_name][point+1][0]
            seg1_lat2 = point_by_street[topology_name][point+1][1]

            for key in topology_names:
                nb_point_in = len(point_by_street[key])
                for i in range(nb_point_in - 1):
                    if (key == topology_name) or ((key == topology_name) and (point == i)):
                        pass
                    else:
                        seg2_long1 = point_by_street[key][i][0]
                        seg2_lat1 = point_by_street[key][i][1]
                        seg2_long2 = point_by_street[key][i+1][0]
                        seg2_lat2 = point_by_street[key][i+1][1]

                        intersection_point = get_intersection_point(seg1_long1, seg1_lat1, 
                                                                    seg1_long2, seg1_lat2,
                                                                    seg2_long1, seg2_lat1, 
                                                                    seg2_long2, seg2_lat2,)
                        if intersection_point:
                            intersection_points.append({
                                "coordinates": intersection_point,
                                "line1": {
                                    "point1": [seg1_long1, seg1_lat1],
                                    "point2": [seg1_long2, seg1_lat2],
                                    "topo_name": topology_name
                                },
                                "line2": {
                                    "point1": [seg2_long1, seg2_lat1],
                                    "point2": [seg2_long2, seg2_lat2],
                                    "topo_name": key
                                }
                            })
    return intersection_points

if __name__ == "__main__":
    
    with open('../docker_app/app/data/pistes_cyclables.json', 'r', encoding='utf-8-sig') as f:
        pistes_data = json.load(f)

    # nb_piste = len(pistes_data)
    nb_piste = 500

    point_by_street = {} # will be a dict(key=topo_name, value[points])

    # initiate each key (topo_name) with an empty list
    for piste in range(nb_piste):
        nb_point = len(pistes_data[piste]['geometry']['coordinates'])
        street_name = pistes_data[piste]['properties']['NOM_TOPOGRAPHIE']
        for point in range(nb_point):
            point_by_street[street_name] = []

    # add the list of point for each topo name (key)
    for piste in range(nb_piste):
        nb_point = len(pistes_data[piste]['geometry']['coordinates'])
        street_name = pistes_data[piste]['properties']['NOM_TOPOGRAPHIE']
        for point in range(nb_point):
            point_by_street[street_name].append(pistes_data[piste]['geometry']['coordinates'][point])

    # remove duplicates point in each list of points
    for street in point_by_street.keys():
        nb_point = len(point_by_street[street])
        unique_points = []
        for point in range(nb_point - 1):
            if (point_by_street[street][point] != point_by_street[street][point+1]):
                unique_points.append(point_by_street[street][point])
        unique_points.append(point_by_street[street][nb_point-1])
        point_by_street[street] = unique_points

    intersection_points = get_intersection_points(point_by_street)

    # with open('intersection_point_list.json', 'r', encoding='utf-8-sig') as f:
    #     intersection_points = json.load(f)

    topology_names = point_by_street.keys()

    with open('intersection_point_list.json', 'w', encoding='utf-8-sig') as f:
        json.dump(intersection_points, f, ensure_ascii=False)


    point_list = []
    topo_id = 0 # initiate id for topo_names
    point_id = 0 # initiate id for points

    # create the final structure for points in a same line
    for topology_name in topology_names:
        nb_point = len(point_by_street[topology_name])
        topo_id += 1
        for point in range(nb_point - 1):
            point_id += 1
            point_list.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": {
                        "longitude": point_by_street[topology_name][point][0],
                        "latitude": point_by_street[topology_name][point][1]
                    }
                },
                "properties": {
                    "ID": "{}.{}".format(topo_id, point_id),
                    "NOM_TOPOGRAPIE": topology_name,
                    "linked_to": [point_by_street[topology_name][point + 1]]
                }
            })
        
        point_list.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": {
                    "longitude": point_by_street[topology_name][nb_point - 1][0],
                    "latitude": point_by_street[topology_name][nb_point - 1][1]
                }
            },
            "properties": {
                "ID": "{}.{}".format(topo_id, point_id + 1),
                "NOM_TOPOGRAPIE": topology_name,
                "linked_to": []
            }
        })
        point_id = 0

    ieme_inter = 0

    # add intersections points
    for interserction_pt in intersection_points:
        ieme_inter +=1
        point_list.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": {
                    "longitude": interserction_pt['coordinates'][0],
                    "latitude": interserction_pt['coordinates'][1]
                } 
            },
            "properties": {
                "ID": "intersection_{}".format(ieme_inter),
                "NOM_TOPOGRAPIE": 'intersection_{}_{}'.format(
                                    interserction_pt['line1']['topo_name'], 
                                    interserction_pt['line2']['topo_name']
                                    ),
            # we only consider the second point of both lines since we want to 
            # insert the intersection point in between the 2 points 
                "linked_to": [
                    interserction_pt['line1']['point2'],
                    interserction_pt['line2']['point2']
                ]
            }
        })

        long_pt1_line1 = interserction_pt['line1']['point1'][0]
        lat_pt1_line1 = interserction_pt['line1']['point1'][1]
        long_pt1_line2 = interserction_pt['line2']['point1'][0]
        lat_pt1_line2 = interserction_pt['line2']['point1'][1]

        iem_pt = 0

        # updates the first point of each line so they are now linked to the intersection point 
        for pt in point_list:
            # insert intersection point in first line
            if (
                (pt['geometry']['coordinates']['longitude'] == long_pt1_line1) 
                and 
                (pt['geometry']['coordinates']['latitude'] == lat_pt1_line1)
                ):
                # to check if the next point is the correct one
                next_pt_long = pt['properties']['linked_to'][0][0]
                next_pt_lat = pt['properties']['linked_to'][0][1]
                print(
                    (next_pt_long == interserction_pt['line1']['point2'][0])
                    and
                    (next_pt_lat == interserction_pt['line1']['point2'][1])
                )

                point_list[iem_pt]['properties']['linked_to'] = interserction_pt['coordinates']

            # insert intersection point in second line
            elif (
                (pt['geometry']['coordinates']['longitude'] == long_pt1_line2) 
                and 
                (pt['geometry']['coordinates']['latitude'] == lat_pt1_line2)
                ):
                # to check if the next point is the correct one
                print(pt['properties']['ID'])
                next_pt_long = pt['properties']['linked_to'][0][0]
                next_pt_lat = pt['properties']['linked_to'][0][1]
                print(
                    (next_pt_long == interserction_pt['line2']['point2'][0])
                    and
                    (next_pt_lat == interserction_pt['line2']['point2'][1])
                )

                point_list[iem_pt]['properties']['linked_to'] = interserction_pt['coordinates']

            iem_pt += 1

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