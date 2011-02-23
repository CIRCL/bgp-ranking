************
Installation
************


Get the programms you need
==========================

Direct dependencies of BGP Ranking:

::
    
    apt-get install python-dateutil python-feedparser python-cherrypy3 python-cheetah python-ipy


Dependencies of libbgpdump + gcc (compilation :) ) + unzip (rgraph is zipped):

::
    
    apt-get install gcc autoconf zlib1g-dev libbz2-dev unzip


Repository of Redis:

::

    git clone git://github.com/antirez/redis.git

Repository of the Redis client (Python):

::

    git clone http://github.com/andymccurdy/redis-py.git

Repository of libbgpdump, grab the latest version:

::
    https://bitbucket.org/ripencc/bgpdump/downloads


Grab the latest (stable or unstable) version of Rgraph:

::
    
    http://www.rgraph.net/#download 


You may want the code of BGP Ranking... :)

Stable version:

::
    
    http://gitorious.org/bgp-ranking/bgp-ranking/archive-tarball/1.0
    https://github.com/Rafiot/bgp-ranking/tree/1.0

More or less stable version:

::
    
    https://github.com/Rafiot/bgp-ranking

Unstable version: 

::
    
    http://gitorious.org/bgp-ranking


FYI, I also use this programms:

::

    apt-get install screen ipython htop most iotop

Versions from trunk
===================

Our test environnement is based on Ubuntu 10.10. Except the following programms, we use the
versions of the repositories: 

* Redis : 2.2
* Redis-py : 2.2.3
* libbgpdump : 1.4.99.13
* Rgraph : 2011-01-28-stable


Third-party programms
=====================

By default, the system will search `libbgdump` and `rgraph` in :path:`bgpranking/thirdparty/`.
But if you want to change it, fell free to edit :file:`bgpranking/etc/bgp-ranking.conf`

Compilation and installation libbgpdump
---------------------------------------

Example with the version **1.4.99.13**:

::
    
    tar xjf 1.4.99.13.bz2 -C bgpranking/thirdparty/
    cd bgpranking/thirdparty/bgpdump
    ./bootstrap.sh
    make

Installation and compilation redis
----------------------------------

By default, BGP Ranking will search `redis-server` in :path:`~/redis/src`. If you want 
yo change it, take a look at :file:`bgp-ranking/scripts/common.source.sh`.

We assume you did it. 

::
    
    cd redis
    make

Installation rgraph
-------------------

::
    
    unzip RGraph_2011-01-28-stable.zip -d bgpranking/thirdparty/

Installation redis-py
---------------------

In the directory where you clone the repository:

::
    
    python setup.py install


Migration
=========

Stop everything :)
------------------

::
    
    cd scripts
    ./stop_ranking.sh
    ./stop_services.sh
    ./stop_redis.sh


Copy the redis dumps
--------------------

::
    
    scp redis/src/{dump-cache.rdb,dump.rdb} your.new.server:~/redis/src/


Monitoring
==========

Redis logs:

::
    
    tail -f ~/redis/src/*.log

BGP Ranking logs:

::
    
    tail -f /var/log/user.log

Website:

::
    
    python bgp-ranking/website/master.py

Processes:

::
    
    htop

Webserver
=========

Nginx
-----

::
    
    apt-get install nginx

.. put config

Cherrypy
--------

::
    
    python bgp-ranking/website/master.py


Your new BGP Ranking instance is now up and running, congratulations!


I would be glad to have your feedback!


