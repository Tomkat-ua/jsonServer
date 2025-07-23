database=sklad_prod
eport=8082
tag=`cat version`

container=jsonServer_$database
img=tomkat/jsonserver:$tag

docker container stop $container
docker container rm $container 

docker run -dt \
    -p $eport:8000 \
    --name=$container \
    -e APP_VERSION=$tag \
    -e TZ=Europe/Kyiv \
    -e DELAY_LOOP=30 \
    -e DB_HOST=192.168.10.5 \
    -e DB_PATH=$database \
    -e DB_USER=monitor \
    -e DB_PASSWORD=inwino \
    -e PORT=8000 \
    -e API_KEY=AIzaSyDtzSvLJesvqAUbySNq20egFBiKtZCKMEM \
    -e CHECK_EXT_IP=192.168.10.1 \
    --restart=always \
    $img
