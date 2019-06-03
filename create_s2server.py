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
g_s2_server_id = None
g_s2_shared_target_id = None





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

def create_s2server(vxnet_id):
    print("子线程启动")
    print("create_s2server")
    global conn
    global g_s2_server_id

    ret = conn.create_s2_server(
        vxnet=vxnet_id,
        service_type='vnas',
        s2_server_name='vdi-portal-nas',
        s2_server_type=1,
        description='vdi portal nas',
        s2_class=0
    )
    if ret < 0:
        print("create_s2server fail")
        exit(-1)
    print("ret==%s" % (ret))

    #check ret_code
    ret_code = ret.get("ret_code")
    print("ret_code==%s" % (ret_code))
    if ret_code!=0:
        print("create_s2server ret_code is error")
        exit(-1)

    g_s2_server_id = ret.get("s2_server")
    print("g_s2_server_id=%s" % (g_s2_server_id))

    if not g_s2_server_id:
        print("create_s2server fail")
        exit(-1)
    status = "pending"
    num = 0
    while status != "active" and num <= 300:
        time.sleep(1)
        status = get_s2_server_status()
        num = num + 1
        print("num=%d" %(num))

    if status!="active":
        print("create_s2server timeout")
        exit(-1)
    print("子线程结束")




def get_s2_server_status():
    print("get_s2_server_status")
    global conn
    global g_s2_server_id
    ret = conn.describe_s2_servers(s2_servers=[g_s2_server_id],verbose=1)
    if ret < 0:
        print("describe_s2_servers fail")
        exit(-1)
    # print(ret)
    matched_s2_server = ret['s2_server_set']
    print("matched_s2_server==%s"%(matched_s2_server))

    print("************************************")

    wanted_s2_server = matched_s2_server[0]
    print("wanted_s2_server==%s" % (wanted_s2_server))

    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    status = wanted_s2_server.get('status')
    print("status=%s" % (status))
    return status


def get_s2_servers_transition_status():
    print("get_s2_servers_transition_status")
    global conn
    global g_s2_server_id
    global g_s2_shared_target_id

    ret = conn.describe_s2_servers(s2_servers=[g_s2_server_id])
    if ret < 0:
        print("describe_s2_servers fail")
        exit(-1)

    matched_s2_server = ret['s2_server_set']
    print("matched_s2_server==%s"%(matched_s2_server))

    print("************************************")

    wanted_s2_server = matched_s2_server[0]
    print("wanted_s2_server==%s" % (wanted_s2_server))

    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    transition_status = wanted_s2_server.get('transition_status')
    print("transition_status==%s" % (transition_status))
    return transition_status


def get_s2_server_ip():
    print("get_s2_server_ip")
    global conn
    global g_s2_server_id
    ret = conn.describe_s2_servers(s2_servers=[g_s2_server_id], verbose=1)
    if ret < 0:
        print("describe_s2_servers fail")
        exit(-1)
    # print(ret)
    matched_s2_server = ret['s2_server_set']
    print("matched_s2_server==%s"%(matched_s2_server))

    print("************************************")
    wanted_s2_server = matched_s2_server[0]
    print("wanted_s2_server==%s" % (wanted_s2_server))

    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    s2_server_ip = wanted_s2_server.get('private_ip')
    print("s2_server_ip==%s" % (s2_server_ip))
    return s2_server_ip

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


def create_s2_shared_target():
    print("子线程启动")
    print("create_s2_shared_target")
    global conn
    global g_s2_server_id
    global g_s2_shared_target_id
    ret = conn.create_s2_shared_target(
        s2_server_id=g_s2_server_id,
        export_name='/mnt/nas',
        target_type='NFS',
        description='create s2 shared target'
    )
    if ret < 0:
        print("create_s2_shared_target fail")
        exit(-1)
    print("ret==%s" % (ret))
    g_s2_shared_target_id = ret.get("s2_shared_target")
    print("g_s2_shared_target_id==%s" % (g_s2_shared_target_id))
    print("子线程结束")


def update_s2_servers():
    print("子线程启动")
    print("update_s2_servers")
    global conn
    global g_s2_server_id
    global g_s2_shared_target_id

    ret = conn.update_s2_servers(s2_servers=[g_s2_server_id])
    if ret < 0:
        print("update_s2_servers fail")
        exit(-1)
    print("ret==%s" % (ret))
    time.sleep(1)

    transition_status = "updating"
    while transition_status !="":
        time.sleep(1)
        transition_status = get_s2_servers_transition_status()

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

    (options, _) = opt_parser.parse_args(sys.argv)

    zone_id = options.zone_id
    access_key_id = options.access_key_id
    secret_access_key = options.secret_access_key
    host = options.host
    port = options.port
    protocol = options.protocol
    vxnet_id = options.vxnet_id
    print("zone_id:%s" % (zone_id))
    print("access_key_id:%s" % (access_key_id))
    print("secret_access_key:%s" % (secret_access_key))
    print("host:%s" % (host))
    print("port:%s" % (port))
    print("protocol:%s" % (protocol))
    print("vxnet_id:%s" % (vxnet_id))


    #连接iaas后台
    connect_iaas(zone_id, access_key_id, secret_access_key, host,port,protocol)


    #创建子线程--创建共享存储服务器
    t = threading.Thread(target=create_s2server,args=(vxnet_id,))
    t.start()
    t.join()

    #创建子线程--新建共享存储目标
    t2 = threading.Thread(target=create_s2_shared_target)
    t2.start()
    t2.join()

    #创建子线程--更新共享存储服务器的配置信息
    t3 = threading.Thread(target=update_s2_servers)
    t3.start()
    t3.join()

    #s2server 写入文件
    s2server_ip_conf = "/tmp/s2server_ip_conf"
    ret = get_s2_server_ip()
    with open(s2server_ip_conf, "w+") as f1:
        f1.write("S2SERVER_ADDRESS %s" %(ret))

    print("主线程结束")

