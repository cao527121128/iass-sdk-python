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

def delete_s2server(conn,user_id,s2_servers_id):
    print("子线程启动")
    print("delete_s2server user_id == %s s2_servers_id == %s" % (user_id,s2_servers_id))
    if s2_servers_id and not isinstance(s2_servers_id, list):
        s2_servers_id = [s2_servers_id]
    print("s2_servers_id == %s" %(s2_servers_id))

    # DeleteS2Servers
    action = const.ACTION_DELETE_S2_SERVERS
    print("action == %s" % (action))
    ret = conn.delete_s2_servers(s2_servers=s2_servers_id,owner=user_id)
    print("delete_s2_servers ret == %s" % (ret))
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
            print("delete_s2_servers successful")
            break
    print("status == %s" % (status))

    if status == "successful":
        print("delete_s2_servers s2_servers successful")

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

    opt_parser.add_option("-l", "--s2_servers_id", action="store", type="string", \
                          dest="s2_servers_id", help='s2_servers_id', default="")

    (options, _) = opt_parser.parse_args(sys.argv)

    zone_id = options.zone_id
    access_key_id = options.access_key_id
    secret_access_key = options.secret_access_key
    host = options.host
    port = options.port
    protocol = options.protocol
    s2_servers_id = options.s2_servers_id

    print("zone_id:%s" % (zone_id))
    print("access_key_id:%s" % (access_key_id))
    print("secret_access_key:%s" % (secret_access_key))
    print("host:%s" % (host))
    print("port:%s" % (port))
    print("protocol:%s" % (protocol))
    print("s2_servers_id:%s" % (s2_servers_id))

    #连接iaas后台
    conn = Common.connect_iaas(zone_id, access_key_id, secret_access_key, host,port,protocol)
    print("connect_iaas conn == %s" % (conn))

    # 获取账号ID
    user_id = Common.get_user_id(conn,access_key_id)
    print("get_user_id user_id == %s" % (user_id))

    #创建子线程--删除共享存储服务
    t1 = threading.Thread(target=delete_s2server,args=(conn,user_id,s2_servers_id,))
    t1.start()
    t1.join()

    print("主线程结束")

