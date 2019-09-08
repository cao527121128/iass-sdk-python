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

def get_user_id(conn,access_key_id,secret_access_key_flag=True,access_key_id_flag=True,host_flag=True):
    print("get_user_id")
    user_id = None

    #查看access_keys详情
    try:
        # DescribeAccessKeys
        action = const.ACTION_DESCRIBE_ACCESS_KEYS
        print("action == %s" % (action))
        ret = conn.describe_access_keys(access_keys=[access_key_id])
        print("describe_access_keys ret == %s" % (ret))
        if ret.get("ret_code") == 0:
            access_key_set = ret['access_key_set']
            if access_key_set is None or len(access_key_set) == 0:
                print("describe_access_keys access_key_set is None")
                exit(-1)
            for access_key in access_key_set:
                user_id = access_key.get("owner")
        else:
            if ret.get("message") == "AuthFailure, signature not matched":
                print("AuthFailure, signature not matched")
                secret_access_key_flag = False
            else:
                print("AuthFailure, illegal access key")
                access_key_id_flag = False

    except:

        # host error
        # socket.gaierror: [Errno -2] Name or service not known
        print("socket.gaierror: [Errno -2] Name or service not known")
        # host_flag 写入文件
        host_flag = False

    finally:
        print("secret_access_key_flag == %s" % (secret_access_key_flag))
        print("access_key_id_flag == %s" % (access_key_id_flag))
        print("host_flag == %s" % (host_flag))

        # secret_access_key_flag 写入文件
        secret_access_key_conf = "/opt/secret_access_key_conf"
        with open(secret_access_key_conf, "w+") as f1:
            f1.write("SECRET_ACCESS_KEY_FLAG %s" % (secret_access_key_flag))

        # access_key_id_flag 写入文件
        access_key_id_conf = "/opt/access_key_id_conf"
        with open(access_key_id_conf, "w+") as f1:
            f1.write("ACCESS_KEY_ID_FLAG %s" % (access_key_id_flag))

        # host_flag 写入文件
        host_conf = "/opt/host_conf"
        with open(host_conf, "w+") as f1:
            f1.write("HOST_FLAG %s" % (host_flag))

        return user_id

def check_zone_id_parameter(conn,resource_type,user_id,zone_id_flag=True):
    print("check_zone_id_parameter")

    # 调用用户配额剩余 以检查zone_id是否正确
    # DescribeAccessKeys
    action = const.ACTION_GET_QUOTA_LEFT
    print("action == %s" % (action))
    ret = conn.get_quota_left(resource_types=[resource_type], owner=user_id)
    print("get_quota_left ret == %s" % (ret))
    if ret.get("ret_code") == 1400:
        message = ret.get("message")
        test_message = 'PermissionDenied, access denied for zone'
        result = test_message in message
        print("result == %s" % (result))
        if result == True:
            zone_id_flag = False

    print("zone_id_flag == %s" % (zone_id_flag))
    # zone_id_flag 写入文件
    zone_id_conf = "/opt/zone_id_conf"
    with open(zone_id_conf, "w+") as f1:
        f1.write("ZONE_ID_FLAG %s" % (zone_id_flag))

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

    (options, _) = opt_parser.parse_args(sys.argv)
    zone_id = options.zone_id
    access_key_id = options.access_key_id
    secret_access_key = options.secret_access_key
    host = options.host
    port = options.port
    protocol = options.protocol
    print("zone_id:%s" % (zone_id))
    print("access_key_id:%s" % (access_key_id))
    print("secret_access_key:%s" % (secret_access_key))
    print("host:%s" % (host))
    print("port:%s" % (port))
    print("protocol:%s" % (protocol))

    #连接iaas后台
    conn = Common.connect_iaas(zone_id, access_key_id, secret_access_key, host,port,protocol)
    print("connect_iaas conn == %s" % (conn))

    # 获取账号ID
    user_id = get_user_id(conn,access_key_id)
    print("get_user_id user_id == %s" % (user_id))

    # user_id 写入文件
    user_id_conf = "/opt/user_id_conf"
    with open(user_id_conf, "w+") as f1:
        f1.write("USER_ID %s" % (user_id))

    if user_id:
        #check zone parameter if correct
        check_zone_id_parameter(conn,'rdb',user_id)

    print("主线程结束")

