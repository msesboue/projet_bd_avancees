# Script des commandes pour préparer les conteneurs de préparation des données

## Préparation du container

docker run -d --name data_prep mongo:3.6.1

docker cp restaurants.json data_prep:/data/restaurants.json
docker cp pistes_cyclables.json data_prep:/data/pistes_cyclables.json

docker exec -it data_prep bash

mongoimport --db appdb --collection restaurant --mode upsert --type json --file /data/restaurants.json --jsonArray
mongoimport --db appdb --collection pistes --mode upsert --type json --file /data/pistes_cyclables.json --jsonArray

## Requêtes mongo

mongo
use appdb
show collections
db.restaurant.find().limit(1).pretty()
db.pistes.find().limit(1).pretty()

### Création de l'index géographique

db.pistes.createIndex({"geometry": "2dsphere"})
db.restaurant.createIndex({"geometry": "2dsphere"})

### Longueur totale de piste cyclable

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

## Nettoyage de la BD

db.pistes.updateMany({},{
    $unset: {
        "properties.OBJECTID": true,
        "properties.Type": true,
        "properties.ShapeSTLength": true,
        "type": true
    }
})

C'est le dossier /data/db/journal/ qui est très lourd
il peut être supprimé ou en tout cas non passé via le volume car mongo c'est le recréer à la volée

## Autres requêtes

docker stop data_prep
docker system prune -f

du -sh /data/db/    # taille d'un dossier
