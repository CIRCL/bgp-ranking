from model import *

drop_all()
create_all()

# 'address' : [pre_options, post_options]
options = {'whois.nic.ad.jp' :  ['', ' /e ']}



def insert(assignations): 
    for ip,url in assignations:
        if not re.findall('\.',url):
            url = 'whois.' + url + '.net'
        assignations = Assignations(block=unicode(ip), whois=unicode(url))
        whois_options = options.get(url,  None)
        if whois_options:
            assignations.pre_options = whois_options[0]
            assignations.post_options = whois_options[1]

f = open('whois/ip_del_list').read()
assignations = re.findall('[\n]*([^#][\d./]*)\t([^#][\d\w.]*)\s*',f)
insert(assignations)

f = open('whois/ip6_del_list').read()
assignations = re.findall('[\n]*([^#][\w\d:/]*)\t([^#][\d\w.]*)\s*',f)
insert(assignations)

session.commit()


