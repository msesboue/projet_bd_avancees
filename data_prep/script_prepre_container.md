# Script des commandes pour préparer les conteneurs de préparation des données

## Préparation du container

docker run -d --name data_prep -p 27017:27017 mongo:4.2

docker cp ../docker_app/app/data/restaurants.json data_prep:/data/restaurants.json
docker cp ../docker_app/app/data/pistes_cyclables.json data_prep:/data/pistes_cyclables.json

docker cp pistes_boxes.json data_prep:/data/pistes_boxes.json
docker cp pistes_polygons.json data_prep:/data/pistes_polygons.json

docker exec -it data_prep bash

mongoimport --db appdb --collection restaurant --mode upsert --type json --file /data/restaurants.json --jsonArray
mongoimport --db appdb --collection pistes --mode upsert --type json --file /data/pistes_cyclables.json --jsonArray

mongoimport --db appdb --collection pistes_boxes --mode upsert --type json --file /data/pistes_boxes.json --jsonArray
mongoimport --db appdb --collection pistes_poly --mode upsert --type json --file /data/pistes_polygons.json --jsonArray

## Requêtes mongo

mongo
use appdb
show collections
db.restaurant.find().limit(1).pretty()
db.pistes.find().limit(1).pretty()
db.pistes_boxes.find().limit(1).pretty()

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

## GeoJson

Troisième paramètre des coordonnées d'un point est l'altitude

## restaurants à proximité d'une piste cyclable

Pour chaque document des pistes cyclables:

* Extraire chaque point des lineString
* Pour chaque 2 points consécutifs construire les 5 coordonnées des polygones entourant la ligne
  * <https://docs.mongodb.com/manual/reference/operator/query/geoWithin/>
* Pour chaque polygone construit faire une requête geowithin sur les restaurants
  * Récupérer les distances de chaque restaurants à la piste
* Stocker la liste des restaurants à chaque portion de piste
  * Penser à éliminer les doublons à l'intérieur d'une même portion de piste ? (geoNear)
* Extraire un document au format JSON
* Construire la BD Neo4J
  * noeuds: Portions de piste{ID, longueur}, restaurants{ID, nom}
  * liaisons: à_proximité{distance}, est_reliée_à

Casser les LineString en petit bout ?

### Construire un tableau de pairs de coorconnées consécutives

db.pistes.aggregate([
    {$project:{
        pistes_line:{$map:{
            input:{$range:[0,{$size:"$geometry.coordinates"}]},
            in:{$slice:["$geometry.coordinates","$$this",2]}
                }
            }
        }
    },
    {$unwind: "$pistes_line"},
    {$project: {_id:0, pistes_line: 1}},
    {$out: "box4piste"}
])

boxes = {}
skip = 0.0004522022

db.box4piste.find().limit(5).forEach(
    function(doc) {
        toinsert = {"doc._id":[
                [doc.pistes_line[0] - skip, doc.pistes_line[1] + skip],
                [doc.pistes_line[3] + skip, doc.pistes_line[4] + skip],
                [doc.pistes_line[3] + skip, doc.pistes_line[4] - skip],
                [doc.pistes_line[0] - skip, doc.pistes_line[1] - skip],
                [doc.pistes_line[0] - skip, doc.pistes_line[1] + skip]
            ]}
        db.boxes.insert(toinsert)
    }
)

db.boxes.insert( {"doc._id": [
                ["doc.pistes_line"[0][0] - skip, doc.pistes_line[0][1] + skip],
                ["doc.pistes_line"[1][0] + skip, doc.pistes_line[1][1] + skip],
                ["doc.pistes_line"[1][0] + skip, doc.pistes_line[1][1] - skip],
                ["doc.pistes_line"[0][0] - skip, doc.pistes_line[0][1] - skip],
                ["doc.pistes_line"[0][0] - skip, doc.pistes_line[0][1] + skip]
            ]})

### Calculer les coordonnées d'un rectangle 500 mètres autour d'un segment

ref : <https://stackoverflow.com/questions/7477003/calculating-new-longitude-latitude-from-old-n-meters>

new_latitude  = latitude  + (dy / r_earth) * (180 / pi);
new_longitude = longitude + (dx / r_earth) * (180 / pi) / cos(latitude * pi/180);

delta = 500 m
r_earth = 6378 km = 6378000 m

[[long1, lat1], [long2, lat2]] --> [
    [long1 - delta, lat1 + delta], 
    [long2 + delta, lat2 + delta],
    [long2 + delta, lat2 - delta],
    [long1 - delta, lat1 - delta], 
    [long1 - delta, lat1 + delta]
]

### Requête Mongo pour extraire les listes de restaurants à proximité par tronçon

nb_resto = db.restaurants.find().count()

for (i = 0; i < nb_resto; i++){
    box = db.pistes_boxes.find({},{_id: 0, "geometry.coordinates": 1}).limit(1).pretty()
}

db.restaurants.find(
   {
     loc: {
       $geoWithin: {
          $geometry: {
             type : "Polygon" ,
             coordinates: [ [ 
                    [-72.64067549439955, 46.6163308329641],
                    [-72.62780500366914, 46.61624551356211],
                    [-72.62780500366914, 46.60726216776201],
                    [-72.64067549439955, 46.607347487164],
                    [-72.64067549439955, 46.6163308329641]
                ] ]
          }
       }
     }
   }
)


db.restaurant.find(
   {
     "geometry":
       { $near :
          {
            $geometry: { type: "Point",  coordinates: [ -71.24003988088926, 46.83234451991697 ] },
            $maxDistance: 500
          }
       }
   }
)