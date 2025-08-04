bash ./bump_version.sh
tag=`cat version`
docker build -t tomkat/jsonserver:$tag  .

