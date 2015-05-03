# combine-docker

A simple Dockerfile for running [Combine](https://github.com/mlsecproject/combine).

To build the docker image, copy a valid `combine.cfg` next to the `Dockerfile` and:
```shell
$ sudo docker build -t combine .
```

Then run with:
```
$ sudo docker run --rm -v `pwd`/output:/home/combine/output -t combine
```

This will put the results in the `./combine` directory. Replace the path after the colon in the command line if desired.
