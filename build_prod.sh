tag=`cat version`
#docker build -t tomkat/jsonserver:3  .
docker build -t tomkat/jsonserver:$tag  .

