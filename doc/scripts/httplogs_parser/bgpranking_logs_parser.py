import re
import redis
import glob
import os
from subprocess import Popen, PIPE


class HTTPParser(object):
    
    def __init__(self):
        self.blacklist_uri = ".*(RGraph|robots.txt|master.css|favicon).*"
        self.blacklist_agents = ".*(Googlebot|YandexBot|Wget).*"
        self.useful_entries = []
        self.asn_regex = ".*asn=([\d]*).*"


    def parse(self, filename):
        'Return tuple of dictionaries containing file data.'
        def make_entry(x):
            return { 
                'server_ip':x.group('ip'),
                'uri':x.group('uri'),
                'time':x.group('time'),
                'status_code':x.group('status_code'),
                'referral':x.group('referral'),
                'agent':x.group('agent'),
                }
        log_re = '(?P<ip>[.:0-9a-fA-F]+) - - \[(?P<time>.*?)\] "GET (?P<uri>.*?) HTTP/1.\d" (?P<status_code>\d+) \d+ "(?P<referral>.*?)" "(?P<agent>.*?)"'
        search = re.compile(log_re).search
        matches = (search(line) for line in file(filename))
        return (make_entry(x) for x in matches if x)



    def read_logs(self):
        logs = glob.glob( os.path.join("logs", 'localhost.access.log') )
        for log in logs:
            parsed_file = self.parse(log)
            for entry in parsed_file:
                if entry["referral"] != "http://localhost/" and len(re.findall(self.blacklist_uri, entry["uri"])) == 0  and len(re.findall(self.blacklist_agents, entry["agent"])) == 0 :
                   self.useful_entries.append(entry)

    def uri_by_origin_ip(self):
        """
            "ips" -> all ips
            ip -> all uris
        """
        r = redis.Redis(db = 0)
        for entry in self.useful_entries:
            r.sadd("ips", entry["server_ip"])
            r.sadd(entry["server_ip"], entry["uri"])
            asn = re.findall(self.asn_regex, entry["uri"])
            if len(asn) > 0 and len(asn[0]) >0:
                r.sadd(entry["server_ip"] + "short", asn[0])
        ips = r.smembers("ips")
        for ip in ips:
            r.zadd("order_ips", **{ip: r.scard(ip)})

    def agent_by_origin_ip(self):
        """
            "ips" -> all ips
            ip -> all agents
        """
        r = redis.Redis(db=0)
        for entry in self.useful_entries:
            r.sadd("ips", entry["server_ip"])
            r.sadd(entry["server_ip"], entry["agent"])
        ips = r.smembers("ips")
        for ip in ips:
            r.zadd("order_ips", **{ip: r.scard(ip)})
        

    def origin_ip_by_asn(self):
        """
            "asns" -> all asns
            asn -> all ips
        """
        r = redis.Redis(db = 0)
        asn_regex = ".*asn=([\d]*).*"
        for entry in self.useful_entries:
            asn = re.findall(asn_regex, entry["uri"])
            if len(asn) > 0 and len(asn[0]) >0:
                r.sadd("asns", asn[0])
                r.sadd(asn[0], entry["server_ip"])
        asns = r.smembers("asns")
        for asn in asns:
            r.zadd("order_asns", **{asn: r.scard(asn)})

    def ip_by_agent(self):
        """
            "agents" -> all agents
            agent -> all ips
        """
        r = redis.Redis(db = 0)
        for entry in self.useful_entries:
            r.sadd("agents", entry["agent"])
            r.sadd(entry["agent"], entry["server_ip"])
        agents = r.smembers("agents")
        for agent in agents:
            r.zadd("order_agents", **{agent: r.scard(agent)})

    def ip_by_origin(self):
        """
            "origins" -> all origins
            origin -> all ips
        """
        r = redis.Redis(db = 0)
        for entry in self.useful_entries:
            if entry["referral"] is not "-" and "bgpranking.circl.lu" not in entry["referral"]:
                r.sadd("origins", entry["referral"])
                r.sadd(entry["referral"], entry["server_ip"])
        origins = r.smembers("origins")
        for origin in origins:
            r.zadd("order_origins", **{origin: r.scard(origin)})

    def ip_queries(self):
        """
            "ips" -> all ips
            "ip_queries"    -> ip_asn  top = one IP did many queries on one ASN
            ip              -> asns    top = the AS which interests a lot this ip
            "queries"       -> asn     top = most loved asn
            asn             -> ips     all ips which did queries on this asn
        """
        r = redis.Redis(db = 0)
        asn_regex = ".*asn=([\d]*).*"
        for entry in self.useful_entries:
            asn = re.findall(asn_regex, entry["uri"])
            if len(asn) > 0 and len(asn[0]) >0:
                r.sadd("ips", entry["server_ip"])
                r.sadd("asns", asn[0])
                r.sadd(asn[0], entry["server_ip"])
                r.zincrby("ip_queries", entry["server_ip"] + "_" + asn[0])
                r.zincrby(entry["server_ip"], asn[0])
                r.zincrby("queries", asn[0])

    def top_asn_ips_info(self, limit = 20):
        """
            Display the 20 most active IPs.
        """
        r = redis.Redis(db = 0)
        ip_queries = r.zrevrange("ip_queries", 0, limit, withscores = True)
        ips = []
        asns = []
        scores = []
        for ip_query, score in ip_queries:
            ip, asn = ip_query.split("_")
            ips.append(ip)
            asns.append(asn)
            scores.append(score)
        infos = self.check_ips("\n".join(ips) + "\n")
        i = 0
        j = 0
        for ip in ips:
            asn = asns[i]
            score = scores[i]
            print "{ip} - {query} - {score}".format(ip = ip, query = asn, score = score)
            if ":" not in ip:
                print "          -> {info}".format(info = infos[j])
                j += 1
            i += 1

    def check_ips(self, ips):
        p = Popen(["/usr/bin/perl", "iplookup/iporigin.pl"], stdout=PIPE, stdin=PIPE, stderr = open(os.devnull, 'w'))
        stdout = p.communicate(input=ips)[0].split("\r\n")
        return stdout

    def top_ips_info(self, limit = 20):
        r = redis.Redis(db = 0)
        ips_temp = r.zrevrange("order_ips", 0, limit, withscores = True)
        ips = []
        scores = []
        for ip, score in ips_temp:
            ips.append(ip)
            scores.append(score)
        infos = self.check_ips("\n".join(ips) + "\n")
        i = 0
        j = 0
        for ip in ips:
            score = scores[i]
            queries = r.smembers(ip + "short")
            print "{ip} - {score}".format(ip = ip, score = score)
            if queries is not None and len(queries) > 0 :
                q = ", ".join(queries)
                print "          -> {query}".format(query = q)
            if ":" not in ip:
                print "          -> {info}".format(info = infos[j])
                j += 1
            i += 1



if __name__ == '__main__':

    parser = HTTPParser()
    parser.read_logs()
    
    # One ASN interests multiple IPs
#    parser.origin_ip_by_asn()
    
    # Multiple agents for one single ip ?!
#    parser.agent_by_origin_ip()
    
    # All the IPs with a single agent id
#    parser.ip_by_agent()

    # Where are they from ?
#    parser.ip_by_origin()
 
    # Very active IPs on a particular AS
#    parser.ip_queries()
#    parser.top_asn_ips_info()

    # Very active IPs
    parser.uri_by_origin_ip()
    parser.top_ips_info()


