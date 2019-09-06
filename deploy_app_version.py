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

# global
zone_id = None
conn=None
access_key_id = None
secret_access_key = None
host = None
port = None
protocol = None
vxnet_id = None

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

def get_vxnet_id():
    print("get_vxnet_id")
    global conn
    #查看基础网络vxnet_id
    ret = conn.describe_vxnets(limit=1, vxnet_type=2)
    print("ret==%s" % (ret))
    # check ret_code
    ret_code = ret.get("ret_code")
    print("ret_code==%s" % (ret_code))
    if ret_code != 0:
        print("describe_vxnets failed")
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
    print("ret==%s" % (ret))
    # check ret_code
    ret_code = ret.get("ret_code")
    print("ret_code==%s" % (ret_code))
    if ret_code != 0:
        print("describe_access_keys failed")
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

def check_ret_code(ret,action):
    ret_code = ret.get("ret_code")
    print("ret_code==%s" % (ret_code))
    if ret_code != 0:
        print("%s failed" %(action))
        exit(-1)


def deploy_app_version(app_ids):
    print("子线程启动")
    print("deploy_app_version")
    global conn
    print("app_ids == %s" % (app_ids))

    if app_ids and not isinstance(app_ids, list):
        app_ids = [app_ids]

    # describe_apps
    action = const.ACTION_DESCRIBE_APPS
    print("action == %s" % (action))
    ret = conn.describe_apps(app_type=["cluster"],app=app_ids[0])
    print("describe_apps ret == %s" % (ret))
    check_ret_code(ret, action)


    # # describe_app_versions
    # print("describe_app_versions app_ids =%s" % (app_ids))
    # ret = conn.describe_app_versions(app_ids=app_ids,limit=1)
    # # check ret_code
    # print("ret==%s" % (ret))
    # ret_code = ret.get("ret_code")
    # print("ret_code==%s" % (ret_code))
    # if ret_code != 0:
    #     print("describe_app_versions failed")
    #     exit(-1)
    #
    # #get version_id
    # version_set = ret['version_set']
    # print("version_set==%s" % (version_set))
    # if version_set is None or len(version_set) == 0:
    #     print("describe_app_versions version_set is None")
    #     exit(-1)
    #
    # for version in version_set:
    #     version_id = version.get("version_id")
    # print("version_id == %s" %(version_id))

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

    opt_parser.add_option("-A", "--app_ids", action="store", type="string", \
                          dest="app_ids", help='appcenter app_ids', default="")

    (options, _) = opt_parser.parse_args(sys.argv)

    zone_id = options.zone_id
    access_key_id = options.access_key_id
    secret_access_key = options.secret_access_key
    host = options.host
    port = options.port
    protocol = options.protocol
    vxnet_id = options.vxnet_id
    app_ids = explode_array(options.app_ids or "")

    print("zone_id:%s" % (zone_id))
    print("access_key_id:%s" % (access_key_id))
    print("secret_access_key:%s" % (secret_access_key))
    print("host:%s" % (host))
    print("port:%s" % (port))
    print("protocol:%s" % (protocol))
    print("vxnet_id:%s" % (vxnet_id))
    print("app_ids:%s" % (app_ids))

    #连接iaas后台
    connect_iaas(zone_id, access_key_id, secret_access_key, host,port,protocol)

    #创建子线程通过appcenter创建postgresql集群 部署指定数据库应用版本的集群
    t = threading.Thread(target=deploy_app_version,args=(app_ids,))
    t.start()
    t.join()

    print("主线程结束")

