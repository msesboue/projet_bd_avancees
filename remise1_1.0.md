# Remise 1 : Évaluer la faisabilité

Les bases de données supportant l'application doivent contenir au minimum les informations suivantes:

* Les pistes cyclables : nom du lieu, coordonnées des points
* Les restaurants : nom du restaurant, addresse du restaurant, coordonnées du restaurant, type de cuisine

L'application doit pouvoir calculer un parcours pour atteindre la distance maximale demandée, identifier les restaurants du type voulu situés à moins de 50 mètres du parcours et obtenir le nombre d'arrêts spécifiés.

Pour les besoin de l'application nous devons stocker:

* Les données utilisateurs de bases (nom, prénom, image de profil ...)
* Les données spatiales pour les pistes cyclables et les restaurants de la ville de Québec
* Les données spécifiques concernant les restaurants (type, adresse postale, description ...)

Méthode d'acquisition et provenance des données :

* Données publiques de la ville de Québec qui contiennent un jeu de données sur les pistes cyclables de QC : <https://www.donneesquebec.ca/recherche/fr/dataset/vque_24>
* Les restaurants : nous utiliserons une méthode de scrapping sur les pages du site <https://www.restoquebec.ca/>.

Format des données :

* Données des pistes cyclables : format GEOJSON.
* Nous devons générer le ficher GEOJSON des données restaurants à partir des données brutes récupérées.

Serveur web : Nous choisierons Nginx.

Base de données :
  
* Les données utilisateurs seront stockées dans une base de données de type clé-valeur, avec l'identifiant des utilisateurs comme clé. De même nous stockerons dans une BD similaire les données des restaurants avec l'identifiant des restaurants en clé. Nous considérons la BD Amazone DynamoBD pour le stockage des ces données.
* Pour les données spatiales notre choix se porte sur MongoDB. Nous y stockerons d'une part les données des pistes cyclables ainsi que celles des points correspondant à la localisation des restaurants.
* Enfin nous envisageons la possibilité de stocker certaines informations sur les restaurants, comme leurs types, dans une BD orientée colonnes pour optimiser les recherches en fonction de critères particuliers. Nous considérons la BD MariaDB pour cela.

Conteneurs Docker :

* Des images docker existent pour chacune des bases de données que nous souhaitons utiliser, ainsi que pour le serveur Nginx: <https://hub.docker.com/_/nginx>, <https://hub.docker.com/_/mongo>, <https://hub.docker.com/r/amazon/dynamodb-local/>, <https://hub.docker.com/_/mariadb>
