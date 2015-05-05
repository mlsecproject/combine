# Dockerfile for running combine - https://github.com/mlsecproject/combine
# written by Kyle Maxwell

#MAINTAINER Kyle Maxwell, krmaxwell@gmail.com
FROM ubuntu:14.04

RUN apt-get update && \
    apt-get upgrade -y
RUN apt-get install -y --no-install-recommends \
    python-pip  \
    python-dev \
    build-essential \
    python-virtualenv \
    git
RUN pip install tox

RUN groupadd -r combine && \
    useradd -r -g combine -d /home/combine -s /sbin/nologin -c "Combine user" combine

WORKDIR /home
RUN git clone https://github.com/mlsecproject/combine.git
ADD run_combine.sh /home/combine/run_combine.sh
ADD combine.cfg /home/combine/combine.cfg
RUN chown -R combine:combine /home/combine

USER combine
ENV HOME /home/combine
ENV USER combine

WORKDIR /home/combine
RUN make venv

ENTRYPOINT ["/bin/bash", "-c", "/home/combine/run_combine.sh"]