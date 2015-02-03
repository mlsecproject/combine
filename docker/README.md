# combine-docker

A simple Dockerfile for running [Combine](https://github.com/mlsecproject/combine). Also on [Docker Hub](https://registry.hub.docker.com/u/technoskald/combine/).

If you prefer to use the Docker file rather than pull from the Docker hub, then run with something like:
- `sudo docker build .`
Then note the ID at the end and run:
- `sudo docker run --rm -v \`pwd\`/harvest.csv:/combine/harvest.csv IDHERE`
