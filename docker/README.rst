Building image
--------------------------

::

  docker build -t habr_proxy -f docker/Dockerfile .

Running demo
--------------------------

::

  docker run -it -p 127.0.0.1:8080:8080 habr_proxy

Service is now available at ``http://127.0.0.1:8080``.
