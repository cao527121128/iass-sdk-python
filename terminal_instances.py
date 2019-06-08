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
g_instance_id = None
g_ip_resources_is_released = False



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
   #print("ret_code==%s" % (ret_code))
    if ret_code != 0:
        print("describe_access_keys failed")
        exit(-1)

    matched_access_key = ret['access_key_set']
   # print("matched_access_key==%s" % (matched_access_key))

    #print("************************************")

    wanted_access_key = matched_access_key[0]
    #print("wanted_access_key==%s" % (wanted_access_key))

    #print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    user_id = wanted_access_key.get('owner')
    #print("user_id=%s" % (user_id))
    return user_id

def describe_instances(private_ips):
    print("子线程启动")
    print("describe_instances")
    global conn
    global access_key_id
    global g_instance_id
    user_id = get_user_id()

    print("private_ips == %s" %(private_ips))
    ret = conn.describe_instances(offset=0, limit=100, search_word=private_ips,owner=user_id)

    # check ret_code
    print("ret==%s" % (ret))
    ret_code = ret.get("ret_code")
    print("ret_code==%s" % (ret_code))
    if ret_code != 0:
        print("describe_instances failed")
        exit(-1)

    #get total
    total_count = ret.get('total_count')
    print("total_count == %d" %(total_count))
    if not total_count:
        print("total_count == %d" % (total_count))
        print("instances with private_ips:%s is not exist" %(private_ips))
        print("you can create  instances with this private_ip %s" %(private_ips))

    else:
        print("total_count == %d" % (total_count))
        print("instances with private_ips:%s is exist" %(private_ips))
        print("you can't create instances with this private_ip %s" %(private_ips))

        #查询对应主机id
        matched_instance = ret['instance_set']
        #print("matched_instance==%s" % (matched_instance))

        #print("************************************")

        wanted_instance = matched_instance[0]
        #print("wanted_instance==%s" % (wanted_instance))

        #print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        g_instance_id = wanted_instance.get("instance_id")
        print("g_instance_id=%s" % (g_instance_id))

    print("子线程结束")

def terminate_instances(private_ips,vxnet_id):
    print("子线程启动")
    print("terminate_instances")
    global conn
    global access_key_id
    global g_instance_id
    global g_ip_resources_is_released

    user_id = get_user_id()
    print("private_ips == %s" %(private_ips))
    print("vxnet_id == %s" %(vxnet_id))

    #terminate_instances
    ret = conn.terminate_instances(instances=[g_instance_id],direct_cease=1)
    print("ret==%s" % (ret))

    time.sleep(5)
    #describe_instances
    ret = conn.describe_instances(offset=0, limit=100, instances=[g_instance_id], owner=user_id)
    print("ret==%s" % (ret))
    ret_code = ret.get("ret_code")
    print("ret_code==%s" % (ret_code))
    if ret_code != 0:
        print("describe_instances failed")
        exit(-1)

    #Check if iP resources are released
    ip_resources_is_released = True
    num = 0
    total_count = 0
    while ip_resources_is_released:
        total_count = get_check_private_ip(vxnet_id,private_ips)
        print("num = %d" % (num))
        print("total_count = %d" % (total_count))
        if total_count == 0:
            g_ip_resources_is_released = True
            break
        num = num + 1
        if num > 300:
            break

    print("total_count = %d" % (total_count))
    print("g_ip_resources_is_released = %d" % (g_ip_resources_is_released))
    print("子线程结束")



def get_check_private_ip(vxnet_id,private_ips):
    print("get_check_private_ip")
    global conn


    user_id = get_user_id()
    print("user_id==%s" %(user_id))
    print("vxnet_id==%s" % (vxnet_id))
    print("private_ips==%s" % (private_ips))

    ret = conn.describe_vxnet_resources(vxnet=vxnet_id, offset=0, limit=100, search_word=private_ips,owner=user_id)
    print("ret==%s" % (ret))
    # check ret_code
    ret_code = ret.get("ret_code")
    print("ret_code==%s" % (ret_code))
    if ret_code != 0:
        print("describe_vxnet_resources failed")
        exit(-1)

    #get total
    total_count = ret.get('total_count')
    print("total_count == %d" %(total_count))
    return total_count

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


    #创建子线程--按照关键字private_ips查询 对应主机是否存在
    t = threading.Thread(target=describe_instances,args=(private_ips,))
    t.start()
    t.join()


    #创建子线程--删除已经绑定private_ips的主机 释放ip资源
    if g_instance_id:
        t1 = threading.Thread(target=terminate_instances,args=(private_ips,vxnet_id,))
        t1.start()
        t1.join()


    print("主线程结束")

