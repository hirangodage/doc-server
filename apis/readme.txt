build the docker image
docker build -t usc-server .

run docker image
docker run -d -p 8089:8083 -t nginx