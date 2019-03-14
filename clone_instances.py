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
    global g_cloned_instance_id
    for res_id in resource_id:
        ret = conn.clone_instances(instances=[res_id])
        if ret < 0:
            print("clone_instances fail")
            exit(-1)
        print("ret==%s" % (ret))
        g_cloned_instance_id = ret.get("instances")
        print("g_cloned_instance_id=%s" %(g_cloned_instance_id))
        if not g_cloned_instance_id:
            print("clone instances fail")
            exit(-1)
        status = "pending"
        while status != "running":
            time.sleep(1)
            status = get_instances_status()
        print("子线程结束")




def get_instances_status():
    print("get_instances_status")
    global conn
    global g_cloned_instance_id
    ret = conn.describe_instances(instances=g_cloned_instance_id)
    if ret < 0:
        print("describe_instances fail")
        exit(-1)
    matched_instance = ret['instance_set']
    print("matched_instance==%s"%(matched_instance))

    print("************************************")

    wanted_instance = matched_instance[0]
    print("wanted_instance==%s" % (wanted_instance))

    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    status = wanted_instance.get("status")
    print("status=%s" % (status))
    return status



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
    global access_key_id
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
    print("vxnet_id:%s" % (vxnet_id))
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

