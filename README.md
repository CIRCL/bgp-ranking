# BGP AS / ISP Security Ranking

For an Internet Service Provider, AS numbers are a logical representation of
the other ISP peering or communicating with his autonomous system. ISP customers
are using the capacity of the Internet Service Provider to reach Internet
services over other AS. Some of those communications can be malicious (e.g. due
to malware activities on an end-user equipments) and hosted at specific AS location.

In order to provide an improved security view on those AS numbers, a trust ranking
scheme will be implemented based on existing dataset of compromised systems,
malware C&C IP and existing datasets of the ISPs.

The official website of the project is: https://github.com/CIRCL/bgp-ranking/

There is a public BGP Ranking at http://bgpranking.circl.lu/

BGP Ranking is free software licensed under the GNU Affero General Public License

BGP Ranking is a software to rank AS numbers based on malicious activities.


# Data access

## Database 5 (contains all raw data):

```python
    <YYYY-MM-DD>|sources -> set(sources)
    <YYYY-MM-DD>|<source>|asns -> set(asns)
    <YYYY-MM-DD>|<source>|asn_details -> set(<asn>|<ipblock>)
    <asn>|<ipblock>|<YYYY-MM-DD>|<source> -> set(<ip>|<datetime_isoformat>)

    <asn> -> set(ipblock) # The bloc can be ipv4 or ipv6
                          # WARNING: some of the entries are timestamp, this is
                          # a bug in old data and should be discarded
    <asn>|<ipblock> -> hash(<datetime_isoformat>: <verbose_description_from_riswhois>)
```

## Database 6 (contains rankings):

```python
    <YYYY-MM-DD>|amount_asns -> value(nb_asns_day) # from all the ASNs known by RIPE for a day
    <asn>|<YYYY-MM-DD>|<source>|rankv4 -> value(rank)
    <asn>|<YYYY-MM-DD>|<source>|rankv4|details -> zset((<ipblock>, <computed rank>) )
                            # WARNING: some of the entries are timestamp, this is
                            # a bug in old data and should be discarded
    <asn>|<YYYY-MM-DD>|<source>|rankv6 -> value(rank) # Not used
    <asn>|<YYYY-MM-DD>|<source>|rankv6|details -> zset((<ipblock>, <computed rank>) ) # Not used
                            # WARNING: some of the entries are timestamp, this is
                            # a bug in old data and should be discarded

    <asn>|<YYYY-MM-DD>|clean_set

```

