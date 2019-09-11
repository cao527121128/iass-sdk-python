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

def leave_vxnet(conn,user_id,instance_id):
    print("leave_vxnet user_id == %s instance_id == %s" %(user_id,instance_id))
    if instance_id and not isinstance(instance_id, list):
        instance_id = [instance_id]

    vxnet_id = None
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

    if not vxnet_id:
        print("describe_instances no vxnet")
        return None

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

def terminate_instances(conn,user_id,instance_id):
    print("terminate_instances user_id == %s instance_id == %s" % (user_id,instance_id))
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

    opt_parser.add_option("-l", "--instance_id", action="store", type="string", \
                          dest="instance_id", help='instance_id', default="")

    (options, _) = opt_parser.parse_args(sys.argv)

    zone_id = options.zone_id
    access_key_id = options.access_key_id
    secret_access_key = options.secret_access_key
    host = options.host
    port = options.port
    protocol = options.protocol
    instance_id = options.instance_id

    print("zone_id:%s" % (zone_id))
    print("access_key_id:%s" % (access_key_id))
    print("secret_access_key:%s" % (secret_access_key))
    print("host:%s" % (host))
    print("port:%s" % (port))
    print("protocol:%s" % (protocol))
    print("instance_id:%s" % (instance_id))

    #连接iaas后台
    conn = Common.connect_iaas(zone_id, access_key_id, secret_access_key, host,port,protocol)
    print("connect_iaas conn == %s" % (conn))

    # 获取账号ID
    user_id = Common.get_user_id(conn,access_key_id)
    print("get_user_id user_id == %s" % (user_id))

    # 创建子线程--先释放主机的ip资源  离开网络
    t1 = threading.Thread(target=leave_vxnet, args=(conn,user_id,instance_id,))
    t1.start()
    t1.join()

    # 创建子线程--删除主机
    t2 = threading.Thread(target=terminate_instances, args=(conn,user_id,instance_id,))
    t2.start()
    t2.join()

    print("主线程结束")

