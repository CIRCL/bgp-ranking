*********
Databases
*********


.. _db0:

Database 0
==========

Contains temporary information originating from the modules and 
some helper keys.

Helpers (keys)
--------------

.. data:: uid

	It is an integer, autoincremented.
	When a module has a new entry to insert in the system, it increments 
	the key and use its new value as a unique key to identify the parameters
	he wants to pass.

.. data:: uid_list

	It is a set of :data:`uid`. The set is used as a queue to know all the pending 
	entries to insert in the system. 

	.. tip::

		To know the number of entries to insert in the system, do: ::
	
			redis-cli -n 0 scard uid_list

		If the key does not exists (the command returns 0), there is no entries 
		to insert. 

.. data:: ris

	It is a set of IPs. The Ranking System needs the RIS Information of this IPs.

	.. note::

		the set may contains IPs that are already cached (see :ref:`db1_2`): they 
		will be automatically dropped by the fetching process and not fetched again
		until they are removed from the cache.

	.. tip::

		To know the number of RIS entries to fetch: 
		
			::

				redis-cli -n 0 scard ris

.. data:: whois

	same as :data:`ris` but for the Whois information


Temporary information
---------------------

All the information coming from the modules will have the following format: ::

	integer|string

.. data:: integer
	
	is an uid

.. data:: string

	can be one of the following: ::
	
		ip (mandatory)
		source (mandatory)
		timestamp
		infection
		raw
		times

	.. hint::

		if the timestamp does not exist in the dataset, it will be set to `today 
		at midnight` by the module 


.. note::
	If there is a few keys in the database but :data:`uid_list` does not exists, it is 
	probably that you stop the processing of the new entries when it was running.

	All the keys like 

		::
	
			integer|string 
	
	can be safely dropped, they will never be inserted anymore. 

.. _db1_2:

Databases 1 and 2
=================

This databases are completely volatile

`Database 1` 
	is a cache for the RIS Whois entries

`Database 2`
	is a cache for the Whois entries

.. note::

	All the entries are cached 24 hours

**Keys**
	IPs Addresses

**Values**
	(RIS) Whois entries

The two databases are on their own redis instance. 

.. _db3:

Database 3
==========

This database is also temporary: it is used by the ranking process to dump 
the routing information provided by the RIPE. 

First state
-----------

The database contains only sets: 

**Keys**

	::

		asn 

	the Autonomous System Number

**Values**
	the announced subnets

Second state
------------

During the ranking, the total number of IPs announced by an AS is computed and 
also saved in the database. 

**Keys**

	::

		asn|rankv4 or asn|rankv6

	asn is the Autonomous System Number

**Value**
	an integer, the number of IPs announced by the AS (in v4 or in v6)

.. note::
	The database is dropped when the ranking is computed.


.. _db4:

Database 4
==========

Contains information (url, ports, arguments to pass to the server) 
needed by the whois client to fetch the entries.

Also Contains a sort of hash to lookup the right whois server from an IP. 

You probably do not want to know anything more about it. (it needs a big refactoring)

.. warning::

	if this database if not initialized, the system will not be able 
	to do the RIS queries. 


.. _db5:

Database 5
==========

This database contains all the static information from the modules and the ASNs
but also a small amount of temporary information during the first state of the
processing of the new entries. 

.. _first:

First state
-----------

As we already know, the information from the modules comes in a raw format 
in :ref:`db0`. 
At this point, we always have an IP, a source and a timestamp (cf :data:`string`) .  

Sets
^^^^

1. The sources for a day: 

   ::

		YYYY-MM-DD|sources

.. tip::
	To know the sources available for a day, do: 

		::
		
			redis-cli smembers YYYY-MM-DD|sources

.. note::
	Every time you will read `source` in this document, it is the 
	name of a source from this set.

2. A temporary set of IPs for a day by source and by type waiting 
   to know their ASNs:

	::

		temp|YYYY-MM-DD|source|type

.. note:: 
	* source: the name of a source it comes from :ref:`db0`
	* type can be v4 or v6 

The values of this set are looks like: 

	::

		ip|timestamp

.. note::
	ip and timestamp comes from :ref:`db0`

3. a temporary set containing all the keys of the temporary set of IPs
   which are not linked with an ASN:

	::

		no_asn

.. note::
	Each IP is also inserted in the set :data:`ris` of :ref:`db0`.

Keys
^^^^

A key is inserted only if there is more information (an infection, an number 
of times, a raw stuff) provided by the dataset. It will looks like this: 

	::

		ip|timestamp|{infection,times,raw} 

And the value is the one given by the module (cf :data:`string`). 

Second state
------------

At this point, the information from the modules is in the database, we have 
to insert the rest of information in order to compute the ranking (RIS and Whois).

Ris
^^^

Using the keys generated during the :ref:`first` and the set `no_asn`, we get 
the RIS entries from :ref:`the first database <db1_2>`. 

Each ASN announce one or more subnets. A subnet is referenced by this two keys
in the database: 
	
	:: 

		asn|timestamp|ip_block (value: 0.0.0.0/0)
		asn|timestamp|description (value: Description)

There is also a set for each ASN which contains the subnets: 

**Key**
	asn

**Value**
	timestamp
		
.. note::
	There is only one occurence of each subnet for each ASN. Before creating
	a new entry, we check if the block and the description are already present.

.. note::
	if the ASN has been set to -1 (the IP is invalid, there is no information 
	on the RIS Whois server), we use a default AS object. 

.. _indexes:

Indexes
^^^^^^^

1. Index of subnets: 

   ::

		YYYY-MM-DD|source|index_asns_details (value: asn|timestamp)

	Usage:
		- get the list of subnets and compute the ranking
		- display the ranking by subnet

2. Index of ASN:

   ::

		YYYY-MM-DD|source|index_asns (value: asn)
	
	Usage:
		- get list of ASNs to rank
		- display the ranking by ASN


3. Index of IPs:

   ::

		asn|timestamp|YYYY-MM-DD|source (value: ip|timestamp)
	
	Usage:
		- ensure an IP is not already there
		- display the list of IPs


When it is fully populated, the integrity of the database in complete.

Whois 
^^^^^

The idea is simple: an user ask for a whois entry through the web interface, 
the IP is put in :data:`whois` of :ref:`db0`, fetched and put in :ref:`Database 2<db1_2>`. 
From :ref:`Database 2<db1_2>`, it is copied and put in :ref:`db5` as value of: 

	::

		ip|timestamp|whois

.. warning::
	The whois part is desactivated by default.

.. _db6:

Database 6
==========

Ranking
-------

Before
^^^^^^

The ranking can only be computed when the :ref:`db3` in fully populated. When it is 
finished, a new index is created: 

	::

		to_rank 

Which is set of

	::

		asn|timestamp|YYYY-MM-DD|source

It is an index of IPs (see :ref:`indexes`). By using this index, we compute a rank for 
each subnet and each ASN found for `YYYY-MM-DD`, by source. 

After
^^^^^

Subnets ranking
"""""""""""""""

	::
	
		asn|YYYY-MM-DD|source|{rankv4,rankv6}|details

It is a zset which contains the ranks of each subnet announced by the ASN 

**Value**
	timestamp of the subnet

**Score**
	rank 

This zset is actually not used but it will be usefull to generate a report 
for a ranking by subnet.

ASN ranking
"""""""""""

	::
	
		asn|YYYY-MM-DD|source|{rankv4,rankv6}

It is a string key.

**Value**
	sum of the ranks of the subnets announced by the ASN

The entry is created only of the rank is > 0.

Only one occurence of the rank is saved for a day.

Reports
-------

To display the reports on the website, we will need one key for each source and
a "global" key for the global report. They have this format: 

	::
	
		source|{rankv4,rankv6}


It is a zset.

**Value**

	::

		asn|YYYY-MM-DD|source|{rankv4,rankv6}
	
**Score**
	The rank of the ASN

The list of sources and of ASNs is found by using the :ref:`db5` and this keys 

	::

		YYYY-MM-DD|sources 
		YYYY-MM-DD|source|index_asns 

It is possible to change the day and get the report of an other one very easily :) 
