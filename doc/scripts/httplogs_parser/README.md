
========================== !!!!WARNING!!!! ============================

__NEVER__ run this code on a server with a running BGP Ranking instance!

It uses a redis db as backend to sorts the informations from the logs.
If you run it and there is a BGP Ranking instance at the same time on the 
server, you will likely kill it. 

=======================================================================

## Usage

1. Open and read bgpranking_logs_parser.py :)
2. Put your logfile(s) in logs/
3. Change the name of the logfile in the fonction "readlogs"
4. Run the script

If you take a look at the other functions, you might find some other interesting stuff


## Credits

This script draws inspiration and code from:

* https://github.com/lethain/apache-log-parser (Mostly)
* http://effbot.org/zone/wide-finder.htm
* http://www.python.org/dev/peps/pep-0265/
