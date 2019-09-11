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

def get_memcached_ip(conn,user_id,cache_id):
    print("get_memcached_ip user_id == %s cache_id == %s" % (user_id,cache_id))
    if cache_id and not isinstance(cache_id, list):
        cache_id = [cache_id]
    print("cache_id == %s" %(cache_id))
    private_ip = None

    # DescribeCaches
    action = const.ACTION_DESCRIBE_CACHES
    print("action == %s" % (action))
    ret = conn.describe_caches(owner=user_id,caches=cache_id,verbose=1)
    print("describe_caches ret == %s" % (ret))
    Common.check_ret_code(ret, action)

    cache_set = ret['cache_set']
    if cache_set is None or len(cache_set) == 0:
        print("describe_caches cache_set is None")
        exit(-1)
    for cache in cache_set:
        nodes = cache.get("nodes")
        for node in nodes:
            private_ip = node.get("private_ip")

    return private_ip


def create_cache(conn,user_id,vxnet_id,private_ips=None):
    print("子线程启动")
    print("create_cache user_id == %s vxnet_id == %s private_ips == %s" % (user_id,vxnet_id,private_ips))

    if not private_ips:
        print("private_ips is None")
        # CreateCache
        action = const.ACTION_CREATE_CACHE
        print("action == %s" % (action))
        ret = conn.create_cache(owner=user_id,vxnet=vxnet_id,cache_size=1,cache_type='memcached1.4.13',cache_name='vdi-portal-memcached')
        print("create_cache ret == %s" % (ret))
        Common.check_ret_code(ret, action)
    else:
        print("private_ips is %s" %(private_ips))
        # CreateCache
        action = const.ACTION_CREATE_CACHE
        print("action == %s" % (action))
        private_ips_list = {"cache_role": "master", "private_ips": private_ips}
        ret = conn.create_cache(owner=user_id,vxnet=vxnet_id,cache_size=1,cache_type='memcached1.4.13',cache_name='vdi-portal-memcached',private_ips=[private_ips_list])
        print("create_cache ret == %s" % (ret))
        Common.check_ret_code(ret, action)

    job_id = ret['job_id']
    cache_id = ret['cache_id']
    print("job_id == %s" % (job_id))
    print("cache_id == %s" % (cache_id))
    # check job status
    num = 0
    while num < 300:
        num = num + 1
        print("num == %d" % (num))
        time.sleep(1)
        status = Common.get_job_status(conn,job_id)
        if status == "successful":
            print("create_cache successful")
            break
    print("status == %s" % (status))

    if status == "successful":
        print("create_cache cache successful")

        #memcached_ip 写入文件
        memcached_ip_conf = "/opt/memcached_ip_conf"
        memcached_ip = get_memcached_ip(conn,user_id,cache_id)
        print("get_memcached_ip memcached_ip == %s" %(memcached_ip))
        if memcached_ip:
            with open(memcached_ip_conf, "w+") as f1:
                f1.write("MEMCACHED_ADDRESS %s" %(memcached_ip))

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
    conn = Common.connect_iaas(zone_id, access_key_id, secret_access_key, host,port,protocol)
    print("connect_iaas conn == %s" % (conn))

    # 获取账号ID
    user_id = Common.get_user_id(conn,access_key_id)
    print("get_user_id user_id == %s" % (user_id))

    #创建子线程执行创建数据库的操作
    t = threading.Thread(target=create_cache,args=(conn,user_id,vxnet_id,private_ips,))
    t.start()
    t.join()

    print("主线程结束")

