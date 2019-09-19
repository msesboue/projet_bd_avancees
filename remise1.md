# Remise 1 : Évaluer la faisabilité

Afin de choisir la structure nécessaire à la mise en place de notre application, il est essentiel d'identifier clairement les besoins de ce système. Il importe ainsi de connaître les informations que l'utilisateur fournira à l'application afin d'exécuter les requêtes pour obtenir le résultat voulu.

Dans un premier temps, nous restreindrons l'utilisation de l'application aux pistes cyclables de la ville de Québec.L'application doit pouvoir suggérer un parcours cyclable rencontrant certains types de restaurants pour un nombre d'arrêts spécifiés et une distance maximale à parcourir.L'utilisateur doit donc fournir un lieu de départ (nom du lieu et/ou ses coordonnées), le type de restaurants recherchés (ex: cuisine française, thaï), un nombre d'arrêts ainsi que la distance maximale qu'il veut parcourir. L'application doit alors retourner une série de lieux (nom du lieu et/ou ses coordonnées) ordonnancés afin de décrire un trajet de la longueur maximale spécifiée, de même que les restaurants (nom du restaurant et/ou ses coordonnées) situés sur ce parcours pour le nombre d'arrêts souhaités.

Les bases de données supportant cette application doivent donc contenir minimalement les informations suivantes:

* Pour les pistes cyclables:
    - Nom du lieu
    - Coordonnées des points
* Pour les restaurants:
    - Nom du restaurants
    - Adresse du restaurant
    - Coordonnées du restaurants
    - Type de cuisine

L'application doit pouvoir calculer le parcours pour atteindre la distance maximale demandée, identifier les restaurants du type voulu situés à moins de 50 mètres du parcours et obtenir le nombre d'arrêts spécifiés.

## Stratégie d'acquisition des données

### Méthode d'acquisition et provenance des données

Nous utiliserons les données publiques de la ville de Québec. Cette dernière fournie les données géographiques de ses pistes cyclables : <https://www.donneesquebec.ca/recherche/fr/dataset/vque_24>

Pour les données concernant les restaurants, nous utiliserons une méthode de scrapping sur les pages du site <https://www.restoquebec.ca/>.

### Format des données

Les données concernant les pistes cyclables de la ville de Québec sont disponibles dans plusieurs formats : CSV, GEOJSON, KML, SHP. Nous utiliserons le format GEOJSON car celui ci est répendu, adapté aux applications web et supporté par la plupart des logiciels. Nous aurions pu choisir d'utiliser le format Shapefile qui est le plus répendu des formats de données geospatiales. Mais celui-ci implique à minima 3 fichiers (.SHP.DBF.SHX). De plus, nous devons générer le ficher des données restaurants à partir des données brutes récupérées, le format GEOJSON est plus facile à appréhender.

## Stratégie de déploiement

- quelles informations nous fourni l'utilisateur ?
- quelles information nous avons ? --> données spatiales des pistes cyclables + restaurants. 
- De quels informations sur les restaurants avons nous besoin ?
- Quelles requêtes fais l'utilisateur ?
- Quelles resultats doit-on fournir ?
- Quels calculs cela implique ?

### Serveur web

### Conteneur Docker

### Base de données

## Ressources

À propos des bases de données géospatiales :

- <http://michaelminn.net/tutorials/gis-storage/>
- <https://en.wikipedia.org/wiki/List_of_geographic_information_systems_software>
- <https://blog.westerndigital.com/geospatial-data-storage-infrastructure/>
- <https://en.wikipedia.org/wiki/Spatial_database>
- <https://www.planetwatchers.com/choosing-the-right-database-for-geoanalytics/>

Jeux de données : 

- <https://open.canada.ca/data/en/dataset>
- <https://www.donneesquebec.ca/recherche/fr/dataset/vque_24>
- <http://www.ressourcesentreprises.org/faites-votre-demande-en-ligne/faites-votre-demande-marche/>
- <https://www.restoquebec.ca/s/?restaurants=parking-available-quebec&f=23&lang=en> 