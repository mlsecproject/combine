# combine-docker

A simple Dockerfile for running [Combine](https://github.com/mlsecproject/combine).

To build the docker container, copy a valid `combine.cfg` next to the `Dockerfile` and build:
```shell
$ sudo docker build -t combine .
```

Then create a directory for the container's output:
```
$ mkdir output
$ chown 0777 output
```

Finally, run with:
```shell
$ sudo docker run --rm -v `pwd`/output:/home/combine/output -t combine
```

This will put the results in the `./combine` directory. Replace the path after the colon in the command line if desired.
