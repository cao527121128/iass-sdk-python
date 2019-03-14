#!/usr/bin/env python
#coding:utf-8
'''
Created on 2019-03-05

@author: yunify
'''

import qingcloud.iaas
import threading
import time
from optparse import OptionParser
import sys
import os

# global
zone_id = None
conn=None
access_key_id = None
secret_access_key = None
host = None
port = None
protocol = None
vxnet_id = None
g_cache_id = None





def connect_iaas(zone_id, access_key_id, secret_access_key, host,port,protocol):
    print("connect_iaas")
    print("starting connect_to_zone ...")
    global conn
    conn = qingcloud.iaas.connect_to_zone(
        zone_id,
        access_key_id,
        secret_access_key,
        host,
        port,
        protocol
    )
    if conn < 0:
        print("connect_to_zone fail")
        exit(-1)
    print("conn==%s" %(conn))

def create_cache(vxnet_id):
    print("子线程启动")
    print("create_cache")
    global conn
    global g_cache_id

    ret = conn.create_cache(
        # vxnet='vxnet-glp08w9',
        vxnet=vxnet_id,
        cache_size=1,
        cache_type='memcached1.4.13',
        cache_name='vdi-portal-memcached'
    )
    if ret < 0:
        print("create_cache fail")
        exit(-1)
    print("ret==%s" % (ret))

    g_cache_id = ret.get("cache_id")
    print("g_cache_id=%s" % (g_cache_id))

    status = "pending"
    while status != "active":
        time.sleep(1)
        status = get_cache_status()
    print("子线程结束")




def get_cache_status():
    print("get_cache_status")
    global conn
    global g_cache_id
    ret = conn.describe_caches(caches=[g_cache_id],verbose=1)
    if ret < 0:
        print("describe_caches fail")
        exit(-1)
    # print(ret)
    matched_cache = ret['cache_set']
    print("matched_cache==%s"%(matched_cache))

    print("************************************")

    wanted_cache = matched_cache[0]
    print("wanted_cache==%s" % (wanted_cache))

    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    status = wanted_cache.get('status')
    print("status=%s" % (status))
    return status



def get_memcached_ip():
    print("get_memcached_ip")
    global conn
    global g_cache_id
    ret = conn.describe_caches(caches=[g_cache_id], verbose=1)
    if ret < 0:
        print("describe_caches fail")
        exit(-1)
    # print(ret)
    matched_cache = ret['cache_set']
    print("matched_cache==%s"%(matched_cache))

    print("************************************")
    wanted_cache = matched_cache[0]
    print("wanted_cache==%s" % (wanted_cache))

    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    nodes = wanted_cache['nodes']
    print("nodes==%s"%(nodes))


    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    memcached_ip = nodes[0].get('private_ip')
    print("memcached_ip=%s" % (memcached_ip))
    return memcached_ip

def get_vxnet_id():
    print("get_vxnet_id")
    global conn
    #查看基础网络vxnet_id
    ret = conn.describe_vxnets(limit=1, vxnet_type=2)
    if ret < 0:
        print("describe_vxnets fail")
        exit(-1)
    matched_vxnet = ret['vxnet_set']
    print("matched_vxnet==%s" % (matched_vxnet))

    print("************************************")

    wanted_vxnet = matched_vxnet[0]
    print("wanted_vxnet==%s" % (wanted_vxnet))

    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    vxnet_id = wanted_vxnet.get('vxnet_id')
    print("vxnet_id=%s" % (vxnet_id))
    return vxnet_id


if __name__ == "__main__":
    print("主线程启动")

    #解析参数
    opt_parser = OptionParser()
    opt_parser.add_option("-z", "--zone_id", action="store", type="string", \
                          dest="zone_id", help='zone id', default="")
    opt_parser.add_option("-a", "--access_key_id", action="store", type="string", \
                          dest="access_key_id", help='access key id', default="")

    opt_parser.add_option("-s", "--secret_access_key", action="store", type="string", \
                          dest="secret_access_key", help='secret access key', default="")

    opt_parser.add_option("-H", "--host", action="store", type="string", \
                          dest="host", help='host', default="")

    opt_parser.add_option("-p", "--port", action="store", type="string", \
                          dest="port", help='port', default="")

    opt_parser.add_option("-P", "--protocol", action="store", type="string", \
                          dest="protocol", help='protocol', default="")
    opt_parser.add_option("-v", "--vxnet_id", action="store", type="string", \
                          dest="vxnet_id", help='vxnet id', default="")

    (options, _) = opt_parser.parse_args(sys.argv)
    global access_key_id

    zone_id = options.zone_id
    access_key_id = options.access_key_id
    secret_access_key = options.secret_access_key
    host = options.host
    port = options.port
    protocol = options.protocol
    vxnet_id = options.vxnet_id
    print("zone_id:%s" % (zone_id))
    print("access_key_id:%s" % (access_key_id))
    print("secret_access_key:%s" % (secret_access_key))
    print("host:%s" % (host))
    print("port:%s" % (port))
    print("protocol:%s" % (protocol))
    print("vxnet_id:%s" % (vxnet_id))


    #连接iaas后台
    connect_iaas(zone_id, access_key_id, secret_access_key, host,port,protocol)

    #获取vxnet_id
    if vxnet_id:
        print("vxnet_id==%s" %(vxnet_id))
    else:
        vxnet_id = get_vxnet_id()
        print("vxnet_id==%s" % (vxnet_id))

    #创建子线程执行创建数据库的操作
    t = threading.Thread(target=create_cache,args=(vxnet_id,))
    t.start()
    t.join()


    #memcached_ip 写入文件
    memcached_ip_conf = "/tmp/memcached_ip_conf"
    ret = get_memcached_ip()
    with open(memcached_ip_conf, "w+") as f1:
        f1.write("MEMCACHED_ADDRESS %s" %(ret))

    print("主线程结束")

