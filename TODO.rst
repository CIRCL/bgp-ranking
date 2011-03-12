
.. todolist::


*********
TODO List
*********

Bugfixes
========

* There is actually a problem with the slave database: it takes **to much** time.
  The proper fix it the move the temporary data from the global database to an other one,
  not synchronized with the slave.

Improvements
============

* API (telnet like ?) 
    - get the weight of each source
    - get the rank of a subnet/asn (by whatever you want)

New functionalities
===================

* Ranking by subnet can be improved: we divide the number of IPs found in a subnet by 
  the total of IPs announced by the AS. Like this, we just have to add the ranks of 
  each subnet of the AS to get the global rank of the AS.

  It might be interesting to compute the division of the number of IPs found in a subnet
  by the size of this subnet and to compare it to the global rank of the AS: if we have a 
  (big) difference, we can be sure that this particular subnet is better/worse than the 
  rest of the subnets announced by the AS. And investigate it further.

Not trivial
===========

* use python-whois as an external dep instead of the bundled version
  (http://gitorious.org/python-whois)
* read the code of Khanku (http://gitorious.org/~khanku/bgp-ranking/predictive-bgp-ranking/)
  ans find a way to handle this usage of the ranking system in the main trunk
* Extract interesting informations of the bview file, prepare to do a diff 
    egrep -w "^$|PREFIX:|ASPATH:"| awk -F' ' '{print $NF}' |  sed 's/^$/XXXXX/' | tr '\n' ' ' | sed 's/XXXXX/\n/g'| sed 's/^ //' | sort | uniq


Whishlist
=========

* Module which ping a list of URL known as malicious and insert the IP in the system.
