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

def leave_vxnet(conn,instance_id,user_id):
    print("leave_vxnet instance_id == %s user_id == %s" %(instance_id,user_id))

    if instance_id and not isinstance(instance_id, list):
        instance_id = [instance_id]
    # DescribeInstances
    action = const.ACTION_DESCRIBE_INSTANCES
    print("action == %s" % (action))
    ret = conn.describe_instances(instances=instance_id,owner=user_id,verbose=1)
    print("describe_instances ret == %s" % (ret))
    Common.check_ret_code(ret,action)

    # get vxnet_id
    instance_set = ret['instance_set']
    if instance_set is None or len(instance_set) == 0:
        print("describe_instances instance_set is None")
        exit(-1)
    for instance in instance_set:
        vxnets = instance.get("vxnets")
        for vxnet in vxnets:
            vxnet_id = vxnet.get("vxnet_id")
            print("vxnet_id == %s" % (vxnet_id))

    # LeaveVxnet
    action = const.ACTION_LEAVE_VXNET
    print("action == %s" % (action))
    ret = conn.leave_vxnet(instances=instance_id,vxnet=vxnet_id,owner=user_id)
    print("leave_vxnet ret == %s" % (ret))
    Common.check_ret_code(ret,action)

    # check job status
    job_id = ret['job_id']
    print("job_id == %s" % (job_id))
    num = 0
    while num < 300:
        num = num + 1
        print("num == %d" % (num))
        time.sleep(1)
        status = Common.get_job_status(conn, job_id)
        if status == "successful":
            print("leave_vxnet successful")
            break
    print("status == %s" % (status))

    return vxnet_id

def get_check_private_ip(vxnet_id,private_ips,user_id):
    print("get_check_private_ip vxnet_id == %s private_ips == %s user_id == %s" %(vxnet_id,private_ips,user_id))

    # DescribeVxnetResources
    action = const.ACTION_DESCRIBE_VXNET_RESOURCES
    print("action == %s" % (action))
    ret = conn.describe_vxnet_resources(vxnet=vxnet_id, offset=0, limit=100, search_word=private_ips, owner=user_id)
    print("describe_vxnet_resources ret == %s" % (ret))
    Common.check_ret_code(ret, action)

    #get total
    total_count = ret.get('total_count')
    print("total_count == %d" %(total_count))
    return total_count

def check_instance_ip_resource_is_released(conn,user_id,instance_id):
    print("check_instance_ip_resource_is_released user_id == %s instance_id == %s" % (user_id,instance_id))

    if instance_id and not isinstance(instance_id, list):
        instance_id = [instance_id]
    ip_resources_is_released = False

    # check ip resources is released
    num = 0
    while num < 300:
        num = num + 1
        print("num == %d" % (num))
        time.sleep(1)
        total_count = get_check_private_ip(vxnet_id, private_ips,user_id)
        if total_count == 0:
            print("ip_resources_is_released successful")
            ip_resources_is_released = True
            break

    print("ip_resources_is_released == %s" % (ip_resources_is_released))
    return ip_resources_is_released

def describe_instances_by_private_ip(conn,user_id,private_ips=None):
    print("describe_instances_by_private_ip user_id == %s private_ips == %s" %(user_id,private_ips))

    instance_id = ""
    # DescribeInstances
    action = const.ACTION_DESCRIBE_INSTANCES
    print("action == %s" % (action))
    ret = conn.describe_instances(offset=0, limit=100, search_word=private_ips, owner=user_id)
    print("describe_instances ret == %s" % (ret))
    Common.check_ret_code(ret,action)

    #get instance_id
    total_count = ret.get('total_count')
    print("total_count == %d" %(total_count))
    if not total_count:
        print("The instances with private_ips:%s is deleted" %(private_ips))
    else:
        print("The instances with private_ips:%s is running" % (private_ips))
        instance_set = ret['instance_set']
        if instance_set is None or len(instance_set) == 0:
            print("describe_instances instance_set is None")
            exit(-1)
        for instance in instance_set:
            instance_id = instance.get("instance_id")

    return instance_id

def terminate_instances(conn,instance_id,user_id,private_ips):
    print("子线程启动")
    print("terminate_instances instance_id == %s user_id == %s" % (instance_id,user_id))

    if instance_id and not isinstance(instance_id, list):
        instance_id = [instance_id]

    # TerminateInstances
    action = const.ACTION_TERMINATE_INSTANCES
    print("action == %s" % (action))
    ret = conn.terminate_instances(instances=instance_id,owner=user_id,direct_cease=1)
    print("terminate_instances ret == %s" % (ret))
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
            print("terminate_instances successful")
            break
    print("status == %s" % (status))

    # Result is written to file
    if status == "successful":
        print("terminate_instances instances successful")
        # Check if iP resources are released
        ret = check_instance_ip_resource_is_released(conn,user_id,instance_id)
        print("check_instance_ip_resource_is_released ret == %s" %(ret))

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

    #按照关键字private_ips查询 对应主机是否存在
    instance_id = describe_instances_by_private_ip(conn,user_id,private_ips)
    if instance_id:
        print("instance with private_ips:%s is running" % (private_ips))
        # 创建子线程--先释放主机的ip资源  离开网络
        t1 = threading.Thread(target=leave_vxnet, args=(conn,instance_id,user_id,))
        t1.start()
        t1.join()

        # 创建子线程--删除已经绑定private_ips的主机
        t2 = threading.Thread(target=terminate_instances, args=(conn,instance_id,user_id,private_ips,))
        t2.start()
        t2.join()

    print("主线程结束")

