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

def get_rdb_master_ip(conn,user_id,rdb_id):
    print("get_rdb_master_ip user_id == %s rdb_id == %s" % (user_id,rdb_id))
    if rdb_id and not isinstance(rdb_id, list):
        rdb_id = [rdb_id]
    print("rdb_id == %s" %(rdb_id))
    master_ip = None

    # DescribeRDBs
    action = const.ACTION_DESCRIBE_RDBS
    print("action == %s" % (action))
    ret = conn.describe_rdbs(owner=user_id,rdbs=rdb_id,verbose=1)
    print("describe_rdbs ret == %s" % (ret))
    Common.check_ret_code(ret, action)

    rdb_set = ret['rdb_set']
    if rdb_set is None or len(rdb_set) == 0:
        print("describe_rdbs rdb_set is None")
        exit(-1)
    for rdb in rdb_set:
        master_ip = rdb.get("master_ip")

    return master_ip

def create_rdb(conn,user_id,vxnet_id,master_private_ip,topslave_private_ip):
    print("子线程启动")
    print("create_rdb user_id == %s vxnet_id == %s master_private_ip == %s topslave_private_ip == %s" % (user_id,vxnet_id,master_private_ip,topslave_private_ip))

    if not master_private_ip:
        print("master_private_ip is None")
        # CreateRDB
        action = const.ACTION_CREATE_RDB
        print("action == %s" % (action))
        ret = conn.create_rdb(owner=user_id,vxnet=vxnet_id,rdb_engine='psql',engine_version='9.4',rdb_username='yunify',rdb_password='Zhu88jie',rdb_type=2,storage_size=10,rdb_name='vdi-portal-postgresql')
        print("create_rdb ret == %s" % (ret))
        Common.check_ret_code(ret, action)
    else:
        print("master_private_ip is %s" %(master_private_ip))
        # CreateRDB
        action = const.ACTION_CREATE_RDB
        print("action == %s" % (action))
        private_ips_list = {"master":master_private_ip,"topslave":topslave_private_ip}
        print("private_ips_list == %s" %(private_ips_list))
        ret = conn.create_rdb(owner=user_id,vxnet=vxnet_id,rdb_engine='psql',engine_version='9.4',rdb_username='yunify',rdb_password='Zhu88jie',rdb_type=2,storage_size=10,rdb_name='vdi-portal-postgresql',private_ips=[private_ips_list])
        print("create_rdb ret == %s" % (ret))
        Common.check_ret_code(ret, action)

    job_id = ret['job_id']
    rdb_id = ret['rdb']
    print("job_id == %s" % (job_id))
    print("rdb_id == %s" % (rdb_id))
    # check job status
    num = 0
    while num < 300:
        num = num + 1
        print("num == %d" % (num))
        time.sleep(1)
        status = Common.get_job_status(conn,job_id)
        if status == "successful":
            print("create_rdb successful")
            break
    print("status == %s" % (status))

    if status == "successful":
        print("create_rdb rdb successful")

        #create_rdb ok
        create_rdb_status = "True"
        # create_rdb_status 写入文件
        create_rdb_status_conf = "/opt/create_rdb_status_conf"
        with open(create_rdb_status_conf, "w+") as f1:
            f1.write("CREATE_RDB_STATUS %s" % (create_rdb_status))

        #master_ip 写入文件
        master_ip_conf = "/opt/master_ip_conf"
        master_ip = get_rdb_master_ip(conn,user_id,rdb_id)
        print("get_rdb_master_ip master_ip == %s" %(master_ip))
        if master_ip:
            with open(master_ip_conf, "w+") as f2:
                f2.write("POSTGRESQL_ADDRESS %s" %(master_ip))

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

    opt_parser.add_option("-m", "--master_private_ip", action="store", type="string", \
                          dest="master_private_ip", help='master private ip', default="")

    opt_parser.add_option("-t", "--topslave_private_ip", action="store", type="string", \
                          dest="topslave_private_ip", help='topslave private ip', default="")

    (options, _) = opt_parser.parse_args(sys.argv)

    zone_id = options.zone_id
    access_key_id = options.access_key_id
    secret_access_key = options.secret_access_key
    host = options.host
    port = options.port
    protocol = options.protocol
    vxnet_id = options.vxnet_id
    master_private_ip = options.master_private_ip
    topslave_private_ip = options.topslave_private_ip
    print("zone_id:%s" % (zone_id))
    print("access_key_id:%s" % (access_key_id))
    print("secret_access_key:%s" % (secret_access_key))
    print("host:%s" % (host))
    print("port:%s" % (port))
    print("protocol:%s" % (protocol))
    print("vxnet_id:%s" % (vxnet_id))
    print("master_private_ip:%s" % (master_private_ip))
    print("topslave_private_ip:%s" % (topslave_private_ip))

    #连接iaas后台
    conn = Common.connect_iaas(zone_id, access_key_id, secret_access_key, host,port,protocol)
    print("connect_iaas conn == %s" % (conn))

    # 获取账号ID
    user_id = Common.get_user_id(conn,access_key_id)
    print("get_user_id user_id == %s" % (user_id))

    #创建子线程执行创建数据库的操作
    t = threading.Thread(target=create_rdb,args=(conn,user_id,vxnet_id,master_private_ip,topslave_private_ip,))
    t.start()
    t.join()

    print("主线程结束")

