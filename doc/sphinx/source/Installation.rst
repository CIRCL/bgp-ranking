************
Installation
************


Dependencies of BGP Ranking
===========================

Dependencies available in the ubuntu repositories (Ubuntu 11.04):

    ::
    
        $ apt-get install python-dateutil python-feedparser python-cherrypy3 python-cheetah python-ipy

To use the JSON interface (v1.1.4), you need at least Cherrypy 3.2:
    
    ::

        sudo easy_install -U cherrypy

Dependencies of libbgpdump + gcc (compilation :) ) + unzip (rgraph is zipped):

    ::
        
        $ apt-get install gcc autoconf zlib1g-dev libbz2-dev unzip


Repository of Redis. You can safely get the latest stable version:

    ::

        $ git clone git://github.com/antirez/redis.git

Repository of the Redis client (Python). You can safely get the latest stable version:

    ::

        $ git clone http://github.com/andymccurdy/redis-py.git

.. _Repository of libbgpdump: https://bitbucket.org/ripencc/bgpdump/downloads

`Repository of libbgpdump`_, grab the latest version.

.. _Website of Rgraph: http://www.rgraph.net/#download 

`Website of Rgraph`_, grab the latest (stable) version.

.. _github: ttps://github.com/Rafiot/bgp-ranking/tree/stable

Optional dependencies
---------------------

.. _hiredis: https://github.com/pietern/hiredis-py

`hiredis`_ may improve the performances of the system. To use it, you have to do the following: 

1. Install the dependencies

    ::
        
        $ apt-get install python-dev

2. Install hiredis

    ::
        
        $ easy_install hiredis


To be able to post on twitter and identi.ca:
    
    ::
        
        $ apt-get install python-oauth2 python-twitter

BGP Ranking
===========

You can get the latest stable version of the code from `gitorious`_ or 
from `github`_. Now the latest stable version is 1.1. Always ensure you 
are using the latest stable version.


You can also download a testing from the github repository: 

    ::
        
        git clone git://github.com/Rafiot/bgp-ranking.git

And an unstable version from gitorious: 

    ::
        
        git clone http://git.gitorious.org/bgp-ranking/bgp-ranking.git

FYI, I also use this programms for the monitoring tasks:

    ::
        
        $ apt-get install screen ipython htop most iotop

Versions from trunk
===================

Our test environnement is based on Ubuntu 10.10. Except the following programms, we use the
versions of the repositories: 

* Redis : 2.4
* Redis-py : 2.4.*
* libbgpdump : 1.4.99.13
* Rgraph : Latest stable


Third-party programms
=====================

By default, the system will search `libbgdump` and `rgraph` in :file:`bgpranking/thirdparty/`.
But if you want to change it, fell free to edit :file:`bgpranking/etc/bgp-ranking.conf`

Compilation and installation libbgpdump
---------------------------------------

Example with the version **1.4.99.13**:

::
    
    $ tar xjf 1.4.99.13.bz2 -C bgpranking/thirdparty/
    $ cd bgpranking/thirdparty/bgpdump
    $ ./bootstrap.sh
    $ make

Installation and compilation redis
----------------------------------

By default, BGP Ranking will search `redis-server` in :file:`~/redis/src`. If you want 
yo change it, take a look at :file:`bgp-ranking/scripts/common.source.sh`.

We assume you did it. 

::
    
    $ cd redis
    $ make

Installation rgraph
-------------------

::
    
    $ unzip RGraph_2011-01-28-stable.zip -d bgpranking/thirdparty/

Installation redis-py
---------------------

In the directory where you clone the repository:

::
    
    $ python setup.py install


Migration
=========

Stop everything :)
------------------

::
    
    $ cd scripts
    $ ./stop_ranking.sh
    $ ./stop_services.sh
    $ ./stop_redis.sh


Copy the redis dumps
--------------------

::
    
    $ scp redis/src/{dump-cache.rdb,dump.rdb} your.new.server:~/redis/src/


Fresh new install
=================

If you have a completely fresh new install, the first thing to do is to populate the
database 4. It contains the information needed by the whois clients.

::
    
    $ lib/db_init/init_assignations_redis.py

Start the system
================

::
    
    $ cd scripts
    $ ./start_redis.sh
    $ ./start_services.sh
    $ ./start_ranking.sh

Monitoring
==========

Redis logs:

::
    
    $ tail -f ~/redis/src/*.log

BGP Ranking logs:

::
    
    $ tail -f /var/log/bgpranking.log

Website:

::
    
    $ python bgp-ranking/website/master.py

Processes:

::
    
    $ htop

Reverse proxy and Webserver
===========================

Nginx (reverse proxy)
---------------------

::
    
    $ apt-get install nginx

Configuration:

::
    
    server {

        listen   80; ## listen for ipv4
        listen   [::]:80 default ipv6only=on; ## listen for ipv6

        server_name  localhost;

        access_log  /var/log/nginx/localhost.access.log;

        location / {
            proxy_pass        http://localhost:8080;
            proxy_set_header  X-Real-IP  $remote_addr;
        }
    }

.. put config

Cherrypy (webserver)
--------------------

::
    
    $ python bgp-ranking/website/master.py


Your new BGP Ranking instance is now up and running, congratulations!


I would be glad to have your feedback!



