import os
from flask import Flask, jsonify, request
from pymongo import MongoClient, GEO2D
from py2neo import Graph
import json
from bson import json_util
import socket

if "production" in os.environ:
    mongo_server_uri = "mongo"
    neo4j_server_uri = "neo"
else:
    mongo_server_uri = "localhost"
    neo4j_server_uri = "localhost"

MONGODB_PORT = 27017
NEO4J_PORT = 7687
APP_PORT = 5000
user = "neo4j"
password = "projetBD"

app = Flask("Vélo Épicurien")
mongo_client = MongoClient("{}:{}".format(mongo_server_uri, MONGODB_PORT))
neo4j_graph = Graph("http://neo4j:7474/db/data/", auth=(user,password),bolt=False)

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
def get_starting_point():
    """
        Cet appel permet à un utilisateur ou une application cliente d’obtenir un point de départ aléatoire.
       
        Parameters
        ----------
        maximum_length : int
            La longueur maximale du trajet
        type : tableau de str
            Les types sont définis dans le tableau type

        Returns
        -------
        starting_point : GeoPoint
            Un point de départ aléatoire
    """
    maximum_length = int(request.args.get('maximum_length'))
    type_restaurant = []
    _type = str(request.args.get('type')).split('+')[0]
    for t in str(_type).split():
        type_restaurant.append(t)

    restaurant_set = db.restaurants.find({
        "properties.labels": {
            "$in":type_restaurant
        }
    },
    {
        "_id":0,
        "properties.nom": 1,
    })

    nom_restaurant = [doc["properties"]["nom"] for doc in restaurant_set]

    query = "match (p:PistePoint)-[w:way]->(r:Restaurant) where (r.nom in {}) and w.distance < {} return p, w.distance order by rand() limit 1".format(nom_restaurant,maximum_length)
    
    neo4j_graph.begin()
    starting_point = [x for x in neo4j_graph.run(query)]
    if len(starting_point) !=0:
        return jsonify({
                        "starting_point" : {
                            "type" : "GeoPoint",
                            "coordinates":{
                                "latitude" : starting_point[0][0]['latitude'],
                                "longitude" : starting_point[0][0]['longitude']
                            }
                        } 
                    })
    else:
        return jsonify({
            "Erreur" : "Aucun point n'a été trouvé, veuillez utiliser un des types définis dans 'http://localhost:8080/type'"
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
def parcours():
    """
        Cet appel permet à un utilisateur ou une application cliente d’obtenir un point de départ aléatoire.
       
        Parameters
        ----------
        maximum_length : int
            La longueur maximale du trajet
        type : tableau de str
            Les types sont définis dans le tableau type
        number_of_stop : int
            Le nombre de stop sur le trajet

        Returns
        -------
        starting_point : GeoPoint
            Un point de départ aléatoire
    """
    
    maximum_length = int(request.args.get('maximum_length'))
    type_restaurant = []
    number_of_stops = int(request.args.get('number_of_stops'))
    _type = str(request.args.get('type')).split('+')[0]
    for t in str(_type).split():
        type_restaurant.append(t)
    """
    maximum_length = 500
    number_of_stops = 2
    type_restaurant = ["Sandwichs"]
    """
    segments = []
    restaurant_set = db.restaurants.find({
        "properties.labels": {
            "$in":type_restaurant
        }
    },
    {
        "_id":0,
        "properties.nom": 1,
    })

    nom_restaurant = [doc["properties"]["nom"] for doc in restaurant_set]
    nom_restaurant_deja_visite = []
    distance_parcours = 0
    query = "match (p:PistePoint)-[w:way]->(r:Restaurant) where (r.nom in {}) and w.distance < {} return p, w.distance order by rand() limit 1".format(nom_restaurant,maximum_length)

    neo4j_graph.begin()
    starting_point = [x for x in neo4j_graph.run(query)]
    distance_parcours += starting_point[0][1]
    new_starting_point = [starting_point[0][0]['latitude'], starting_point[0][0]['longitude']]
    #resultat= []
    for it in range(0,number_of_stops):
        resultat = (neo4j_graph.run("match path = (starting_point:PistePoint)-[w:way*]->(restaurant:Restaurant) where (starting_point.latitude = {}) and (starting_point.longitude = {}) with path, reduce (sum = 0, r in w| sum + r.distance) as dist order by dist limit 1 return reduce(points = head(nodes(path)).nom, n in tail(nodes(path)) | points + '->' + n.nom) as res".format(new_starting_point[0],new_starting_point[1])))
        segments.append(resultat)
    temp = [doc for doc in resultat]
    return jsonify({
                    "path" : temp,
                    "Problème" : "Trop de points dans la base de donnée neo4j "
                })

@app.route("/readme", methods=['GET'])
def get_readme():
    readme = """
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
    ### Dans le browser, http://localhost:8080/starting-point?maximum_length=100&type=Sandwichs+Casse-croute
        On met les paramètres dans l'URL, maximun_lenght= 'distance' et type='liste de type de restaurant' (NB: les types sont séparés par le signe '+')

    ## Générer un parcours

    ```Bash
        Dans le browser, http://localhost:8080/parcours?maximum_length=500&type=Sandwichs+Poutine&number_of_stops=1
        
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
    return readme

if __name__ == "__main__":
    app.run("0.0.0.0", APP_PORT, debug=True)

