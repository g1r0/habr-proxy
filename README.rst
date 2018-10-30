About
_________________

Habr-proxy project has been done for the `test challenge #1
<https://github.com/ivelum/job/blob/master/code_challenges/python.md>`_.

Assamptions
_________________

* Service will be run locally. No remotes.
* Proxy is available at ``http://127.0.0.1:8080``.
* Demo can be run with local environment or docker image

What was used
_________________

* Python 3.6
* Mitmproxy
* Docker

How to run demo
_________________

Docker
~~~~~~~
Instructions for docker-powered demo can be found at ``docker/README.rst``.

Local python environment
~~~~~~~~~~~~~~~~~~~~~~~~~
1. Setup Python 3.6 environment and install dependencies for ``requirements/prod.txt``:

::

 pip install -r requirements/prod.txt

2. Set environment variable **PROXY_CONFIG_DIR** pointing to directory with ``config.yaml``.

::

 export PROXY_CONFIG_DIR=/path/to/config_dir

3. Run server with command:

::

 python src/server.py

Proxy is now available at ``http://127.0.0.1:8080``.