# combine-docker

A simple Dockerfile for running [Combine](https://github.com/mlsecproject/combine). Also on [Docker Hub](https://registry.hub.docker.com/u/technoskald/combine/).

The easiest way to run is simply:

```
sudo docker pull technoskald/combine
sudo docker run --rm -v `pwd`/harvest.csv:/combine/harvest.csv technoskald/combine 
```

This will put the results in the `/combine` directory. Replace the path after the colon in the command line if desired.

If you prefer to use the Docker file rather than pull from the Docker Hub, then run with something like:
```
sudo docker build .
```
Then note the ID at the end and run:
```
sudo docker run --rm -v `pwd`/harvest.csv:/combine/harvest.csv IDHERE
```
