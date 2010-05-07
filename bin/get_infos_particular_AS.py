import sys
sys.path.insert(0, sys.path[0] + '/..')

from utils.models import *

from whois_parse.whois_parsers import *

def usage():
    print "get_infos_particular_AS.py asn"
    exit (1)

if len(sys.argv) < 2:
    usage()

asn = sys.argv[1]


descs = IPsDescriptions.query.filter(IPsDescriptions.asn.has(asn_asn=asn)).order_by(IPsDescriptions.list_date)

for desc in descs:
#    print desc.whois_address, desc.whois
    w = Whois(desc.whois, desc.whois_address)
    if w.netname:
        print('[' + str(desc.list_date) + ']\t"' + desc.list_name + '"\t\t' + desc.ip_ip + '\t' + w.netname + '\t\t-> ' + desc.infection)
    else:
        print('[' + str(desc.list_date) + ']\t"' + desc.list_name + '"\t\t' + desc.ip_ip + '\t-> ' + desc.infection)

ips_counter = {}
for desc in descs:
    if not ips_counter.get(desc.ip.ip, None):
        w = Whois(desc.whois, desc.whois_address)
        ips_counter[desc.ip.ip] = [IPsDescriptions.query.filter_by(ip_ip=unicode(desc.ip.ip)).count(), w.netname, desc.infection]

#for ip, count in ips_counter.iteritems():
#    print(ip + ':\t' + str(count))


#print('By IP (ips are strings in the db...)')
#by_ip = ips_counter.items()
#by_ip.sort()
#for ip, count in by_ip:
#    print(ip + ':\t' + str(count))

print('By occurrences')
by_count  = ips_counter.items()
by_count.sort(key=lambda x: x[1][0])
for ip, infos in by_count:
    print(ip + ':\t' + str(infos))
