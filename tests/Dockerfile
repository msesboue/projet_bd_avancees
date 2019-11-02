FROM mongo:4.0

RUN mongoimport --db pistes --collection piste_velo --file vdq-reseaucyclable.json

CMD [ "mongo" ]