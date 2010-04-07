from model import *

drop_all()
create_all()


def insert(assignations): 
    for ip,url in assignations:
        if not re.findall('\.',url):
            url = 'whois.' + url + '.net'
        Assignations(block=unicode(ip), whois=unicode(url))

f = open('whois/ip_del_list').read()
assignations = re.findall('[\n]*([^#][\d./]*)\t([^#][\d\w.]*)\s*',f)
insert(assignations)

f = open('whois/ip6_del_list').read()
assignations = re.findall('[\n]*([^#][\w\d:/]*)\t([^#][\d\w.]*)\s*',f)
insert(assignations)

session.commit()


