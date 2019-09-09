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

def get_instance_vxnet_id(conn,resource_id):
    print("get_instance_vxnet_id resource_id == %s" % (resource_id))
    if resource_id and not isinstance(resource_id, list):
        resource_id = [resource_id]
    print("resource_id == %s" %(resource_id))
    vxnet_id = ""

    # DescribeInstances
    action = const.ACTION_DESCRIBE_INSTANCES
    print("action == %s" % (action))
    ret = conn.describe_instances(instances=resource_id, verbose=1)
    print("describe_instances ret == %s" % (ret))
    Common.check_ret_code(ret, action)

    instance_set = ret['instance_set']
    if instance_set is None or len(instance_set) == 0:
        print("describe_instances instance_set is None")
        exit(-1)
    for instance in instance_set:
        vxnets = instance.get("vxnets")
        for vxnet in vxnets:
            vxnet_id = vxnet.get("vxnet_id")

    return vxnet_id

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

    opt_parser.add_option("-r", "--resource_id", action="store", type="string", \
                          dest="resource_id", help='resource id', default="")

    (options, _) = opt_parser.parse_args(sys.argv)
    zone_id = options.zone_id
    access_key_id = options.access_key_id
    secret_access_key = options.secret_access_key
    host = options.host
    port = options.port
    protocol = options.protocol
    resource_id = options.resource_id
    print("zone_id:%s" % (zone_id))
    print("access_key_id:%s" % (access_key_id))
    print("secret_access_key:%s" % (secret_access_key))
    print("host:%s" % (host))
    print("port:%s" % (port))
    print("protocol:%s" % (protocol))
    print("resource_id:%s" % (resource_id))

    #连接iaas后台
    conn = Common.connect_iaas(zone_id, access_key_id, secret_access_key, host,port,protocol)
    print("connect_iaas conn == %s" % (conn))

    instance_vxnet_id = get_instance_vxnet_id(conn,resource_id)
    print("get_instance_vxnet_id instance_vxnet_id=%s" %(instance_vxnet_id))

    if instance_vxnet_id:
        # instance_vxnet_id 写入文件
        instance_vxnet_id_conf = "/opt/instance_vxnet_id_conf"
        with open(instance_vxnet_id_conf, "w+") as f1:
            f1.write("INSTANCE_VXNET_ID %s" % (instance_vxnet_id))

    print("主线程结束")

