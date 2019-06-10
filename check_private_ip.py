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
user_id = None
g_private_ips_available_flag = False
g_private_ips_status = None





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

    # check ret_code
    print("ret==%s" % (ret))
    ret_code = ret.get("ret_code")
    print("ret_code==%s" % (ret_code))
    if ret_code != 0:
        print("describe_access_keys failed")
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


def check_private_ip(private_ips):
    print("子线程启动")
    print("check_private_ip")
    global conn
    global g_private_ips_available_flag

    user_id = get_user_id()
    print("user_id==%s" %(user_id))
    print("private_ips==%s" % (private_ips))

    ret = conn.describe_nics(offset=0, limit=100, search_word=private_ips, owner=user_id,status=["in-use", "available"])
    print("ret==%s" % (ret))
    # check ret_code
    ret_code = ret.get("ret_code")
    print("ret_code==%s" % (ret_code))
    if ret_code != 0:
        print("describe_nics failed")
        exit(-1)

    #get total
    total_count = ret.get('total_count')
    print("total_count == %d" %(total_count))
    if not total_count:
        print("total_count is  null")
        print("total_count == %d" % (total_count))
        print("private_ips:%s is available" %(private_ips))
        g_private_ips_available_flag = True

    print("子线程结束")



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

    opt_parser.add_option("-m", "--private_ips", action="store", type="string", \
                          dest="private_ips", help='private ips', default="")



    (options, _) = opt_parser.parse_args(sys.argv)
    zone_id = options.zone_id
    access_key_id = options.access_key_id
    secret_access_key = options.secret_access_key
    host = options.host
    port = options.port
    protocol = options.protocol
    vxnet_id = options.vxnet_id
    private_ips = options.private_ips
    print("zone_id:%s" % (zone_id))
    print("access_key_id:%s" % (access_key_id))
    print("secret_access_key:%s" % (secret_access_key))
    print("host:%s" % (host))
    print("port:%s" % (port))
    print("protocol:%s" % (protocol))
    print("vxnet_id:%s" % (vxnet_id))
    print("private_ips:%s" % (private_ips))



    #连接iaas后台
    connect_iaas(zone_id, access_key_id, secret_access_key, host,port,protocol)

    #创建子线程--查询私有网络IP是否可用
    t = threading.Thread(target=check_private_ip,args=(private_ips,))
    t.start()
    t.join()

    if not g_private_ips_available_flag:
        print("private_ips:%s is in-use" % (private_ips))
        g_private_ips_status = "in-use"
    else:
        print("private_ips:%s is available" % (private_ips))
        g_private_ips_status = "available"


    # g_private_ips_status 写入文件
    private_ips_status_conf = "/opt/private_ips_status_conf"
    with open(private_ips_status_conf, "w+") as f1:
        f1.write("PRIVATE_IPS_STATUS %s" % (g_private_ips_status))

    print("主线程结束")

