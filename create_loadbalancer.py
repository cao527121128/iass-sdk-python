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
eip_id = None
platform = None
g_loadbalancer_id = None
g_loadbalancer_listeners_id = None
eip_addr = None
g_vdi_portal_loadbalancer_ip_flag = False


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

def create_loadbalancer(vxnet_id,eip_id,private_ips):
    print("子线程启动")
    print("create_loadbalancer")
    global conn
    global g_loadbalancer_id

    print("vxnet_id == %s" % (vxnet_id))
    print("eip_id == %s" %(eip_id))
    print("private_ips == %s" % (private_ips))

    if not eip_id:
        print("create_loadbalancer with vxnet_id=%s" %(vxnet_id))
        if not private_ips:
            print("private_ips is null")
            ret = conn.create_loadbalancer(
                vxnet=vxnet_id,
                loadbalancer_name='vdi-portal-loadbalancer',
                loadbalancer_type=0,
                node_count=2,
                mode=1
            )
        else:
            print("private_ips is %s" %(private_ips))
            ret = conn.create_loadbalancer(
                vxnet=vxnet_id,
                private_ip=private_ips,
                loadbalancer_name='vdi-portal-loadbalancer',
                loadbalancer_type=0,
                node_count=2,
                mode=1
            )
    else:
        print("create_loadbalancer with eip_id=%s" % (eip_id))
        ret = conn.create_loadbalancer(
            eips=[eip_id],
            loadbalancer_name='vdi-portal-loadbalancer',
            loadbalancer_type=0,
            node_count=2,
            mode=1
    )


    # check ret_code
    print("ret==%s" % (ret))
    ret_code = ret.get("ret_code")
    print("ret_code==%s" % (ret_code))
    if ret_code != 0:
        print("create_loadbalancer failed")
        exit(-1)

    #get loadbalancer_id
    g_loadbalancer_id = ret.get("loadbalancer_id")
    print("g_loadbalancer_id=%s" %(g_loadbalancer_id))

    #check create_loadbalancer status
    status = "pending"
    num = 0
    while status != "active" and num <= 120:
        time.sleep(1)
        status = get_loadbalancer_status()
        num = num + 1
        print("num=%d" %(num))

    if status!="active":
        print("create_loadbalancer timeout")
        exit(-1)

    print("子线程结束")

def get_loadbalancer_ip():
    print("get_loadbalancer_ip")
    global conn
    global g_loadbalancer_id
    loadbalancer_ip=""
    ret = conn.describe_loadbalancers(loadbalancers=[g_loadbalancer_id],verbose=1)

    # check ret_code
    print("ret==%s" % (ret))
    ret_code = ret.get("ret_code")
    print("ret_code==%s" % (ret_code))
    if ret_code != 0:
        print("describe_loadbalancers failed")
        exit(-1)

    matched_loadbalancer = ret['loadbalancer_set']
    print("matched_loadbalancer==%s"%(matched_loadbalancer))
    if not matched_loadbalancer:
        print("describe_loadbalancers is NULL")
        exit(-1)

    print("************************************")
    wanted_loadbalancer = matched_loadbalancer[0]
    print("wanted_loadbalancer==%s" % (wanted_loadbalancer))

    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    if wanted_loadbalancer.get("vxnet",0):
        vxnet = wanted_loadbalancer['vxnet']
        print("vxnet==%s"%(vxnet))
        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        loadbalancer_ip = vxnet.get('private_ip',0)

    print("loadbalancer_ip=%s" % (loadbalancer_ip))
    return loadbalancer_ip

def get_loadbalancer_status():
    print("get_loadbalancer_status")
    global conn
    global g_loadbalancer_id
    ret = conn.describe_loadbalancers(loadbalancers=[g_loadbalancer_id],verbose=1)

    # check ret_code
    print("ret==%s" % (ret))
    ret_code = ret.get("ret_code")
    print("ret_code==%s" % (ret_code))
    if ret_code != 0:
        print("describe_loadbalancers failed")
        exit(-1)

    matched_loadbalancer = ret['loadbalancer_set']

    wanted_loadbalancer = matched_loadbalancer[0]

    status = wanted_loadbalancer.get('status')
    print("status=%s" % (status))
    return status


def get_loadbalancer_transition_status():
    print("get_loadbalancer_transition_status")
    global conn
    global g_loadbalancer_id
    ret = conn.describe_loadbalancers(loadbalancers=[g_loadbalancer_id], verbose=1)

    # check ret_code
    print("ret==%s" % (ret))
    ret_code = ret.get("ret_code")
    print("ret_code==%s" % (ret_code))
    if ret_code != 0:
        print("describe_loadbalancers failed")
        exit(-1)

    matched_loadbalancer = ret['loadbalancer_set']

    wanted_loadbalancer = matched_loadbalancer[0]

    transition_status = wanted_loadbalancer.get('transition_status')
    print("transition_status=%s" % (transition_status))
    return transition_status




def get_vxnet_id():
    print("get_vxnet_id")
    global conn
    #查看基础网络vxnet_id
    ret = conn.describe_vxnets(limit=1, vxnet_type=2)

    # check ret_code
    print("ret==%s" % (ret))
    ret_code = ret.get("ret_code")
    print("ret_code==%s" % (ret_code))
    if ret_code != 0:
        print("describe_vxnets failed")
        exit(-1)

    matched_vxnet = ret['vxnet_set']
    wanted_vxnet = matched_vxnet[0]
    vxnet_id = wanted_vxnet.get('vxnet_id')
    print("vxnet_id=%s" % (vxnet_id))
    return vxnet_id


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
    wanted_access_key = matched_access_key[0]
    user_id = wanted_access_key.get('owner')
    print("user_id=%s" % (user_id))
    return user_id

def get_eip_id():
    print("get_eip_id")
    global conn
    #查看公网IP
    user_id = get_user_id()
    ret = conn.describe_eips(limit=1, status=['available'], owner=user_id, verbose=1)

    # check ret_code
    print("ret==%s" % (ret))
    ret_code = ret.get("ret_code")
    print("ret_code==%s" % (ret_code))
    if ret_code != 0:
        print("describe_eips failed")
        exit(-1)

    matched_eip = ret['eip_set']
    if  not matched_eip:
        print("matched_eip is null")
        exit(-1)
    wanted_eip = matched_eip[0]
    print("wanted_eip==%s" % (wanted_eip))

    eip_id = wanted_eip['eip_id']
    print("eip_id=%s" % (eip_id))
    return eip_id

def get_eip_addr_by_eip_id(eip_id):
    print("get_eip_addr_by_eip_id")
    global conn
    #查看公网IP
    user_id = get_user_id()
    ret = conn.describe_eips(eips=[eip_id],owner=user_id, verbose=1)

    # check ret_code
    print("ret==%s" % (ret))
    ret_code = ret.get("ret_code")
    print("ret_code==%s" % (ret_code))
    if ret_code != 0:
        print("describe_eips failed")
        exit(-1)

    matched_eip = ret['eip_set']
    print("matched_eip==%s" % (matched_eip))

    print("************************************")
    if  not matched_eip:
        print("get_eip_addr_by_eip_id matched_eip is null")
        exit(-1)
    wanted_eip = matched_eip[0]
    print("wanted_eip==%s" % (wanted_eip))

    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    eip_addr = wanted_eip['eip_addr']
    print("eip_addr=%s" % (eip_addr))
    return eip_addr


def add_loadbalancer_listeners():
    print("子线程启动")
    print("add_loadbalancer_listeners")
    global conn
    global g_loadbalancer_id
    global g_loadbalancer_listeners_id
    global platform
    print("platform==%s" % (platform))
    if platform == "citrix":
        listeners=[
            {"listener_protocol":"http",
             "listener_port":80,
             "backend_protocol":"http",
             "balance_mode":"roundrobin",
             "loadbalancer_listener_name":"http-listener",
             "session_sticky":"insert|1200",
             "forwardfor":1
            },
            {"listener_protocol": "http",
             "listener_port": 9520,
             "backend_protocol": "http",
             "balance_mode": "roundrobin",
             "loadbalancer_listener_name": "websocket",
             "session_sticky": "insert|1200",
             "forwardfor": 1
             },
            {"listener_protocol": "http",
             "listener_port": 10080,
             "backend_protocol": "http",
             "balance_mode": "roundrobin",
             "loadbalancer_listener_name": "citrix",
             "session_sticky": "insert|1200",
             "forwardfor": 1
             }
        ]
    elif platform == "qingcloud":
        listeners = [
            {"listener_protocol": "http",
             "listener_port": 80,
             "backend_protocol": "http",
             "balance_mode": "roundrobin",
             "loadbalancer_listener_name": "http-listener",
             "session_sticky": "insert|1200",
             "forwardfor": 1
             },
            {"listener_protocol": "http",
             "listener_port": 9520,
             "backend_protocol": "http",
             "balance_mode": "roundrobin",
             "loadbalancer_listener_name": "websocket",
             "session_sticky": "insert|1200",
             "forwardfor": 1
             }
        ]
    else:
        print("invalid platform")


    print("listeners==%s" % (listeners))
    ret = conn.add_listeners_to_loadbalancer(
        loadbalancer=g_loadbalancer_id,
        listeners=listeners
    )

    # check ret_code
    print("ret==%s" % (ret))
    ret_code = ret.get("ret_code")
    print("ret_code==%s" % (ret_code))
    if ret_code != 0:
        print("add_listeners_to_loadbalancer failed")
        exit(-1)

    g_loadbalancer_listeners_id = ret.get("loadbalancer_listeners")
    print("g_loadbalancer_listeners_id=%s" % (g_loadbalancer_listeners_id))
    print("子线程结束")

def update_loadbalancers():
    print("子线程启动")
    print("update_loadbalancers")
    global conn
    global g_loadbalancer_id
    user_id = get_user_id()
    ret = conn.update_loadbalancers(
        loadbalancers=[g_loadbalancer_id],
        target_user=user_id
    )

    # check ret_code
    print("ret==%s" % (ret))
    ret_code = ret.get("ret_code")
    print("ret_code==%s" % (ret_code))
    if ret_code != 0:
        print("update_loadbalancers failed")
        exit(-1)

    status = "pending"
    transition_status = "updating"
    while status != "active":
        while transition_status !="":
            time.sleep(1)
            transition_status = get_loadbalancer_transition_status()
        time.sleep(1)
        status = get_loadbalancer_status()

    transition_status = get_loadbalancer_transition_status()
    status = get_loadbalancer_status()
    print("update_loadbalancers transition_status == %s" %(transition_status))
    print("update_loadbalancers status == %s" %(status))
    print("子线程结束")


def add_backends_to_listener(resource_id):
    print("子线程启动")
    print("add_backends_to_listener")
    global conn
    global g_loadbalancer_listeners_id
    for loadbalancer_listener_id in g_loadbalancer_listeners_id:
        ret = conn.describe_loadbalancer_listeners(loadbalancer_listeners=[loadbalancer_listener_id])
        matched_loadbalancer_listener = ret['loadbalancer_listener_set']
        print("matched_loadbalancer_listener=%s" %(matched_loadbalancer_listener))

        print("************************************")
        wanted_loadbalancer_listener = matched_loadbalancer_listener[0]

        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        print("wanted_loadbalancer_listener=%s" %(wanted_loadbalancer_listener))

        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        listener_port = wanted_loadbalancer_listener.get("listener_port")
        print("listener_port=%s" %(listener_port))

        for res_id in resource_id:
            if listener_port == 80:
                backends=[
                    {"resource_id":res_id,
                     "port":80,
                     "weight":"1",
                     "loadbalancer_backend_name":"backend_desktop_server"
                    }
                ]
                print("backends=%s" % (backends))
                ret = conn.add_backends_to_listener(
                                loadbalancer_listener=loadbalancer_listener_id,
                                backends=backends
                            )
                # check ret_code
                print("ret==%s" % (ret))
                ret_code = ret.get("ret_code")
                print("ret_code==%s" % (ret_code))
                if ret_code != 0:
                    print("add_backends_to_listener failed")
                    exit(-1)


            elif listener_port == 9520:
                backends=[
                    {"resource_id":res_id,
                     "port":9520,
                     "weight":"1",
                     "loadbalancer_backend_name":"backend_desktop_server"
                    }
                ]
                print("backends=%s" % (backends))
                ret = conn.add_backends_to_listener(
                                loadbalancer_listener=loadbalancer_listener_id,
                                backends=backends
                            )
                # check ret_code
                print("ret==%s" % (ret))
                ret_code = ret.get("ret_code")
                print("ret_code==%s" % (ret_code))
                if ret_code != 0:
                    print("add_backends_to_listener failed")
                    exit(-1)

            elif listener_port == 10080:
                backends=[
                    {"resource_id":res_id,
                     "port":10080,
                     "weight":"1",
                     "loadbalancer_backend_name":"backend_desktop_server"
                    }
                ]
                print("backends=%s" % (backends))
                # ret = conn.add_backends_to_listener(
                #                 loadbalancer_listener=loadbalancer_listener_id,
                #                 backends=backends
                #             )
                # if ret < 0:
                #     print("add_backends_to_listener fail")
                #     exit(-1)
                # print("ret==%s" % (ret))
            else:
                print("invalid listener_port")
                exit(-1)

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


def check_loadbalancer(vdi_portal_loadbalancer_ip):
    print("子线程启动")
    print("check_loadbalancer")
    global conn
    global g_vdi_portal_loadbalancer_ip_flag
    global g_loadbalancer_id

    user_id = get_user_id()
    print("user_id==%s" %(user_id))
    print("vdi_portal_loadbalancer_ip==%s" % (vdi_portal_loadbalancer_ip))

    ret = conn.describe_loadbalancers(offset=0, limit=100, search_word=vdi_portal_loadbalancer_ip,owner=user_id)
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
    if not total_count:
        g_vdi_portal_loadbalancer_ip_flag = False
        print("total_count == %d" % (total_count))
        print("vdi_portal_loadbalancer_ip:%s is not exist" %(vdi_portal_loadbalancer_ip))
        print("you need create new loadbalancer")

    else:
        g_vdi_portal_loadbalancer_ip_flag = True
        print("total_count == %d" % (total_count))
        print("vdi_portal_loadbalancer_ip:%s is exist" %(vdi_portal_loadbalancer_ip))
        print("no need recreate loadbalancer")
        #get loadbalancer_id
        matched_loadbalancer = ret['loadbalancer_set']
        wanted_loadbalancer = matched_loadbalancer[0]
        g_loadbalancer_id = wanted_loadbalancer.get('loadbalancer_id')
        print("g_loadbalancer_id=%s" % (g_loadbalancer_id))

        #DescribeLoadBalancerListeners
        print("DescribeLoadBalancerListeners")
        ret = conn.describe_loadbalancer_listeners(loadbalancer=g_loadbalancer_id, offset=0, limit=50, verbose=1)
        print("ret==%s" % (ret))
        # check ret_code
        ret_code = ret.get("ret_code")
        print("ret_code==%s" % (ret_code))
        if ret_code != 0:
            print("describe_loadbalancer_listeners failed")
            exit(-1)
        # get total
        total_count = ret.get('total_count')
        print("total_count == %d" % (total_count))

        matched_loadbalancer_listener = ret['loadbalancer_listener_set']
        num = 0
        while num < total_count:
            print("num == %d" %(num))
            loadbalancer_listener_id = None
            wanted_loadbalancer_listener = matched_loadbalancer_listener[num]
            loadbalancer_listener_id = wanted_loadbalancer_listener.get("loadbalancer_listener_id")
            num = num + 1

            if loadbalancer_listener_id:
                # DeleteLoadBalancerListeners
                ret = conn.delete_loadbalancer_listeners(loadbalancer_listeners=[loadbalancer_listener_id])
                print("ret==%s" % (ret))
                # check ret_code
                ret_code = ret.get("ret_code")
                print("ret_code==%s" % (ret_code))
                if ret_code != 0:
                    print("delete_loadbalancer_listeners failed")
                    exit(-1)

        #UpdateLoadBalancers
        print("UpdateLoadBalancers")
        ret = conn.update_loadbalancers(
            loadbalancers=[g_loadbalancer_id],
            target_user=user_id
        )

        # check ret_code
        print("ret==%s" % (ret))
        ret_code = ret.get("ret_code")
        print("ret_code==%s" % (ret_code))
        if ret_code != 0:
            print("update_loadbalancers failed")
            exit(-1)

        status = "pending"
        transition_status = "updating"
        while status != "active":
            while transition_status != "":
                time.sleep(1)
                transition_status = get_loadbalancer_transition_status()
            time.sleep(1)
            status = get_loadbalancer_status()
        transition_status = get_loadbalancer_transition_status()
        status = get_loadbalancer_status()
        print("update_loadbalancers transition_status == %s" %(transition_status))
        print("update_loadbalancers status == %s" %(status))
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
    opt_parser.add_option("-e", "--eip_id", action="store", type="string", \
                          dest="eip_id", help='eip id', default="")
    opt_parser.add_option("-r", "--resource_id", action="store", type="string", \
                          dest="resource_id", help='resource id', default="")
    opt_parser.add_option("-F", "--platform", action="store", type="string", \
                          dest="platform", help='platform', default="")

    opt_parser.add_option("-m", "--private_ips", action="store", type="string", \
                          dest="private_ips", help='private ips', default="")

    opt_parser.add_option("-l", "--vdi_portal_loadbalancer_ip", action="store", type="string", \
                          dest="vdi_portal_loadbalancer_ip", help='vdi_portal loadbalancer ip', default="")



    (options, _) = opt_parser.parse_args(sys.argv)
    zone_id = options.zone_id
    access_key_id = options.access_key_id
    secret_access_key = options.secret_access_key
    host = options.host
    port = options.port
    protocol = options.protocol
    vxnet_id = options.vxnet_id
    eip_id = options.eip_id
    resource_id = explode_array(options.resource_id or "")
    if not options.platform:
        platform = "qingcloud"
    else:
        platform = options.platform
    private_ips = options.private_ips
    vdi_portal_loadbalancer_ip = options.vdi_portal_loadbalancer_ip
    print("zone_id:%s" % (zone_id))
    print("access_key_id:%s" % (access_key_id))
    print("secret_access_key:%s" % (secret_access_key))
    print("host:%s" % (host))
    print("port:%s" % (port))
    print("protocol:%s" % (protocol))
    print("vxnet_id:%s" % (vxnet_id))
    print("eip_id:%s" % (eip_id))
    print("resource_id:%s" % (resource_id))
    print("platform:%s" % (platform))
    print("private_ips:%s" % (private_ips))
    print("vdi_portal_loadbalancer_ip:%s" % (vdi_portal_loadbalancer_ip))

    #连接iaas后台
    connect_iaas(zone_id, access_key_id, secret_access_key, host,port,protocol)



    #获取eip_id
    if eip_id:
        print("eip_id==%s" %(eip_id))
        print("Loadbalancer will use eip ip")
        # 获取eip_addr
        eip_addr = get_eip_addr_by_eip_id(eip_id)
        print("eip_addr==%s" % (eip_addr))
    else:
        print("eip_id is None")
        print("Loadbalancer will use vxnet ip")
        # 获取vxnet_id
        if vxnet_id:
            print("vxnet_id==%s" % (vxnet_id))
        else:
            vxnet_id = get_vxnet_id()
            print("vxnet_id==%s" % (vxnet_id))

    if vdi_portal_loadbalancer_ip:
        #创建子线程--检测负载均衡器是否已经存在
        t = threading.Thread(target=check_loadbalancer,args=(vdi_portal_loadbalancer_ip,))
        t.start()
        t.join()



    if not g_vdi_portal_loadbalancer_ip_flag:
        print("loadbalancer is not exist,you need create new loadbalancer")
        #创建子线程--创建负载均衡器
        t1 = threading.Thread(target=create_loadbalancer,args=(vxnet_id,eip_id,private_ips,))
        t1.start()
        t1.join()



    #创建子线程--添加负载均衡器监听器
    t2 = threading.Thread(target=add_loadbalancer_listeners)
    t2.start()
    t2.join()



    #创建子线程--更新负载均衡器：使添加的监听器生效
    t3 = threading.Thread(target=update_loadbalancers)
    t3.start()
    t3.join()



    # 创建子线程--添加负载均衡器监听器后端服务
    t4 = threading.Thread(target=add_backends_to_listener, args=(resource_id,))
    t4.start()
    t4.join()


    #创建子线程--更新负载均衡器:使监听器添加的后端服务生效
    t5 = threading.Thread(target=update_loadbalancers)
    t5.start()
    t5.join()

    #check loadbalancer ip
    if not eip_addr:
        loadbalancer_ip = get_loadbalancer_ip()
    else:
        loadbalancer_ip = eip_addr

    print("loadbalancer_ip=%s" %(loadbalancer_ip))
    #loadbalancer_ip 写入文件
    loadbalancer_ip_conf = "/opt/loadbalancer_ip_conf"
    with open(loadbalancer_ip_conf, "w+") as f1:
        f1.write("LOADBALANCER_IP %s" %(loadbalancer_ip))

    print("主线程结束")

