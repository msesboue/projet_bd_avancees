import os
from flask import Flask, redirect, url_for, request, render_template
from pymongo import MongoClient, GEO2D

app = Flask("VeloEpicurien")

MONGODB_HOST = os.environ["MONGODB_PORT_27017_TCP_ADDR"]
MONGODB_PORT = 27017
client = MongoClient(MONGODB_HOST, MONGODB_PORT)

db = client.appdb

db.pistes.create_index([("geometry.coordinates", GEO2D)])
db.restaurants.create_index([("geometry.coordinates", GEO2D)])

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/heartbeat", methods=["GET"])
def heartbeat():
    nb_restaurant = client.appdb.restaurants.find().count()

    dist_pipeline = [
        {"$group": {"_id": '',"total_dist": { "$sum": "$properties.Longueur" }}}, 
        {"$project": {"_id": 0,"total_dist": "$total_dist"}}
    ]
    distance = list(db.pistes.aggregate(dist_pipeline))

    return render_template("index.html", nb_restaurant=nb_restaurant, distance_totale=distance[0]['total_dist'])

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

