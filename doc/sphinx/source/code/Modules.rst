*******
Modules
*******

.. warning::
    Before instantiating the abstract module class, the modules must have a
    `date` and a `directory` variables.

    Take a look at the code is you want to kno more about it

.. automodule:: lib.modules.abstract_module
    :members:

Abuse.ch
========

The datasets are flat files.

.. _palevo: https://palevotracker.abuse.ch/
.. _spyeye: https://spyeyetracker.abuse.ch/
.. _zeus: https://zeustracker.abuse.ch/

There are several trackers provided by this website and each has a blocklist:
 - palevo_
 - spyeye_
 - zeus_

And there is also two ddos lists used to import the datasets of a ddos attack
on the spyeye or zeus trackers

The quality of all this lists is very high.

.. note::
    The format is always (almost) the same :), the classes of the modules just
    define the constraints needed by the system for each module.

.. automodule:: lib.modules.abuse_ch
    :members:

Shadowserver
============

The datasets are csv files.

.. _shadowserver: http://www.shadowserver.org/wiki/

The 3 lists provided by shadowserver_ are private and their quality is quite high.

.. automodule:: lib.modules.shadowserver
    :members:

Atlas
=====

The datasets are XML files

.. _atlas: https://atlas.arbor.net/

Active Threat Level Analysis System (atlas_) also provide private lists of a very good quality.

.. automodule:: lib.modules.atlas
    :members:

Abusix
======

The dataset is flat file which contains only one IP.

.. _abusix: http://abusix.org/

You can get more information on the abusix_ website.

DShield
=======

The datasets are flat files.

.. _DShield: http://www.dshield.org/

Dshield_ provide two lists: one contains the first worse IPs. This list is not updated very often.

The second one contains around I million IPs and is updated every day.

.. note::
    The quality of this lists is quite low.


sshbl
=====

The dataset is a flat file.

.. _sshbl: http://www.sshbl.org/

You can get more information on the sshbl_ website.


Malware Domain List
===================

The dataset is a flat file

.. _Malware Domain List: http://www.malwaredomainlist.com/

More information available on the `Malware Domain List`_ website.


URL Query
=========

The dataset is a flat file

.. _URL Query: http://urlquery.net/

More information available on the `URL Query`_ website.

Blocklist
=========

The dataset is a flat file

.. _Blocklist.de: http://www.blocklist.de

More information available on the `Blocklist.de`_ website.


Alienvault
==========

The dataset is a flat file

.. _Alienvault.com: http://www.alienvault.com/

More information available on the `Alienvault.com`_ website.

Shunlist
========

The dataset is a flat file

.. _Autoshun.org: http://www.autoshun.org/

More information available on the `Autoshun.org`_ website.
