# Remise 2
Veuillez vous référer à l'énoncé du projet pour les fonctionnalités que votre application doit supporter

## À remettre
* Archive compressée comprenant
  * docker-compose.yml 
  * répertoire comprenant votre application
  * répertoire des points de montages de données des bases de données

### Docker-compose.yml
* Gabarit non fonctionnel fourni
* Doit permettre de lancer votre application via la commande `docker-compose up`
    * lance le conteneur de l'API
    * lance le(s) conteneur(s) de base de données avec les données

### Répertoire de l'application
* Doit comprendre le fichier dockerfile pour `builder` l'image de l'application
* Doit comprendre le code source de votre application

### Répertoire des points de montage de données
* Seulement les répertoires des données (*pas les répertoires des binaires du moteur de bd*)
* Les données doivent s'y retrouver
* Devrait peser environ au maximum 5 Mo
* Par exemple, lors de l'initialisation de la BD, ce répertoire pèse pour 
  * MongoDB: 198kb
  * Neo4J: 131kb


