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

db = mongo_client.velo_epicurien

# db.pistes.create_index([("geometry.coordinates", GEO2D)])
# db.restaurants.create_index([("geometry.coordinates", GEO2D)])

@app.route("/", methods=["GET"])
def homepage():
    return "Bonjour et bienvenu dans notre application de vélo épicurien"

@app.route("/type", methods=["GET"])
def type():
    restaurants_type = mongo_client.velo_epicurien.restaurants.distinct("properties.labels")
    return jsonify({
        "restaurants_type" : restaurants_type,
    })

@app.route("/starting-point", methods=['GET'])
def get_starting_point(maximum_length, type):

    return jsonify({
                "starting_point" : {
                    "type": "GeoPoint", 
                    "coordinates": {
                        "latitude":"un float", 
                        "longitude":"un float"
                    }
                }
            })

@app.route("/heartbeat", methods=["GET"])
def heartbeat():
    nb_restaurant = mongo_client.velo_epicurien.restaurants.find().count()

    dist_pipeline = [
        {"$group": {"_id": '',"total_dist": { "$sum": "$properties.LONGUEUR" }}}, 
        {"$project": {"_id": 0,"total_dist": "$total_dist"}}
    ]
    distance = list(db.pistes.aggregate(dist_pipeline))

    return jsonify({
        "nb_restaurants": nb_restaurant,
        "total_path_length": distance[0]['total_dist']
    })

@app.route("/parcours", methods=["GET"])
def parcours(starting_point, maximum_length, number_of_stops, type):
    restaurant_set = db.restaurants.find({
        "properties.labels": {
            "$in":type
        }
    },
    {
        "_id":0,
        "properties.nom": 1,
        "properties.adresse": 1
    })
    
    return "Désolé, cette fonctionnalité est en cours de construction"

@app.route("/readme", methods=['GET'])
def get_readme():
    """
    # Bienvenu dans l'application du vélo épicurien !

    J'espère que vous êtes prêt parce ce que vous allez rentrer en roulant !

    ## Home page
    
    ```Bash
        @GET /heartbeat

        returns: "Bonjour et bienvenu dans notre application de vélo épicurien"
    ```

    ## Des statistiques de bases sur les bases de données

    ```Bash
        @GET /heartbeat

        returns:
        {
            "nb_restaurants":int,
            "total_path_length":float
        }
    ```

    ## README
    
    ```Bash
        @GET /readme
        
        returns: Ce README en markdown
    ```

    ## Les Types de Restaurants

    ```Bash
        @GET /type

        returns:
        [
            str,
            str,
            str,
            ...
        ]
    ```

    ## Obtenir un point de départ

    ```Bash
        @GET /starting-point
        {
            "maximum_length": int (en mètre),
            "type": [str, str, ... ]
        }

        returns:
        {
            "starting_point" : {"type":"Point", "coordinates":{"latitude":float, "longitude":float}}
        }
    ```

    ## Générer un parcours

    ```Bash
        @GET /parcours
        {
            "starting_point" : {"type":"Point", "coordinates":{"latitude":float, "longitude":float}},
            "maximum_length": int (en mètre),
            "number_of_stops": int,
            "type": [str, str, ... ]
        }

        returns:
        [
            {
                "segment_id":1,
                path: {type:"LineString", "coordinates":{"latitude":float, "longitude":float}},
                restaurant: {
                    "name": string,
                    "type": string,
                    "cote": float,
            },{
                "segment_id":2,
                ....   
            }
        ]
    ```
    """

if __name__ == "__main__":
    app.run("0.0.0.0", APP_PORT, debug=True)

