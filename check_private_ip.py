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

def check_private_ip(conn,user_id,private_ips=None):
    print("check_private_ip user_id == %s private_ips == %s" %(user_id,private_ips))

    # DescribeNics
    action = const.ACTION_DESCRIBE_NICS
    print("action == %s" % (action))
    ret = conn.describe_nics(offset=0, limit=100, search_word=private_ips, owner=user_id,status=["in-use", "available"])
    print("describe_nics ret == %s" % (ret))
    Common.check_ret_code(ret,action)

    #get total
    total_count = ret.get('total_count')
    print("total_count == %d" %(total_count))
    if not total_count:
        print("total_count is  0")
        print("private_ips:%s is available" %(private_ips))
        return True
    else:
        return False

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
    private_ips = options.private_ips or ""
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

    ret = check_private_ip(conn,user_id,private_ips)
    if not ret:
        print("private_ips:%s is in-use" % (private_ips))
        g_private_ips_status = "in-use"
    else:
        print("private_ips:%s is available" % (private_ips))
        g_private_ips_status = "available"

    print("g_private_ips_status:%s" % (g_private_ips_status))
    # g_private_ips_status 写入文件
    private_ips_status_conf = "/opt/private_ips_status_conf"
    with open(private_ips_status_conf, "w+") as f1:
        f1.write("PRIVATE_IPS_STATUS %s" % (g_private_ips_status))

    print("主线程结束")

