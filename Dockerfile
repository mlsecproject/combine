# Dockerfile for running combine - https://github.com/mlsecproject/combine
# written by Jose Nazario from Kyle Maxwell's

MAINTAINER jose nazario jose@monkey.org
FROM python:2
RUN groupadd -r combine && \
    useradd -r -g combine -d /home/combine -s /sbin/nologin -c "Combine user" combine

WORKDIR /home/combine
USER combine
ENV HOME /home/combine
ENV USER combine
ADD . /home/combine
COPY combine-example.cfg /home/combine/combine.cfg
USER root
RUN pip install -r requirements.txt && \
    chown -R combine:combine /home/combine 
USER combine
CMD ["python", "combine.py", "-e"]
