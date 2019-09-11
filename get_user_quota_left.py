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
import qingcloud.iaas.constants as const
import common.common as Common

def get_user_quota_left(resource_type,user_id,conn):
    print("get_user_quota_left resource_type == %s user_id == %s" % (resource_type,user_id))
    if resource_type and not isinstance(resource_type, list):
        resource_type = [resource_type]
    print("resource_type == %s" %(resource_type))
    resource_type_left = 0

    # GetQuotaLeft
    action = const.ACTION_GET_QUOTA_LEFT
    print("action == %s" % (action))
    ret = conn.get_quota_left(resource_types=resource_type,owner=user_id)
    print("get_quota_left ret == %s" % (ret))
    Common.check_ret_code(ret, action)

    quota_left_set = ret['quota_left_set']
    if quota_left_set is None or len(quota_left_set) == 0:
        print("get_quota_left quota_left_set is None")
        return 0
    for quota_left in quota_left_set:
        resource_type_left = quota_left.get("left")

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
    conn = Common.connect_iaas(zone_id, access_key_id, secret_access_key, host,port,protocol)
    print("connect_iaas conn == %s" % (conn))

    # 获取账号ID
    user_id = Common.get_user_id(conn,access_key_id)
    print("get_user_id user_id == %s" % (user_id))

    rdb_quota_left = get_user_quota_left('rdb',user_id,conn)
    print("rdb_quota_left=%d" %(rdb_quota_left))

    cache_quota_left = get_user_quota_left('cache', user_id,conn)
    print("cache_quota_left=%d" % (cache_quota_left))

    instance_quota_left = get_user_quota_left('instance', user_id,conn)
    print("instance_quota_left=%d" % (instance_quota_left))

    loadbalancer_quota_left = get_user_quota_left('loadbalancer', user_id,conn)
    print("loadbalancer_quota_left=%d" % (loadbalancer_quota_left))

    s2_server_quota_left = get_user_quota_left('s2_server', user_id,conn)
    print("s2_server_quota_left=%d" % (s2_server_quota_left))

    cluster_quota_left = get_user_quota_left('cluster', user_id,conn)
    print("cluster_quota_left=%d" % (cluster_quota_left))

    # rdb_quota_left 写入文件
    rdb_quota_left_conf = "/opt/rdb_quota_left_conf"
    with open(rdb_quota_left_conf, "w+") as f1:
        f1.write("RDB_QUOTA_LEFT %d" % (rdb_quota_left))

    # cache_quota_left 写入文件
    cache_quota_left_conf = "/opt/cache_quota_left_conf"
    with open(cache_quota_left_conf, "w+") as f1:
        f1.write("CACHE_QUOTA_LEFT %d" % (cache_quota_left))

    # instance_quota_left 写入文件
    instance_quota_left_conf = "/opt/instance_quota_left_conf"
    with open(instance_quota_left_conf, "w+") as f1:
        f1.write("INSTANCE_QUOTA_LEFT %d" % (instance_quota_left))

    # loadbalancer_quota_left 写入文件
    loadbalancer_quota_left_conf = "/opt/loadbalancer_quota_left_conf"
    with open(loadbalancer_quota_left_conf, "w+") as f1:
        f1.write("LOADBALANCER_QUOTA_LEFT %d" % (loadbalancer_quota_left))

    # s2_server_quota_left 写入文件
    s2_server_quota_left_conf = "/opt/s2_server_quota_left_conf"
    with open(s2_server_quota_left_conf, "w+") as f1:
        f1.write("S2_SERVER_QUOTA_LEFT %d" % (s2_server_quota_left))

    # cluster_quota_left 写入文件
    cluster_quota_left_conf = "/opt/cluster_quota_left_conf"
    with open(cluster_quota_left_conf, "w+") as f1:
        f1.write("CLUSTER_QUOTA_LEFT %d" % (cluster_quota_left))

    print("主线程结束")

