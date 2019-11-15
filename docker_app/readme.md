# Application vélo épicurien

## Lancer l'application

```Bash
docker-compose build
docker-compose up
```

Si c'est le tout premier lancement, **penser à peupler les BDs**:

```Bash
python3 ./app/full_mongo.py
python3 ./app/full_neo4j.py
```

Puis entrez `localhost:8080` sur votre navigateur:

* Par défaut c'est la page d'acceuil qui s'affiche
* `localhost:8080/heartbeat` : affiche le nombre restaurants et la longueur de piste dans la base
