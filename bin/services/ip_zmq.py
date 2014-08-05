#!/usr/bin/env python2.7

import ConfigParser
import redis
import zmq

ip_publisher_channel = 'ips'
zmq_port = 5556

zmq_socket = None
pubsub = None


def __prepare():
    global pubsub
    global zmq_socket

    config = ConfigParser.RawConfigParser()
    config_file = "/etc/bgpranking/bgpranking.conf"
    config.read(config_file)

    temp_db = redis.Redis(port=int(config.get('redis', 'port_cache')),
                          db=int(config.get('redis', 'temp')))
    pubsub = temp_db.pubsub()
    pubsub.psubscribe(ip_publisher_channel)
    context = zmq.Context()
    zmq_socket = context.socket(zmq.PUB)
    zmq_socket.bind("tcp://*:%s" % zmq_port)


def run():
    if pubsub is None:
        __prepare()

    for msg in pubsub.listen():
        if msg['type'] == 'pmessage':
            zmq_socket.send(msg['data'])


if __name__ == '__main__':
    run()
