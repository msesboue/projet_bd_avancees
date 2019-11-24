# docker run --rm --name neo4j_server -p 7474:7474 -p 7687:7687 -d neo4j
import json
from py2neo import Graph

NEO4J_PORT = 7687

user = "neo4j"
password = "projetBD"

neo4j_graph = Graph("localhost:{}".format(NEO4J_PORT), auth=(user,password))

with open('resto_min_dist_to_point.json', 'r', encoding='utf-8-sig') as f:
    resto_point = json.load(f)

# query = """
# WITH {json} AS document
# UNWIND document.restaurants AS restaurant
# MERGE (resto:Restaurant {nom: restaurant.nom, adresse: restaurant.adresse})
# MERGE (pts:PistePts {id: restaurant.point.ID, nom: restaurant.point.NOM_TOPOGRAPHIE, type: restaurant.point.TYPE, longitude: restaurant.point.coordinates.longitude, latitude: restaurant.point.coordinates.latitude})
# MERGE (pts)-[:DIST_TO_RESTO {dist: restaurant.min_dist}]->(resto)
# """

query = """
WITH {json} AS document
UNWIND document.points AS pts
MERGE (pts:PistePts {nom_topographie: pts.properties.NOM_TOPOGRAPHIE, longitude: pts.geometry.coordinates.longitude, latitude: pts.geometry.coordinates.latitude})
MERGE (pts)-[:DIST_TO_RESTO {dist: restaurant.min_dist}]->(resto)
"""

neo4j_graph.run(query, json = resto_point)