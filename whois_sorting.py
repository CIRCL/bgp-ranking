import redis
from whois.whois_fetcher import get_server_by_query
import time

"""
A sorting processes which sort the queries by dest whois server 
"""


redis_keys = ['ris', 'whois']
# Temporary redis database, used to push ris and whois requests
temp_reris_db = 0
# Cqche redis database, used to set ris and whois responses
cache_reris_db = 1

process_sleep = 5

temp_db = redis.Redis(db=temp_reris_db)
key = redis_keys[1]
while 1:
    print('blocs to whois: ' + str(temp_db.llen(key)))
    bloc = temp_db.pop(key)
    if not bloc:
        time.sleep(process_sleep)
        continue
    server = get_server_by_query(bloc)
    if not server:
        print ("error, no server found for this block : " + bloc)
        temp_db.push(key, block)
        continue
    temp_db.push(server.whois,  bloc)
