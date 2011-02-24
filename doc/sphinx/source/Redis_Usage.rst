***********
Redis Usage 
***********

Introduction
============

This document gives you some basics information on the usage of Redis in the project.

Environment
===========

Redis 2.2
redis-py 2.2.2

**Debian**:
    64bit
    2Go RAM
    Intel(R) Core(TM)2 Duo CPU T5870  @ 2.00GHz

**Gentoo**: 
    64bit
    4Go RAM 
    Intel(R) Core(TM)2 Duo CPU T9300  @ 2.50GHz

**Ubuntu**: 
    32bit
    8Go RAM
    Intel(R) Xeon(R) CPU 5150  @ 2.66GHz (QuadCore)


Context
=======

Project 1
---------

`BGP-Ranking`, many processes (~50), see in .presentations if you want more 
information. Tested on Ubuntu and a little bit on gentoo.

**Problem**: 
	All the processes are doing a lot of queries at the same time on the 
	same database which just die. 
    
**Idea**: 
	We have only one redis process, the rest of the project is multiprocessed, 
	why not redis ? 

Project 2
---------

Small project, multiprocessed, use many zsets and do a lot of queries. 
Tested on Debian and a little bit on gentoo

**Problem**: 
	there is 15 Milions lines to parse, 50 lines/second is not enough 

**Idea**: 
	Using cProfile, I was able to see that around 60% of the time, 
	the process was opening a connection to redis, sending the command, 
	receving and parsing the response. It is not possible to do UDP but using 
	transactions should automatically reduce the amount of connection to redis...

Multiples redis instances
=========================

**Problem**: 
	we cannot ensure that the slave database contains the 
	same information as the master: Redis only has `slave` modus, not a `cluster`.

There is two possible usages: 

* **a completly standalone instance**: instead of having all the data in a 
  single instance, it is splitted between two (or more). In our system there 
  is only one self alone instance and it contains the (RIS) Whois entries: 
  his information is not saved on the disk

* **a slave**: contains all the keys of the master (or most of them), 
  used in read only mode (it is not a cluster, the changes in the slave are 
  not pushed back in the master). It is used to get information from the redis
  server without slowing down the master which revieve the write commands.
  In our system there is only one slave instance and it is used by web interface:
  it is not very important to have always the latest version of the database in
  the web interface. 


Transations - Single query
==========================

**mget**, **mset**, **delete**, **setex**: all this queries allow you to do many 
queries at the same time, in a single connection. 

**Example of Transaction** (using redis-py): 

	::

		p = redis.pipeline(False)
		p.command
		p.command
		p.command
		...
		p.execute()

**False** means "not in transactional mode" aka "I do not care what the 
commands returns" and it is faster (because we do not parse the result).

.. note:: 
	a pipeline in transactional mode (the default) is faster than no 
	pipeline at all but if you have a pipeline with only write commands, 
	you do not care what the commands return (usually)
