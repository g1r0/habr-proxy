FROM ubuntu:16.04

ENV LANG ru_RU.utf8
ENV PROXY_CONFIG_DIR /usr/src/app/config

RUN set -ex \
    # -------------------------------------------------------------------------
    # Installing required system packages.
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive \
        apt-get install --no-install-recommends --yes \
        ca-certificates \
        language-pack-ru \
        wget \
        g++ \
        libpq-dev \
        libssl-dev \
        libffi-dev \
        libxml2-dev \
        libxslt1-dev \
        libxmlsec1-dev \
        libreadline-dev \
        libbz2-dev \
    && apt autoremove \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    # -------------------------------------------------------------------------
    # Installing Python 3.6.5.
    && mkdir -p /usr/local/python/3.6 \
    && cd /tmp \
    && wget https://www.python.org/ftp/python/3.6.5/Python-3.6.5.tar.xz \
    && tar -xJf Python-3.6.5.tar.xz \
    && rm Python-3.6.5.tar.xz \
    && cd Python-3.6.5 \
    && ./configure \
        --prefix=/usr/local/python/3.6 \
    && make \
    && make install \
    && cd \
    && rm -r /tmp/Python-3.6.5 \
    && ln -s /usr/local/python/3.6/bin/python3.6 /usr/bin/python \
    && ln -s /usr/local/python/3.6/bin/pip3 /usr/bin/pip \
    && export PATH=/usr/local/python/3.6/bin:$PATH \
    # -------------------------------------------------------------------------
    # Create project dir.
    && mkdir -p /usr/src/app


WORKDIR /usr/src/app
COPY . .

RUN set -ex \
    # -------------------------------------------------------------------------
    # Installing environment requirements.
    && pip install --no-cache-dir -r requirements/prod.txt

ENTRYPOINT python /usr/src/app/src/server.py
