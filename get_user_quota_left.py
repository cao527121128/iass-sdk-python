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
resource_id = None



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

    # user_id=get_user_id()
    # if not user_id:
    #     print("user_id is null")
    #     exit(-1)

def get_user_id():
    print("get_user_id")
    global conn
    global access_key_id
    #查看access_keys详情
    ret = conn.describe_access_keys(access_keys=[access_key_id])
    if ret < 0:
        print("describe_access_keys fail")
        exit(-1)
    matched_access_key = ret['access_key_set']
    print("matched_access_key==%s" % (matched_access_key))

    print("************************************")

    wanted_access_key = matched_access_key[0]
    print("wanted_access_key==%s" % (wanted_access_key))

    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    user_id = wanted_access_key.get('owner')
    print("user_id=%s" % (user_id))
    return user_id


def get_user_quota_left(resource_type,user_id):
    print("get_user_quota_left")
    global conn

    #查看用户配额剩余
    ret = conn.get_quota_left(resource_types=[resource_type], owner=user_id)
    if ret < 0:
        print("get_quota_left fail")
        exit(-1)
    print("ret=%s" %(ret))
    print("************************************")
    quota_left_set = ret.get("quota_left_set")
    print("quota_left_set==%s" % (quota_left_set))

    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    resource_type_left = quota_left_set[0].get("left")
    print("resource_type_left==%d" % (resource_type_left))
    return resource_type_left




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



    (options, _) = opt_parser.parse_args(sys.argv)
    zone_id = options.zone_id
    access_key_id = options.access_key_id
    secret_access_key = options.secret_access_key
    host = options.host
    port = options.port
    protocol = options.protocol
    print("zone_id:%s" % (zone_id))
    print("access_key_id:%s" % (access_key_id))
    print("secret_access_key:%s" % (secret_access_key))
    print("host:%s" % (host))
    print("port:%s" % (port))
    print("protocol:%s" % (protocol))



    #连接iaas后台
    connect_iaas(zone_id, access_key_id, secret_access_key, host,port,protocol)

    user_id = get_user_id()
    if not user_id:
        print("user_id is null")
        exit(-1)

    rdb_quota_left = get_user_quota_left('rdb',user_id)
    print("rdb_quota_left=%d" %(rdb_quota_left))

    cache_quota_left = get_user_quota_left('cache', user_id)
    print("cache_quota_left=%d" % (cache_quota_left))

    instance_quota_left = get_user_quota_left('instance', user_id)
    print("instance_quota_left=%d" % (instance_quota_left))

    loadbalancer_quota_left = get_user_quota_left('loadbalancer', user_id)
    print("loadbalancer_quota_left=%d" % (loadbalancer_quota_left))

    s2_server_quota_left = get_user_quota_left('s2_server', user_id)
    print("s2_server_quota_left=%d" % (s2_server_quota_left))

    # rdb_quota_left 写入文件
    rdb_quota_left_conf = "/tmp/rdb_quota_left_conf"
    with open(rdb_quota_left_conf, "w+") as f1:
        f1.write("RDB_QUOTA_LEFT %d" % (rdb_quota_left))

    # cache_quota_left 写入文件
    cache_quota_left_conf = "/tmp/cache_quota_left_conf"
    with open(cache_quota_left_conf, "w+") as f1:
        f1.write("CACHE_QUOTA_LEFT %d" % (cache_quota_left))

    # instance_quota_left 写入文件
    instance_quota_left_conf = "/tmp/instance_quota_left_conf"
    with open(instance_quota_left_conf, "w+") as f1:
        f1.write("INSTANCE_QUOTA_LEFT %d" % (instance_quota_left))

    # loadbalancer_quota_left 写入文件
    loadbalancer_quota_left_conf = "/tmp/loadbalancer_quota_left_conf"
    with open(loadbalancer_quota_left_conf, "w+") as f1:
        f1.write("LOADBALANCER_QUOTA_LEFT %d" % (loadbalancer_quota_left))

    # s2_server_quota_left 写入文件
    s2_server_quota_left_conf = "/tmp/s2_server_quota_left_conf"
    with open(s2_server_quota_left_conf, "w+") as f1:
        f1.write("S2_SERVER_QUOTA_LEFT %d" % (s2_server_quota_left))

    print("主线程结束")

