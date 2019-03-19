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

    user_id=get_user_id()
    if not user_id:
        print("user_id is null")
        exit(-1)

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


def get_instance_vxnet_id(resource_id):
    print("get_instance_vxnet_id")
    global conn

    #查看主机的基础网络vxnet_id
    ret = conn.describe_instances(instances=[resource_id],verbose=1)
    if ret < 0:
        print("describe_vxnets fail")
        exit(-1)
    # print("ret=%s" %(ret))
    instance_set = ret['instance_set']
    # print("instance_set==%s" % (instance_set))

    print("************************************")
    #
    wanted_instance = instance_set[0]
    print("wanted_instance==%s" % (wanted_instance))

    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    vxnets = wanted_instance.get("vxnets")
    print("vxnets=%s" %(vxnets))

    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    vxnet_id = vxnets[0].get("vxnet_id")
    print("vxnet_id=%s" %(vxnet_id))
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

    opt_parser.add_option("-r", "--resource_id", action="store", type="string", \
                          dest="resource_id", help='resource id', default="")


    (options, _) = opt_parser.parse_args(sys.argv)
    zone_id = options.zone_id
    access_key_id = options.access_key_id
    secret_access_key = options.secret_access_key
    host = options.host
    port = options.port
    protocol = options.protocol
    resource_id = options.resource_id
    print("zone_id:%s" % (zone_id))
    print("access_key_id:%s" % (access_key_id))
    print("secret_access_key:%s" % (secret_access_key))
    print("host:%s" % (host))
    print("port:%s" % (port))
    print("protocol:%s" % (protocol))
    print("resource_id:%s" % (resource_id))


    #连接iaas后台
    connect_iaas(zone_id, access_key_id, secret_access_key, host,port,protocol)

    instance_vxnet_id = get_instance_vxnet_id(resource_id)
    print("instance_vxnet_id=%s" %(instance_vxnet_id))

    # instance_vxnet_id 写入文件
    instance_vxnet_id_conf = "/tmp/instance_vxnet_id_conf"
    with open(instance_vxnet_id_conf, "w+") as f1:
        f1.write("INSTANCE_VXNET_ID %s" % (instance_vxnet_id))


    print("主线程结束")

