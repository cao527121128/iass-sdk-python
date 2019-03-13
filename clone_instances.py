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
loadbalancer_id = None
loadbalancer_listener_id = None
resource_id = None
g_cloned_instance_id = None






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

def clone_instances(resource_id):
    print("子线程启动")
    print("clone_instances")
    global conn
    for res_id in resource_id:
        ret = conn.clone_instances(instances=[res_id])
        if ret < 0:
            print("clone_instances fail")
            exit(-1)
        print("ret==%s" % (ret))
        instance_id = ret.get("instances")
        print("instance_id=%s" %(instance_id))
        if not instance_id:
            print("clone instance_id fail")
            exit(-1)
        status = "pending"
        while status != "running":
            time.sleep(1)
            status = get_instances_status(instance_id)
        print("子线程结束")




def get_instances_status(instance_id):
    print("get_instances_status")
    global conn
    global g_cloned_instance_id
    ret = conn.describe_instances(instances=instance_id)
    if ret < 0:
        print("describe_instances fail")
        exit(-1)
    print(ret)
    matched_instance = ret['instance_set']
    print("matched_instance==%s"%(matched_instance))

    print("************************************")

    wanted_instance = matched_instance[0]
    print("wanted_instance==%s" % (wanted_instance))

    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    status = wanted_instance.get("status")
    instance_id = wanted_instance.get("instance_id")
    g_cloned_instance_id = instance_id
    print("status=%s" % (status))
    print("g_cloned_instance_id=%s" %(g_cloned_instance_id))
    return status


def get_loadbalancer_transition_status():
    print("get_loadbalancer_transition_status")
    global conn
    global loadbalancer_id
    ret = conn.describe_loadbalancers(limit=1,search_word='vdi-portal-loadbalancer',verbose=1)
    if ret < 0:
        print("describe_loadbalancers fail")
        exit(-1)
    print(ret)
    matched_loadbalancer = ret['loadbalancer_set']
    print("matched_loadbalancer==%s"%(matched_loadbalancer))

    print("************************************")

    wanted_loadbalancer = ret['loadbalancer_set'][0]
    print("wanted_loadbalancer==%s" % (wanted_loadbalancer))

    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    transition_status = wanted_loadbalancer.get('transition_status')
    print("transition_status=%s" % (transition_status))
    return transition_status

def get_loadbalancer_listener_id():
    print("get_loadbalancer_listener_id")
    global conn
    global loadbalancer_id
    ret = conn.describe_loadbalancers(limit=1,search_word='vdi-portal-loadbalancer',verbose=1)
    if ret < 0:
        print("describe_loadbalancers fail")
        exit(-1)
    print(ret)
    matched_loadbalancer = ret['loadbalancer_set']
    print("matched_loadbalancer==%s"%(matched_loadbalancer))

    print("************************************")

    wanted_loadbalancer = ret['loadbalancer_set'][0]
    print("wanted_loadbalancer==%s" % (wanted_loadbalancer))

    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    listeners = wanted_loadbalancer['listeners']

    loadbalancer_listener_id = listeners[0].get('loadbalancer_listener_id')
    print("loadbalancer_listener_id=%s" % (loadbalancer_listener_id))
    return loadbalancer_listener_id



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

    wanted_vxnet = ret['vxnet_set'][0]
    print("wanted_vxnet==%s" % (wanted_vxnet))

    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    vxnet_id = wanted_vxnet.get('vxnet_id')
    print("vxnet_id=%s" % (vxnet_id))
    return vxnet_id


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

    wanted_access_key = ret['access_key_set'][0]
    print("wanted_access_key==%s" % (wanted_access_key))

    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    user_id = wanted_access_key.get('owner')
    print("user_id=%s" % (user_id))
    return user_id

def get_eip_id():
    print("get_eip_id")
    global conn
    #查看公网IP
    user_id = get_user_id()
    ret = conn.describe_eips(limit=1, status=['available'], owner=user_id, verbose=1)
    if ret < 0:
        print("describe_eips fail")
        exit(-1)
    matched_eip = ret['eip_set']
    print("matched_eip==%s" % (matched_eip))

    print("************************************")
    if  not matched_eip:
        return None
    wanted_eip = matched_eip[0]
    print("wanted_eip==%s" % (wanted_eip))

    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    eip_id = wanted_eip['eip_id']
    print("eip_id=%s" % (eip_id))
    return eip_id

def get_eip_addr_by_eip_id(eip_id):
    print("get_eip_addr")
    global conn
    #查看公网IP
    user_id = get_user_id()
    ret = conn.describe_eips(eips=[eip_id],owner=user_id, verbose=1)
    if ret < 0:
        print("describe_eips fail")
        exit(-1)
    matched_eip = ret['eip_set']
    print("matched_eip==%s" % (matched_eip))

    print("************************************")
    if  not matched_eip:
        return None
    wanted_eip = matched_eip[0]
    print("wanted_eip==%s" % (wanted_eip))

    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    eip_addr = wanted_eip['eip_addr']
    print("eip_addr=%s" % (eip_addr))
    return eip_addr


def add_loadbalancer_listeners(loadbalancer_id):
    print("子线程启动")
    print("add_loadbalancer_listeners")
    global conn
    listeners=[
        {"listener_protocol":"http",
         "listener_port":80,
         "backend_protocol":"http",
         "balance_mode":"roundrobin",
         "loadbalancer_listener_name":"http-listener"
        }
    ]

    ret = conn.add_listeners_to_loadbalancer(
        loadbalancer=loadbalancer_id,
        listeners=listeners
    )

    if ret < 0:
        print("add_listeners_to_loadbalancer fail")
        exit(-1)
    print("ret==%s" % (ret))

    # status = "pending"
    # while status != "active":
    #     time.sleep(1)
    #     status = get_loadbalancer_status()
    print("子线程结束")

def update_loadbalancers(loadbalancer_id):
    print("子线程启动")
    print("update_loadbalancers")
    global conn
    user_id = get_user_id()
    ret = conn.update_loadbalancers(
        loadbalancers=[loadbalancer_id],
        target_user=user_id
    )

    if ret < 0:
        print("update_loadbalancers fail")
        exit(-1)
    print("ret==%s" % (ret))

    status = "pending"
    transition_status = "updating"
    while status != "active":
        while transition_status !="":
            time.sleep(1)
            transition_status = get_loadbalancer_transition_status()
        time.sleep(1)
        status = get_loadbalancer_status()
    print("子线程结束")

def add_backends_to_listener(loadbalancer_listener_id,resource_id):
    print("子线程启动")
    print("add_backends_to_listener")
    global conn
    for res_id in resource_id:
        backends=[
            {"resource_id":res_id,
             "port":80,"weight":"5",
             "loadbalancer_backend_name":"backend_desktop_server_01"
            }
        ]
        print("backends=%s" %(backends))
        ret = conn.add_backends_to_listener(
            loadbalancer_listener=loadbalancer_listener_id,
            backends=backends
        )

        if ret < 0:
            print("add_backends_to_listener fail")
            exit(-1)
        print("ret==%s" % (ret))

    # status = "pending"
    # while status != "active":
    #     time.sleep(1)
    #     status = get_loadbalancer_status()
    print("子线程结束")

def explode_array(list_str, separator = ","):
    ''' explode list string into array '''
    if list_str is None:
        return None
    result = []
    disk_list = list_str.split(separator)
    for disk in disk_list:
        disk = disk.strip()
        if disk != "":

            result.append(disk)
    return result


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


    (options, _) = opt_parser.parse_args(sys.argv)
    zone_id = options.zone_id
    access_key_id = options.access_key_id
    secret_access_key = options.secret_access_key
    host = options.host
    port = options.port
    protocol = options.protocol
    vxnet_id = options.vxnet_id
    resource_id = explode_array(options.resource_id or "")
    print("zone_id:%s" % (zone_id))
    print("access_key_id:%s" % (access_key_id))
    print("secret_access_key:%s" % (secret_access_key))
    print("host:%s" % (host))
    print("port:%s" % (port))
    print("protocol:%s" % (protocol))
    print("resource_id:%s" % (resource_id))


    #连接iaas后台
    connect_iaas(zone_id, access_key_id, secret_access_key, host,port,protocol)

    #获取vxnet_id
    if vxnet_id:
        print("vxnet_id==%s" %(vxnet_id))
    else:
        vxnet_id = get_vxnet_id()
        print("vxnet_id==%s" % (vxnet_id))


    #创建子线程--克隆主机
    t1 = threading.Thread(target=clone_instances,args=(resource_id,))
    t1.start()
    t1.join()



    #g_cloned_instance_id 写入文件
    cloned_instance_id_conf = "/tmp/cloned_instance_id_conf"
    with open(cloned_instance_id_conf, "w+") as f1:
        f1.write("CLONED_INSTANCE_ID %s" %(g_cloned_instance_id))


    print("主线程结束")

