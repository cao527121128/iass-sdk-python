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
g_resource_ids = []
g_cloned_instance_ips = []
g_scale_loadbalancer_backends_ids = []

def get_cloned_instance_ip(conn,user_id,instance_id):
    print("get_cloned_instance_ip user_id == %s instance_id == %s" %(user_id,instance_id))
    private_ip = ""

    if instance_id and not isinstance(instance_id, list):
        instance_id = [instance_id]
    print("instance_id == %s" %(instance_id))

    # DescribeInstances
    action = const.ACTION_DESCRIBE_INSTANCES
    print("action == %s" % (action))
    ret = conn.describe_instances(owner=user_id,instances=instance_id,verbose=1)
    print("describe_instances ret == %s" % (ret))
    Common.check_ret_code(ret, action)

    # get private_ip
    instance_set = ret['instance_set']
    if instance_set is None or len(instance_set) == 0:
        print("describe_instances instance_set is None")
        exit(-1)
    for instance in instance_set:
        vxnets = instance.get("vxnets")
        for vxnet in vxnets:
            private_ip = vxnet.get("private_ip")

    print("private_ip == %s" %(private_ip))
    return private_ip

def clone_instances(conn,user_id,resource_id,vxnet_id,private_ips=None,hostname=None):
    print("子线程启动")
    print("clone_instances user_id == %s resource_id == %s vxnet_id == %s private_ips == %s hostname == %s" % (user_id,resource_id,vxnet_id,private_ips,hostname))
    if resource_id and not isinstance(resource_id, list):
        resource_id = [resource_id]
    print("resource_id == %s" %(resource_id))
    global g_resource_ids
    global g_cloned_instance_ips

    if not private_ips:
        print("private_ips is None")
        # clone_instances
        action = const.ACTION_CLONE_INSTANCES
        print("action == %s" % (action))
        vxnets_list = resource_id[0] + "|" + vxnet_id
        print("vxnets_list == %s" %(vxnets_list))
        ret = conn.clone_instances(owner=user_id,instances=resource_id,vxnets=[vxnets_list])
        print("clone_instances ret == %s" % (ret))
        Common.check_ret_code(ret, action)
    else:
        print("private_ips is %s" %(private_ips))
        # clone_instances
        action = const.ACTION_CLONE_INSTANCES
        print("action == %s" % (action))
        vxnets_list = resource_id[0] + "|" + vxnet_id + "|" + private_ips
        print("vxnets_list == %s" %(vxnets_list))
        ret = conn.clone_instances(owner=user_id,instances=resource_id,vxnets=[vxnets_list])
        print("clone_instances ret == %s" % (ret))
        Common.check_ret_code(ret, action)

    job_id = ret['job_id']
    instance_id = ret['instances']
    cloned_instance_id = instance_id[0]
    print("cloned_instance_id == %s" % (cloned_instance_id))
    print("job_id == %s" % (job_id))
    # check job status
    num = 0
    while num < 300:
        num = num + 1
        print("num == %d" % (num))
        time.sleep(1)
        status = Common.get_job_status(conn,job_id)
        if status == "successful":
            print("clone_instances successful")
            break
    print("status == %s" % (status))

    if status == "successful":
        print("clone_instances instance successful")

        cloned_instance_ip = get_cloned_instance_ip(conn,user_id,instance_id)
        num = 0
        while num < 300:
            num = num + 1
            print("num == %d" % (num))
            time.sleep(1)
            cloned_instance_ip = get_cloned_instance_ip(conn,user_id,instance_id)
            if cloned_instance_ip != "":
                print("get_cloned_instance_ip successful")
                break

        # cloned_instance_ip 写入文件
        print("cloned_instance_ip == %s" % (cloned_instance_ip))
        cloned_instance_ip_conf = "/opt/cloned_%s_instance_ip_conf" %(hostname)
        with open(cloned_instance_ip_conf, "w+") as f1:
            f1.write("CLONED_%s_INSTANCE_IP %s" % (hostname.upper(),cloned_instance_ip))

        if cloned_instance_ip not in g_cloned_instance_ips:
            g_cloned_instance_ips.append(cloned_instance_ip)

        # cloned_instance_id 写入文件
        print("cloned_instance_id == %s" % (cloned_instance_id))
        cloned_instance_id_conf = "/opt/cloned_%s_instance_id_conf" %(hostname)
        with open(cloned_instance_id_conf, "w+") as f2:
            f2.write("CLONED_%s_INSTANCE_ID %s" % (hostname.upper(),cloned_instance_id))

        if cloned_instance_id not in g_resource_ids:
            g_resource_ids.append(cloned_instance_id)

        # attach tags
        current_time = time.strftime("%Y-%m-%d", time.localtime())
        tag_name = '桌面云服务器%s %s' %(hostname,current_time)
        Common.attach_tags_to_resource(conn,user_id=user_id,tag_name=tag_name,resource_type='instance',resource_id=cloned_instance_id)

    print("子线程结束")

def get_loadbalancer_listeners(conn, user_id, loadbalancer_id):
    print("get_loadbalancer_listeners user_id == %s loadbalancer_id == %s" % (user_id, loadbalancer_id))
    loadbalancer_listeners_ids = []

    # DescribeLoadBalancerListeners
    action = const.ACTION_DESCRIBE_LOADBALANCER_LISTENERS
    print("action == %s" % (action))
    ret = conn.describe_loadbalancer_listeners(owner=user_id, offset=0, limit=5,loadbalancer=loadbalancer_id)
    print("describe_loadbalancer_listeners ret == %s" % (ret))
    Common.check_ret_code(ret, action)

    # get listener_port
    loadbalancer_listener_set = ret['loadbalancer_listener_set']
    if loadbalancer_listener_set is None or len(loadbalancer_listener_set) == 0:
        print("describe_loadbalancer_listeners loadbalancer_listener_set is None")
        return None

    for loadbalancer_listener in loadbalancer_listener_set:
        loadbalancer_listener_id = loadbalancer_listener.get("loadbalancer_listener_id")
        if loadbalancer_listener_id not in loadbalancer_listeners_ids:
            loadbalancer_listeners_ids.append(loadbalancer_listener_id)

    print("loadbalancer_listeners_ids == %s" % (loadbalancer_listeners_ids))
    return loadbalancer_listeners_ids

def get_loadbalancer_listeners_port(conn,user_id,loadbalancer_listeners_id):
    print("get_loadbalancer_listeners_port user_id == %s loadbalancer_listeners_id == %s" %(user_id,loadbalancer_listeners_id))
    listener_port = None
    if loadbalancer_listeners_id and not isinstance(loadbalancer_listeners_id, list):
        loadbalancer_listeners_id = [loadbalancer_listeners_id]

    # DescribeLoadBalancerListeners
    action = const.ACTION_DESCRIBE_LOADBALANCER_LISTENERS
    ret = conn.describe_loadbalancer_listeners(owner=user_id,offset=0,limit=1,loadbalancer_listeners=loadbalancer_listeners_id)
    Common.check_ret_code(ret, action)

    # get listener_port
    loadbalancer_listener_set = ret['loadbalancer_listener_set']
    if loadbalancer_listener_set is None or len(loadbalancer_listener_set) == 0:
        print("describe_loadbalancer_listeners loadbalancer_listener_set is None")
        return None

    for loadbalancer_listener in loadbalancer_listener_set:
        listener_port = loadbalancer_listener.get("listener_port")

    return listener_port

def add_backends_to_listener(conn,user_id,loadbalancer_listeners_ids,resource_id):
    print("add_backends_to_listener user_id == %s loadbalancer_listeners_ids == %s resource_id == %s" % (user_id,loadbalancer_listeners_ids,resource_id))
    global  g_scale_loadbalancer_backends_ids

    for loadbalancer_listeners_id in loadbalancer_listeners_ids:
        print("loadbalancer_listeners_id == %s" % (loadbalancer_listeners_id))

        # get listener_port
        listener_port = get_loadbalancer_listeners_port(conn,user_id,loadbalancer_listeners_id)

        if not listener_port:
            print("get_loadbalancer_listeners_port listener_port failed")
            continue

        if 10080 == listener_port:
            print("10080 listener_port does not need to add a listener backend")
            continue

        # DescribeLoadBalancerBackends
        action = const.ACTION_DESCRIBE_LOADBALANCER_BACKENDS
        ret = conn.describe_loadbalancer_backends(loadbalancer_listener=loadbalancer_listeners_id,owner=user_id)
        Common.check_ret_code(ret, action)

        # get exist_resource_ids
        loadbalancer_backend_set = ret['loadbalancer_backend_set']
        exist_resource_ids = []
        if loadbalancer_backend_set:
            for loadbalancer_backend in loadbalancer_backend_set:
                exist_resource_id = loadbalancer_backend.get("resource_id")
                if exist_resource_id not in exist_resource_ids:
                    exist_resource_ids.append(exist_resource_id)

        print("exist_resource_ids == %s" %(exist_resource_ids))
        if resource_id in exist_resource_ids:
            print("backend resource [%s] is (or would be) exist in current loadbalancer_listeners" %(resource_id))
            continue

        # AddLoadBalancerBackends
        action = const.ACTION_ADD_LOADBALANCER_BACKENDS
        backends_list = [{"loadbalancer_backend_name":"backend-desktop-server","resource_id":resource_id,"port":listener_port,"weight":"1"}]
        ret = conn.add_backends_to_listener(loadbalancer_listener=loadbalancer_listeners_id,backends=backends_list,owner=user_id)
        Common.check_ret_code(ret, action)
        loadbalancer_backends_id = ret['loadbalancer_backends'][0]

        if loadbalancer_backends_id not in g_scale_loadbalancer_backends_ids:
            g_scale_loadbalancer_backends_ids.append(loadbalancer_backends_id)

    return None

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

    opt_parser.add_option("-m", "--private_ips", action="store", type="string", \
                          dest="private_ips", help='private ips', default="")

    opt_parser.add_option("-u", "--num_of_desktop_server", action="store", type="int", \
                          dest="num_of_desktop_server", help='the number of desktop_server will scale out', default=0)

    opt_parser.add_option("-l", "--loadbalancer_id", action="store", type="string", \
                          dest="loadbalancer_id", help='loadbalancer_id', default="")

    (options, _) = opt_parser.parse_args(sys.argv)

    zone_id = options.zone_id
    access_key_id = options.access_key_id
    secret_access_key = options.secret_access_key
    host = options.host
    port = options.port
    protocol = options.protocol
    vxnet_id = options.vxnet_id
    resource_id = options.resource_id
    private_ips = options.private_ips
    num_of_desktop_server = options.num_of_desktop_server
    loadbalancer_id = options.loadbalancer_id

    print("zone_id:%s" % (zone_id))
    print("access_key_id:%s" % (access_key_id))
    print("secret_access_key:%s" % (secret_access_key))
    print("host:%s" % (host))
    print("port:%s" % (port))
    print("protocol:%s" % (protocol))
    print("vxnet_id:%s" % (vxnet_id))
    print("resource_id:%s" % (resource_id))
    print("private_ips:%s" % (private_ips))
    print("num_of_desktop_server:%d" % (num_of_desktop_server))
    print("loadbalancer_id:%s" % (loadbalancer_id))

    #连接iaas后台
    conn = Common.connect_iaas(zone_id, access_key_id, secret_access_key, host,port,protocol)
    print("connect_iaas conn == %s" % (conn))

    # 获取账号ID
    user_id = Common.get_user_id(conn,access_key_id)
    print("get_user_id user_id == %s" % (user_id))

    if num_of_desktop_server == 4:
        hostname_list = const.EXPAND_FOUR_DESKTOP_SERVER
    elif num_of_desktop_server == 6:
        hostname_list = const.EXPAND_SIX_DESKTOP_SERVER
    elif num_of_desktop_server == 8:
        hostname_list = const.EXPAND_EIGHT_DESKTOP_SERVER
    else:
        print("invalid num_of_desktop_server:%d" % (num_of_desktop_server))
        exit(-1)

    # clone vdi
    print("hostname_list == %s" %(hostname_list))
    for hostname in hostname_list:
        #创建子线程--克隆主机
        t1 = threading.Thread(target=clone_instances,args=(conn,user_id,resource_id,vxnet_id,private_ips,hostname,))
        t1.start()
        t1.join()

    # test
    # loadbalancer_id='lb-ru60rl99'
    # g_resource_ids = ['i-60e0g5vo', 'i-hq1cby78']

    print("loadbalancer_id:%s" % (loadbalancer_id))
    print("g_resource_ids:%s" % (g_resource_ids))
    # add clone vdi to loadbalancer
    if loadbalancer_id and g_resource_ids:
        #获取负载均衡器监听器
        loadbalancer_listeners_ids = get_loadbalancer_listeners(conn, user_id, loadbalancer_id)
        print("get_loadbalancer_listeners loadbalancer_listeners_ids  == %s" % (loadbalancer_listeners_ids))

        # 添加负载均衡器监听器后端服务主机
        for resource_id in g_resource_ids:
            print("resource_id == %s" %(resource_id))
            loadbalancer_backends_ids = add_backends_to_listener(conn, user_id, loadbalancer_listeners_ids,resource_id)
            print("add_backends_to_listener loadbalancer_backends_ids  == %s" % (loadbalancer_backends_ids))

        #创建子线程--更新负载均衡器 应用修改
        t2 = threading.Thread(target=update_loadbalancers,args=(conn,user_id,loadbalancer_id,))
        t2.start()
        t2.join()

        # g_resource_ids 写入文件
        print("g_resource_ids:%s" % (g_resource_ids))
        g_resource_ids_str = ",".join(g_resource_ids)
        print("g_resource_ids_str:%s" % (g_resource_ids_str))
        scale_cloned_instance_id_conf = "/opt/scale_cloned_instance_id_conf"
        with open(scale_cloned_instance_id_conf, "w+") as f1:
            f1.write("SCALE_CLONED_INSTANCE_IDS %s" % (g_resource_ids_str))

        # g_scale_loadbalancer_backends_ids 写入文件
        print("g_scale_loadbalancer_backends_ids:%s" % (g_scale_loadbalancer_backends_ids))
        g_scale_loadbalancer_backends_ids_str = ",".join(g_scale_loadbalancer_backends_ids)
        print("g_scale_loadbalancer_backends_ids_str:%s" % (g_scale_loadbalancer_backends_ids_str))
        scale_loadbalancer_backends_ids_conf = "/opt/scale_loadbalancer_backends_ids_conf"
        with open(scale_loadbalancer_backends_ids_conf, "w+") as f1:
            f1.write("SCALE_LOADBALANCER_BACKENDS_IDS %s" % (g_scale_loadbalancer_backends_ids_str))

        # g_cloned_instance_ips 写入文件
        print("g_cloned_instance_ips:%s" % (g_cloned_instance_ips))
        g_cloned_instance_ips_str = ",".join(g_cloned_instance_ips)
        print("g_cloned_instance_ips_str:%s" % (g_cloned_instance_ips_str))
        scale_cloned_instance_ip_conf = "/opt/scale_cloned_instance_ip_conf"
        with open(scale_cloned_instance_ip_conf, "w+") as f1:
            f1.write("SCALE_CLONED_INSTANCE_IPS %s" % (g_cloned_instance_ips_str))

    print("主线程结束")

