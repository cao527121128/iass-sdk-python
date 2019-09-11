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

def get_s2server_ip(conn,user_id,s2_servers_id):
    print("get_s2server_ip user_id == %s s2_servers_id == %s" %(user_id,s2_servers_id))
    private_ip = None

    if s2_servers_id and not isinstance(s2_servers_id, list):
        s2_servers_id = [s2_servers_id]
    print("s2_servers_id == %s" % (s2_servers_id))

    # DescribeS2Servers
    action = const.ACTION_DESCRIBE_S2_SERVERS
    print("action == %s" % (action))
    ret = conn.describe_s2_servers(owner=user_id,s2_servers=s2_servers_id,verbose=1)
    print("describe_s2_servers ret == %s" % (ret))
    Common.check_ret_code(ret, action)

    # get private_ip
    s2_server_set = ret['s2_server_set']
    if s2_server_set is None or len(s2_server_set) == 0:
        print("describe_s2_servers s2_server_set is None")
        exit(-1)
    for s2_server in s2_server_set:
        private_ip = s2_server.get("private_ip")

    return private_ip

def update_s2_servers(conn,user_id,s2_servers_id):
    print("update_s2_servers user_id == %s s2_servers_id == %s" %(user_id,s2_servers_id))

    if s2_servers_id and not isinstance(s2_servers_id, list):
        s2_servers_id = [s2_servers_id]
    print("s2_servers_id == %s" % (s2_servers_id))

    # UpdateS2Servers
    action = const.ACTION_UPDATE_S2_SERVERS
    print("action == %s" % (action))
    ret = conn.update_s2_servers(owner=user_id,s2_servers=s2_servers_id)
    print("update_s2_servers ret == %s" % (ret))
    Common.check_ret_code(ret, action)

    job_id = ret['job_id']
    print("job_id == %s" % (job_id))
    # check job status
    num = 0
    while num < 300:
        num = num + 1
        print("num == %d" % (num))
        time.sleep(1)
        status = Common.get_job_status(conn, job_id)
        if status == "successful":
            print("update_s2_servers successful")
            break
    print("status == %s" % (status))

    # Result is written to file
    if status == "successful":
        print("update_s2_servers s2_servers successful")
        #s2server_ip 写入文件
        s2server_ip_conf = "/opt/s2server_ip_conf"
        s2server_ip = get_s2server_ip(conn,user_id,s2_servers_id)
        print("get_s2server_ip s2server_ip == %s" %(s2server_ip))
        if s2server_ip:
            with open(s2server_ip_conf, "w+") as f1:
                f1.write("S2SERVER_ADDRESS %s" %(s2server_ip))
    print("子线程结束")

    return None

def create_s2_account_vdi_host(conn,user_id,g_vdi_ip_list):
    print("create_s2_account_vdi_host user_id == %s g_vdi_ip_list == %s" %(user_id,g_vdi_ip_list))
    s2_account_id_list = []

    for vdi_ip in g_vdi_ip_list:
        print("vdi_ip == %s" %(vdi_ip))

        # DescribeS2Groups
        action = const.ACTION_DESCRIBE_S2_GROUPS
        print("action == %s" % (action))
        ret = conn.describe_s2_groups(owner=user_id,offset=0,limit=1,verbose=1,group_types=['NFS_GROUP'])
        print("describe_s2_groups ret == %s" % (ret))
        Common.check_ret_code(ret, action)

        # get s2_group_id
        s2_group_set = ret['s2_group_set']
        if s2_group_set is None or len(s2_group_set) == 0:
            print("describe_s2_groups s2_group_set is None")
            exit(-1)
        for s2_group in s2_group_set:
            s2_group_id = s2_group.get("group_id")
        print("s2_group_id == %s" % (s2_group_id))

        # CreateS2Account
        action = const.ACTION_CREATE_S2_ACCOUNT
        print("action == %s" % (action))
        s2_groups_list = [{"group_id":s2_group_id,"rw_flag":"rw"}]
        print("s2_groups_list == %s" % (s2_groups_list))
        ret = conn.create_s2_account(owner=user_id,account_name='vdi-portal-account',account_type='NFS',nfs_ipaddr=vdi_ip,s2_group=s2_group_id,opt_parameters='squash=no_root_squash,sync=sync',s2_groups=s2_groups_list)
        print("create_s2_account ret == %s" % (ret))
        ret_code = ret.get("ret_code")
        if ret_code != 0:
            print("%s failed" % (action))
            continue

        # get s2_account_id
        s2_account_id = ret.get("s2_account_id")
        if s2_account_id not in s2_account_id_list:
            s2_account_id_list.append(s2_account_id)

    print("s2_account_id_list == %s" % (s2_account_id_list))
    return None

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

    opt_parser.add_option("-i", "--s2_server_id", action="store", type="string", \
                          dest="s2_server_id", help='s2_server_id', default="")

    opt_parser.add_option("-d", "--vdi_ip", action="store", type="string", \
                          dest="vdi_ip", help='vdi ip', default="")

    (options, _) = opt_parser.parse_args(sys.argv)

    zone_id = options.zone_id
    access_key_id = options.access_key_id
    secret_access_key = options.secret_access_key
    host = options.host
    port = options.port
    protocol = options.protocol
    s2_server_id = options.s2_server_id
    vdi_ip = options.vdi_ip

    print("zone_id:%s" % (zone_id))
    print("access_key_id:%s" % (access_key_id))
    print("secret_access_key:%s" % (secret_access_key))
    print("host:%s" % (host))
    print("port:%s" % (port))
    print("protocol:%s" % (protocol))
    print("s2_server_id:%s" % (s2_server_id))
    print("vdi_ip:%s" % (vdi_ip))

    #连接iaas后台
    conn = Common.connect_iaas(zone_id, access_key_id, secret_access_key, host,port,protocol)
    print("connect_iaas conn == %s" % (conn))

    # 获取账号ID
    user_id = Common.get_user_id(conn,access_key_id)
    print("get_user_id user_id == %s" % (user_id))


    #创建子线程--创建vnas服务访问资源账号 vdi客户端
    t3 = threading.Thread(target=create_s2_account_vdi_host,args=(conn,user_id,[vdi_ip],))
    t3.start()
    t3.join()

    #创建子线程--更新共享存储服务器的配置信息
    t4 = threading.Thread(target=update_s2_servers,args=(conn,user_id,s2_server_id,))
    t4.start()
    t4.join()

    print("主线程结束")

