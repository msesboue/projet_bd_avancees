import os
from flask import Flask, jsonify
from pymongo import MongoClient, GEO2D
from py2neo import Graph

if "production" in os.environ:
    mongo_server_uri = "mongo"
    neo4j_server_uri = "neo"
else:
    mongo_server_uri = "localhost"
    neo4j_server_uri = "localhost"

MONGODB_PORT = 27017
NEO4J_PORT = 7687
APP_PORT = 5000

app = Flask("Vélo Épicurien")
mongo_client = MongoClient("{}:{}".format(mongo_server_uri, MONGODB_PORT))
neo4j_graph = Graph("http://{}".format(neo4j_server_uri), auth={"neo4j","projetBD"})

# MONGODB_HOST = os.environ["MONGODB_PORT_27017_TCP_ADDR"]
# client = MongoClient(MONGODB_HOST, MONGODB_PORT)

db = mongo_client.velo_epicurien

db.pistes.create_index([("geometry.coordinates", GEO2D)])
db.restaurants.create_index([("geometry.coordinates", GEO2D)])

@app.route("/", methods=["GET"])
def homepage():
    return "Bonjour et bienvenu dans notre application de vélo épicurien"

@app.route("/heartbeat", methods=["GET"])
def heartbeat():
    nb_restaurant = mongo_client.velo_epicurien.restaurants.find().count()

    dist_pipeline = [
        {"$group": {"_id": '',"total_dist": { "$sum": "$properties.Longueur" }}}, 
        {"$project": {"_id": 0,"total_dist": "$total_dist"}}
    ]
    distance = list(db.pistes.aggregate(dist_pipeline))

    return jsonify({
        "nb_restaurants": nb_restaurant,
        "total_path_length": distance[0]['total_dist']
    })

if __name__ == "__main__":
    app.run("0.0.0.0", APP_PORT, debug=True)

