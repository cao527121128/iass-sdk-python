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

def get_cache_node_id(conn,user_id,cache_id):
    print("get_cache_node_id user_id == %s cache_id == %s" % (user_id,cache_id))
    cache_node_id = None

    # DescribeCacheNodes
    action = const.ACTION_DESCRIBE_CACHE_NODES
    print("action == %s" % (action))
    ret = conn.describe_cache_nodes(owner=user_id,cache=cache_id,verbose=1)
    print("describe_cache_nodes ret == %s" % (ret))
    Common.check_ret_code(ret, action)

    cache_node_set = ret['cache_node_set']
    if cache_node_set is None or len(cache_node_set) == 0:
        print("describe_cache_nodes cache_node_set is None")
        exit(-1)
    for cache_node in cache_node_set:
        cache_node_id = cache_node.get("cache_node_id")
        print("cache_node_id == %s" %(cache_node_id))

    return cache_node_id

def get_cache_master_ip(conn,user_id,cache_id):
    print("get_cache_master_ip user_id == %s cache_id == %s" % (user_id,cache_id))
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
        ret = conn.create_cache(owner=user_id,vxnet=vxnet_id,cache_size=1,cache_type='memcached1.4.13',cache_name='缓存服务',description='缓存')
        print("create_cache ret == %s" % (ret))
        Common.check_ret_code(ret, action)
    else:
        print("private_ips is %s" %(private_ips))
        # CreateCache
        action = const.ACTION_CREATE_CACHE
        print("action == %s" % (action))
        private_ips_list = {"cache_role": "master", "private_ips": private_ips}
        ret = conn.create_cache(owner=user_id,vxnet=vxnet_id,cache_size=1,cache_type='memcached1.4.13',cache_name='缓存服务',description='缓存',private_ips=[private_ips_list])
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

        # cache_id 写入文件
        cache_id_conf = "/opt/cache_id_conf"
        with open(cache_id_conf, "w+") as f:
            f.write("CACHE_ID %s" % (cache_id))

        #cache_master_ip 写入文件
        cache_master_ip_conf = "/opt/cache_master_ip_conf"
        cache_master_ip = get_cache_master_ip(conn,user_id,cache_id)
        print("get_cache_master_ip cache_master_ip == %s" %(cache_master_ip))
        if cache_master_ip:
            with open(cache_master_ip_conf, "w+") as f:
                f.write("MEMCACHED_ADDRESS %s" %(cache_master_ip))

        #cache_node_id 写入文件
        cache_node_id_conf = "/opt/cache_node_id_conf"
        cache_node_id = get_cache_node_id(conn,user_id,cache_id)
        print("get_cache_node_id cache_node_id == %s" %(cache_node_id))
        if cache_node_id:
            with open(cache_node_id_conf, "w+") as f:
                f.write("CACHE_NODE_ID %s" %(cache_node_id))

        # DescribeTags
        action = const.ACTION_DESCRIBE_TAGS
        print("action == %s" % (action))
        ret = conn.describe_tags(search_word='桌面云缓存',offset=0,limit=100)
        print("describe_tags ret == %s" % (ret))
        Common.check_ret_code(ret, action)
        tag_set = ret['tag_set']
        print("tag_set == %s" % (tag_set))
        if tag_set is None or len(tag_set) == 0:
            print("describe_tags tag_set is None")

            # CreateTag
            action = const.ACTION_CREATE_TAG
            print("action == %s" % (action))
            ret = conn.create_tag(tag_name='桌面云缓存')
            print("create_tag ret == %s" % (ret))
            Common.check_ret_code(ret, action)
            tag_id = ret['tag_id']
        else:
            for tag in tag_set:
                tag_id = tag.get("tag_id")

        print("tag_id == %s" % (tag_id))
        # AttachTags
        action = const.ACTION_ATTACH_TAGS
        print("action == %s" % (action))
        resource_tag_pairs = [{"resource_type": "cache", "resource_id": cache_id, "tag_id": tag_id}]
        selectedData = [tag_id]
        print("resource_tag_pairs == %s" % (resource_tag_pairs))
        print("selectedData == %s" % (selectedData))
        ret = conn.attach_tags(resource_tag_pairs=resource_tag_pairs, selectedData=selectedData)
        print("attach_tags ret == %s" % (ret))
        Common.check_ret_code(ret, action)

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

    #创建子线程执行创建缓存的操作
    t = threading.Thread(target=create_cache,args=(conn,user_id,vxnet_id,private_ips,))
    t.start()
    t.join()

    print("主线程结束")

