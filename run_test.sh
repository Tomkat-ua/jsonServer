database=sklad_prod
eport=8081

container=jsonServer_test_$database
img=tomkat/jsonserver:test

docker container stop $container
docker container rm $container 
 
bash build_test.sh

docker run -dt \
    -p $eport:8000 \
    --name=$container \
    -v ${PWD}/qrys.json:/app/qrys.json \
    -e TZ=Europe/Kyiv \
    -e DELAY_LOOP=30 \
    -e DB_HOST=192.168.10.5 \
    -e DB_PATH=$database \
    -e DB_USER=monitor \
    -e DB_PASSWORD=inwino \
    -e PORT=8000 \
    --restart=always \
    $img
