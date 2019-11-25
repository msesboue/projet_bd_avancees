import json
from pymongo import MongoClient

mongo_server_uri = "localhost"

MONGODB_PORT = 27017

mongo_client = MongoClient("{}:{}".format(mongo_server_uri, MONGODB_PORT))

with open('./app/data/pistes_cyclables.json', 'r', encoding='utf-8-sig') as f:
    file_pistes_data = json.load(f)

with open('./app/data/restaurants.json', 'r', encoding='utf-8-sig') as f:
    file_restaurants_data = json.load(f)

# mongo_client['velo_epicurien']['pistes'].insert(file_pistes_data)
mongo_client['velo_epicurien']['restaurants'].insert(file_restaurants_data)

mongo_client.close()