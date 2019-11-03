# Script des commandes pour préparer les conteneurs de préparation des données

docker run -d --name data_prep mongo:3.6.1

docker cp restaurants.json data_prep:/data/restaurants.json
docker cp pistes_cyclables.json data_prep:/data/pistes_cyclables.json

docker exec -it data_prep bash

mongoimport --db appdb --collection restaurant --mode upsert --type json --file /data/restaurants.json --jsonArray
mongoimport --db appdb --collection pistes --mode upsert --type json --file /data/pistes_cyclables.json --jsonArray

mongo
use appdb
show collections
db.restaurant.find().limit(1).pretty()
db.pistes.find().limit(1).pretty()

db.pistes.createIndex({"geometry": "2dsphere"})

db.pistes.aggregate({
    $group: {
        _id: '',
        "total_dist": { $sum: '$properties.Longueur' }
    }
 }, {
    $project: {
        _id: 0,
        total_dist: '$total_dist'
    }
})

docker stop data_prep
docker system prune -f

