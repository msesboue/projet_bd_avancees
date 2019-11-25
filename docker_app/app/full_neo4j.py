# docker run --rm --name neo4j_server -p 7474:7474 -p 7687:7687 -d neo4j
import json
from py2neo import Graph, NodeMatcher
from py2neo.data import Node, Relationship
from tqdm import tqdm
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
    
    NEO4J_PORT = 7687

    user = "neo4j"
    password = "projetBD"

    neo4j_graph = Graph("localhost:{}".format(NEO4J_PORT), auth=(user,password))

    with open('resto_min_dist_to_point_small.json', 'r', encoding='utf-8-sig') as f:
        resto_point = json.load(f)

    with open('point_list_small.json', 'r', encoding='utf-8-sig') as f:
            point_list = json.load(f)

    print("insertion des points")
    insert_points = neo4j_graph.begin()
    for point in tqdm(point_list['points']):
        point_node = Node(
            "PistePoint",
            id=point['properties']['ID'],
            topographie=point['properties']['NOM_TOPOGRAPHIE'],
            longitude=point['geometry']['coordinates']['longitude'],
            latitude=point['geometry']['coordinates']['latitude']
        )
        insert_points.create(point_node)
    insert_points.commit()

    print("insertion des restaurants")
    insert_resto = neo4j_graph.begin()
    for resto in tqdm(resto_point['restaurants']):
        resto_node = Node("Restaurant", 
                            nom=resto['nom'],
                            adresse=resto['adresse']
                            )
        insert_resto.create(resto_node)
    insert_resto.commit()

    print("liaison des points")

    link_points = neo4j_graph.begin()
    for point in tqdm(point_list['points']):
        matcher = NodeMatcher(neo4j_graph)
        node = matcher.match("PistePoint", id=point['properties']['ID']).first()
        node_long = point['geometry']['coordinates']['longitude']
        node_lat = point['geometry']['coordinates']['latitude']
        for link_pt in point['properties']['linked_to']:
            if len(link_pt) != 0:
                node_to_link = matcher.match("PistePoint", longitude=link_pt[0],latitude=link_pt[1]).first()
                node_to_link_long = link_pt[0]
                node_to_link_lat = link_pt[1]
                distance = get_distance(node_long, node_lat, node_to_link_long, node_to_link_lat)
                link_1 = Relationship(node, "way", node_to_link, distance=distance)
                link_2 = Relationship(node_to_link, "way", node, distance=distance)
                link_points.create(link_1)
                link_points.create(link_2)
    link_points.commit()

    print("liaison des restaurants")

    link_resto = neo4j_graph.begin()
    for resto in tqdm(resto_point['restaurants']):
        matcher = NodeMatcher(neo4j_graph)
        node_resto = matcher.match(
                                "Restaurant", 
                                nom=resto['nom'],
                                adresse=resto['adresse']
                                )
        point_node = matcher.match(
                                    "PistePoint",
                                    id=resto['point']["ID"]
                                )
        distance = resto["min_dist"]
        link = Relationship(point_node, "way_to_resto", resto_node, distance=distance)
        link_resto.create(link)
    link_resto.commit()


        