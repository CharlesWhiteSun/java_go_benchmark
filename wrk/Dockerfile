FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y git build-essential libssl-dev bash curl unzip iputils-ping && \
    git clone https://github.com/wg/wrk.git /tmp/wrk && \
    cd /tmp/wrk && make && mv wrk /usr/local/bin/wrk && \
    rm -rf /var/lib/apt/lists/* /tmp/wrk

WORKDIR /app

ENTRYPOINT [ "tail", "-f", "/dev/null" ]
