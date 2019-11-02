import os
from flask import Flask, redirect, url_for, request, render_template
from pymongo import MongoClient


app = Flask("VeloEpicurien")

# To change accordingly 
#print(os.environ)
MONGODB_HOST = os.environ["MONGODB_PORT_27017_TCP_ADDR"]
MONGODB_PORT = 27017
client = MongoClient(MONGODB_HOST, MONGODB_PORT)
db = client.appdb
print(client.database_names())
print(client.appdb.collection_names())
for x in client.appdb.restaurant.find():
    print(x)
@app.route("/")
def index():
    _items = db.find()
    items = [items for items in _items]

    return render_template("index.html", items=items)

@app.route("/nb_restaurant", methods=["GET"])
def get_nb_restaurant():
    nb_restaurant = client.appdb.restaurant.find().count()
    #print(nb_restaurant)
    return render_template("index.html", nb_restaurant=nb_restaurant)

@app.route("/distance_totale", methods=["GET"])
def get_distance_totale():
    distance_totale = "À faire"
    return render_template("index.html", distance_totale=distance_totale)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

