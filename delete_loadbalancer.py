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

def delete_loadbalancer(conn,user_id,loadbalancer_id):
    print("子线程启动")
    print("delete_loadbalancer user_id == %s loadbalancer_id == %s" % (user_id,loadbalancer_id))
    if loadbalancer_id and not isinstance(loadbalancer_id, list):
        loadbalancer_id = [loadbalancer_id]
    print("loadbalancer_id == %s" %(loadbalancer_id))

    # DeleteLoadBalancers
    action = const.ACTION_CREATE_LOADBALANCER
    print("action == %s" % (action))
    ret = conn.delete_loadbalancers(loadbalancers=loadbalancer_id,owner=user_id)
    print("delete_loadbalancers ret == %s" % (ret))
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
            print("delete_loadbalancers successful")
            break
    print("status == %s" % (status))

    if status == "successful":
        print("delete_loadbalancers loadbalancer successful")

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

    opt_parser.add_option("-l", "--loadbalancer_id", action="store", type="string", \
                          dest="loadbalancer_id", help='loadbalancer_id', default="")

    (options, _) = opt_parser.parse_args(sys.argv)

    zone_id = options.zone_id
    access_key_id = options.access_key_id
    secret_access_key = options.secret_access_key
    host = options.host
    port = options.port
    protocol = options.protocol
    vxnet_id = options.vxnet_id
    loadbalancer_id = options.loadbalancer_id

    print("zone_id:%s" % (zone_id))
    print("access_key_id:%s" % (access_key_id))
    print("secret_access_key:%s" % (secret_access_key))
    print("host:%s" % (host))
    print("port:%s" % (port))
    print("protocol:%s" % (protocol))
    print("vxnet_id:%s" % (vxnet_id))
    print("loadbalancer_id:%s" % (loadbalancer_id))

    #连接iaas后台
    conn = Common.connect_iaas(zone_id, access_key_id, secret_access_key, host,port,protocol)
    print("connect_iaas conn == %s" % (conn))

    # 获取账号ID
    user_id = Common.get_user_id(conn,access_key_id)
    print("get_user_id user_id == %s" % (user_id))

    #创建子线程--删除负载均衡器
    t1 = threading.Thread(target=delete_loadbalancer,args=(conn,user_id,loadbalancer_id,))
    t1.start()
    t1.join()

    print("主线程结束")

