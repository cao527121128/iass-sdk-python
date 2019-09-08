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

def describe_apps(conn,user_id,app_ids):
    print("子线程启动")
    print("describe_apps")

    app_type = ['cluster']
    if app_ids and not isinstance(app_ids, list):
        app_ids = [app_ids]
    print("app_ids == %s" %(app_ids))
    print("app_type == %s" % (app_type))

    for app_id in app_ids:
        # DescribeApps
        action = const.ACTION_DESCRIBE_APPS
        print("action == %s" % (action))
        ret = conn.describe_apps(app=app_id,app_type=app_type)
        print("describe_apps ret == %s" % (ret))
        Common.check_ret_code(ret, action)
        #get total
        total_count = ret.get('total_count')
        print("total_count == %d" %(total_count))

        if app_id == const.POSTGRESQL_APP_IDS:
            if total_count:
                print("appcenter postgresql app %s is available" % (app_id))
                appcenter_postgreql_status = True
            else:
                print("appcenter postgresql app %s isn't available" % (app_id))
                appcenter_postgreql_status = False
            # appcenter_postgreql_status 写入文件
            appcenter_postgreql_status_conf = "/opt/appcenter_postgreql_status_conf"
            with open(appcenter_postgreql_status_conf, "w+") as f1:
                f1.write("APPCENTER_POSTGRESQL_STATUS %s" % (appcenter_postgreql_status))

        elif app_id == const.MEMCACHED_APP_IDS:
            if total_count:
                print("appcenter memcached app %s is available" % (app_id))
                appcenter_memcached_status = True
            else:
                print("appcenter memcached app %s isn't available" % (app_id))
                appcenter_memcached_status = False
            # appcenter_memcached_status 写入文件
            appcenter_memcached_status_conf = "/opt/appcenter_memcached_status_conf"
            with open(appcenter_memcached_status_conf, "w+") as f1:
                f1.write("APPCENTER_MEMCACHED_STATUS %s" % (appcenter_memcached_status))

        else:
            print("app_id %s is unsupport" % (app_id))

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

    opt_parser.add_option("-A", "--app_ids", action="store", type="string", \
                          dest="app_ids", help='appcenter app_ids', default="")

    (options, _) = opt_parser.parse_args(sys.argv)
    zone_id = options.zone_id
    access_key_id = options.access_key_id
    secret_access_key = options.secret_access_key
    host = options.host
    port = options.port
    protocol = options.protocol
    app_ids = Common.explode_array(options.app_ids or "")

    print("zone_id:%s" % (zone_id))
    print("access_key_id:%s" % (access_key_id))
    print("secret_access_key:%s" % (secret_access_key))
    print("host:%s" % (host))
    print("port:%s" % (port))
    print("protocol:%s" % (protocol))
    print("app_ids:%s" % (app_ids))

    #连接iaas后台
    conn = Common.connect_iaas(zone_id, access_key_id, secret_access_key, host,port,protocol)
    print("connect_iaas conn == %s" % (conn))

    # 获取账号ID
    user_id = Common.get_user_id(conn,access_key_id)
    print("get_user_id user_id == %s" % (user_id))

    #创建子线程--Check if the appcenter postgresql and memcached app is available
    t = threading.Thread(target=describe_apps,args=(conn,user_id,app_ids,))
    t.start()
    t.join()

    print("主线程结束")

