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

g_loadbalancer_id = None

def get_loadbalancer_ip(conn,user_id,loadbalancer_id):
    print("get_loadbalancer_ip user_id == %s loadbalancer_id == %s" %(user_id,loadbalancer_id))

    loadbalancer_ip = None
    if loadbalancer_id and not isinstance(loadbalancer_id, list):
        loadbalancer_id = [loadbalancer_id]
    print("loadbalancer_id == %s" %(loadbalancer_id))

    # DescribeLoadBalancers
    action = const.ACTION_DESCRIBE_LOADBALANCERS
    print("action == %s" % (action))
    ret = conn.describe_loadbalancers(owner=user_id,offset=0,limit=1,loadbalancers=loadbalancer_id)
    print("describe_loadbalancers ret == %s" % (ret))
    Common.check_ret_code(ret, action)

    # get loadbalancer_ip
    loadbalancer_set = ret['loadbalancer_set']
    if loadbalancer_set is None or len(loadbalancer_set) == 0:
        print("describe_loadbalancers loadbalancer_set is None")
        return None

    for loadbalancer in loadbalancer_set:
        vxnets = loadbalancer.get("vxnet")
        loadbalancer_ip = vxnets.get("private_ip")

    print("loadbalancer_ip == %s" % (loadbalancer_ip))
    return loadbalancer_ip

def update_loadbalancers(conn,user_id,loadbalancer_id):
    print("子线程启动")
    print("update_loadbalancers user_id == %s loadbalancer_id == %s" % (user_id,loadbalancer_id))
    if loadbalancer_id and not isinstance(loadbalancer_id, list):
        loadbalancer_id = [loadbalancer_id]
    print("loadbalancer_id == %s" %(loadbalancer_id))

    # UpdateLoadBalancers
    action = const.ACTION_UPDATE_LOADBALANCERS
    print("action == %s" % (action))
    ret = conn.update_loadbalancers(loadbalancers=loadbalancer_id,owner=user_id)
    print("update_loadbalancers ret == %s" % (ret))
    Common.check_ret_code(ret, action)

    # check job status
    job_id = ret['job_id']
    print("job_id == %s" % (job_id))
    num = 0
    while num < 300:
        num = num + 1
        print("num == %d" % (num))
        time.sleep(1)
        status = Common.get_job_status(conn,job_id)
        if status == "successful":
            print("update_loadbalancers successful")
            break
    print("status == %s" % (status))

    if status == "successful":
        print("update_loadbalancers loadbalancer successful")

        #loadbalancer_ip 写入文件
        loadbalancer_ip_conf = "/opt/loadbalancer_ip_conf"
        loadbalancer_ip = get_loadbalancer_ip(conn,user_id,loadbalancer_id)
        print("get_loadbalancer_ip loadbalancer_ip == %s" %(loadbalancer_ip))
        if loadbalancer_ip:
            with open(loadbalancer_ip_conf, "w+") as f1:
                f1.write("LOADBALANCER_IP %s" %(loadbalancer_ip))

        # loadbalancer_id 写入文件
        loadbalancer_id_conf = "/opt/loadbalancer_id_conf"
        with open(loadbalancer_id_conf, "w+") as f1:
            f1.write("LOADBALANCER_ID %s" % (loadbalancer_id[0]))

    print("子线程结束")

def get_loadbalancer_listeners_port(conn,user_id,loadbalancer_listeners_id):
    print("get_loadbalancer_listeners_port user_id == %s loadbalancer_listeners_id == %s" %(user_id,loadbalancer_listeners_id))
    listener_port = None
    if loadbalancer_listeners_id and not isinstance(loadbalancer_listeners_id, list):
        loadbalancer_listeners_id = [loadbalancer_listeners_id]
    print("loadbalancer_listeners_id == %s" %(loadbalancer_listeners_id))

    # DescribeLoadBalancerListeners
    action = const.ACTION_DESCRIBE_LOADBALANCER_LISTENERS
    print("action == %s" % (action))
    ret = conn.describe_loadbalancer_listeners(owner=user_id,offset=0,limit=1,loadbalancer_listeners=loadbalancer_listeners_id)
    print("describe_loadbalancer_listeners ret == %s" % (ret))
    Common.check_ret_code(ret, action)

    # get listener_port
    loadbalancer_listener_set = ret['loadbalancer_listener_set']
    if loadbalancer_listener_set is None or len(loadbalancer_listener_set) == 0:
        print("describe_loadbalancer_listeners loadbalancer_listener_set is None")
        return None

    for loadbalancer_listener in loadbalancer_listener_set:
        listener_port = loadbalancer_listener.get("listener_port")

    print("listener_port == %s" % (listener_port))
    return listener_port


def add_backends_to_listener(conn,user_id,loadbalancer_listeners_ids,resource_id):
    print("add_backends_to_listener user_id == %s loadbalancer_listeners_ids == %s resource_id == %s" % (user_id,loadbalancer_listeners_ids,resource_id))
    loadbalancer_backends_ids = []

    for loadbalancer_listeners_id in loadbalancer_listeners_ids:
        print("loadbalancer_listeners_id == %s" % (loadbalancer_listeners_id))

        # get listener_port
        listener_port = get_loadbalancer_listeners_port(conn,user_id,loadbalancer_listeners_id)
        print("get_loadbalancer_listeners_port listener_port == %s" % (listener_port))

        if not listener_port:
            print("get_loadbalancer_listeners_port listener_port failed")
            continue

        if 10080 == listener_port:
            print("get_loadbalancer_listeners_port listener_port [%d]")
            print("10080 listener_port does not need to add a listener backend")
            continue

        # AddLoadBalancerBackends
        action = const.ACTION_ADD_LOADBALANCER_BACKENDS
        print("action == %s" % (action))
        backends_list = [{"loadbalancer_backend_name":"backend-desktop-server","resource_id":resource_id,"port":listener_port,"weight":"1"}]
        print("backends_list == %s" % (backends_list))
        ret = conn.add_backends_to_listener(loadbalancer_listener=loadbalancer_listeners_id,backends=backends_list,owner=user_id)
        print("add_backends_to_listener ret == %s" % (ret))
        Common.check_ret_code(ret, action)
        loadbalancer_backends_id = ret['loadbalancer_backends']
        if loadbalancer_backends_id not in loadbalancer_backends_ids:
            loadbalancer_backends_ids.append(loadbalancer_backends_id)

    print("loadbalancer_backends_ids == %s" % (loadbalancer_backends_ids))
    return loadbalancer_backends_ids

def add_loadbalancer_listeners(conn,user_id,loadbalancer_id,platform):
    print("add_loadbalancer_listeners user_id == %s loadbalancer_id == %s platform == %s" % (user_id,loadbalancer_id,platform))
    loadbalancer_listeners_id = None
    # AddLoadBalancerListeners
    action = const.ACTION_ADD_LOADBALANCER_LISTENERS
    print("action == %s" % (action))
    if "qingcloud" == platform:
        listeners_list = [
            {
                "loadbalancer_listener_name":"http-listener",
                "listener_protocol":"http",
                "listener_port":"80",
                "balance_mode":"roundrobin",
                "session_sticky":"insert|1200",
                "healthy_check_method":"tcp",
                "healthy_check_option":"10|5|2|5",
                "scene":0,
                "timeout":"50",
                "tunnel_timeout":"3600",
                "listener_option":0,
                "backend_protocol":"http",
                "forwardfor":1
            },
            {
                "loadbalancer_listener_name": "websocket",
                "listener_protocol": "http",
                "listener_port": "9520",
                "balance_mode": "roundrobin",
                "session_sticky": "insert|1200",
                "healthy_check_method": "tcp",
                "healthy_check_option": "10|5|2|5",
                "scene": 0,
                "timeout": "50",
                "tunnel_timeout": "3600",
                "listener_option": 0,
                "backend_protocol": "http",
                "forwardfor": 1
            },
        ]
    else:
        listeners_list = [
            {
                "loadbalancer_listener_name": "http-listener",
                "listener_protocol": "http",
                "listener_port": "80",
                "balance_mode": "roundrobin",
                "session_sticky": "insert|1200",
                "healthy_check_method": "tcp",
                "healthy_check_option": "10|5|2|5",
                "scene": 0,
                "timeout": "50",
                "tunnel_timeout": "3600",
                "listener_option": 0,
                "backend_protocol": "http",
                "forwardfor": 1
            },
            {
                "loadbalancer_listener_name": "websocket",
                "listener_protocol": "http",
                "listener_port": "9520",
                "balance_mode": "roundrobin",
                "session_sticky": "insert|1200",
                "healthy_check_method": "tcp",
                "healthy_check_option": "10|5|2|5",
                "scene": 0,
                "timeout": "50",
                "tunnel_timeout": "3600",
                "listener_option": 0,
                "backend_protocol": "http",
                "forwardfor": 1
            },
            {
                "loadbalancer_listener_name": "citrix",
                "listener_protocol": "http",
                "listener_port": "10080",
                "balance_mode": "roundrobin",
                "session_sticky": "insert|1200",
                "healthy_check_method": "tcp",
                "healthy_check_option": "10|5|2|5",
                "scene": 0,
                "timeout": "50",
                "tunnel_timeout": "3600",
                "listener_option": 0,
                "backend_protocol": "http",
                "forwardfor": 1
            },
        ]

    print("listeners_list == %s" % (listeners_list))
    ret = conn.add_listeners_to_loadbalancer(listeners=listeners_list,loadbalancer=loadbalancer_id,owner=user_id)
    print("add_listeners_to_loadbalancer ret == %s" % (ret))
    Common.check_ret_code(ret, action)
    loadbalancer_listeners_ids = ret['loadbalancer_listeners']

    print("loadbalancer_listeners_ids == %s" % (loadbalancer_listeners_ids))
    return loadbalancer_listeners_ids

def create_loadbalancer(conn,user_id,vxnet_id,private_ips):
    print("子线程启动")
    print("create_loadbalancer user_id == %s vxnet_id == %s private_ips == %s" % (user_id,vxnet_id,private_ips))
    global g_loadbalancer_id

    # CreateLoadBalancer
    if not private_ips:
        print("private_ips is None")
        action = const.ACTION_CREATE_LOADBALANCER
        print("action == %s" % (action))
        ret = conn.create_loadbalancer(loadbalancer_name='桌面管理中心',loadbalancer_type=0,node_count=2,vxnet=vxnet_id,mode=1,owner=user_id)
        print("create_loadbalancer ret == %s" % (ret))
        Common.check_ret_code(ret, action)
    else:
        print("private_ips is %s" %(private_ips))
        action = const.ACTION_CREATE_LOADBALANCER
        print("action == %s" % (action))
        ret = conn.create_loadbalancer(loadbalancer_name='桌面管理中心',loadbalancer_type=0,node_count=2,vxnet=vxnet_id,mode=1,owner=user_id,private_ip=private_ips)
        print("create_loadbalancer ret == %s" % (ret))
        Common.check_ret_code(ret, action)

    # check job status
    job_id = ret['job_id']
    loadbalancer_id = ret['loadbalancer_id']
    print("job_id == %s" % (job_id))
    print("loadbalancer_id == %s" % (loadbalancer_id))
    num = 0
    while num < 300:
        num = num + 1
        print("num == %d" % (num))
        time.sleep(1)
        status = Common.get_job_status(conn,job_id)
        if status == "successful":
            print("create_loadbalancer successful")
            break
    print("status == %s" % (status))

    if status == "successful":
        print("create_loadbalancer loadbalancer successful")
        g_loadbalancer_id = loadbalancer_id
        print("g_loadbalancer_id == %s" % (g_loadbalancer_id))

        # DescribeTags
        action = const.ACTION_DESCRIBE_TAGS
        print("action == %s" % (action))
        ret = conn.describe_tags(search_word='桌面云负载均衡器', offset=0, limit=100)
        print("describe_tags ret == %s" % (ret))
        Common.check_ret_code(ret, action)
        tag_set = ret['tag_set']
        print("tag_set == %s" % (tag_set))
        if tag_set is None or len(tag_set) == 0:
            print("describe_tags tag_set is None")

            # CreateTag
            action = const.ACTION_CREATE_TAG
            print("action == %s" % (action))
            ret = conn.create_tag(tag_name='桌面云负载均衡器')
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
        resource_tag_pairs = [{"resource_type": "loadbalancer", "resource_id": loadbalancer_id, "tag_id": tag_id}]
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

    opt_parser.add_option("-r", "--resource_id", action="store", type="string", \
                          dest="resource_id", help='resource id', default="")

    opt_parser.add_option("-F", "--platform", action="store", type="string", \
                          dest="platform", help='platform', default="")

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
    resource_ids = Common.explode_array(options.resource_id or "")
    platform = options.platform
    private_ips = options.private_ips

    print("zone_id:%s" % (zone_id))
    print("access_key_id:%s" % (access_key_id))
    print("secret_access_key:%s" % (secret_access_key))
    print("host:%s" % (host))
    print("port:%s" % (port))
    print("protocol:%s" % (protocol))
    print("vxnet_id:%s" % (vxnet_id))
    print("resource_ids:%s" % (resource_ids))
    print("platform:%s" % (platform))
    print("private_ips:%s" % (private_ips))

    #连接iaas后台
    conn = Common.connect_iaas(zone_id, access_key_id, secret_access_key, host,port,protocol)
    print("connect_iaas conn == %s" % (conn))

    # 获取账号ID
    user_id = Common.get_user_id(conn,access_key_id)
    print("get_user_id user_id == %s" % (user_id))

    #创建子线程--创建负载均衡器
    t1 = threading.Thread(target=create_loadbalancer,args=(conn,user_id,vxnet_id,private_ips,))
    t1.start()
    t1.join()

    print("g_loadbalancer_id == %s" % (g_loadbalancer_id))
    if g_loadbalancer_id:
        #创建负载均衡器监听器
        loadbalancer_listeners_ids = add_loadbalancer_listeners(conn, user_id, g_loadbalancer_id, platform)
        print("add_loadbalancer_listeners loadbalancer_listeners_ids  == %s" % (loadbalancer_listeners_ids))

        # 添加负载均衡器监听器后端服务主机
        for resource_id in resource_ids:
            print("resource_id == %s" %(resource_id))
            loadbalancer_backends_ids = add_backends_to_listener(conn, user_id, loadbalancer_listeners_ids,resource_id)
            print("add_backends_to_listener loadbalancer_backends_ids  == %s" % (loadbalancer_backends_ids))

        #创建子线程--更新负载均衡器 应用修改
        t2 = threading.Thread(target=update_loadbalancers,args=(conn,user_id,g_loadbalancer_id,))
        t2.start()
        t2.join()

    print("主线程结束")

