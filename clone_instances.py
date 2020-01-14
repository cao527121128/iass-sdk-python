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

def clone_instances(conn,user_id,resource_id,vxnet_id,private_ips=None):
    print("子线程启动")
    print("clone_instances user_id == %s resource_id == %s vxnet_id == %s private_ips == %s" % (user_id,resource_id,vxnet_id,private_ips))
    if resource_id and not isinstance(resource_id, list):
        resource_id = [resource_id]
    print("resource_id == %s" %(resource_id))

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
        cloned_instance_ip_conf = "/opt/cloned_instance_ip_conf"
        with open(cloned_instance_ip_conf, "w+") as f1:
            f1.write("CLONED_INSTANCE_IP %s" % (cloned_instance_ip))

        # cloned_instance_id 写入文件
        print("cloned_instance_id == %s" % (cloned_instance_id))
        cloned_instance_id_conf = "/opt/cloned_instance_id_conf"
        with open(cloned_instance_id_conf, "w+") as f2:
            f2.write("CLONED_INSTANCE_ID %s" % (cloned_instance_id))

        # attach tags
        current_time = time.strftime("%Y-%m-%d", time.localtime())
        tag_name = '桌面云服务器VDI1 %s' %(current_time)
        Common.attach_tags_to_resource(conn,user_id=user_id,tag_name=tag_name,resource_type='instance',resource_id=cloned_instance_id)
        tag_name = '桌面云服务器VDI0 %s' % (current_time)
        Common.attach_tags_to_resource(conn, user_id=user_id,tag_name=tag_name, resource_type='instance',resource_id=resource_id[0])

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

    print("zone_id:%s" % (zone_id))
    print("access_key_id:%s" % (access_key_id))
    print("secret_access_key:%s" % (secret_access_key))
    print("host:%s" % (host))
    print("port:%s" % (port))
    print("protocol:%s" % (protocol))
    print("vxnet_id:%s" % (vxnet_id))
    print("resource_id:%s" % (resource_id))
    print("private_ips:%s" % (private_ips))

    #连接iaas后台
    conn = Common.connect_iaas(zone_id, access_key_id, secret_access_key, host,port,protocol)
    print("connect_iaas conn == %s" % (conn))

    # 获取账号ID
    user_id = Common.get_user_id(conn,access_key_id)
    print("get_user_id user_id == %s" % (user_id))

    #创建子线程--克隆主机
    t1 = threading.Thread(target=clone_instances,args=(conn,user_id,resource_id,vxnet_id,private_ips,))
    t1.start()
    t1.join()

    print("主线程结束")

