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

# global
zone_id = None
conn=None
access_key_id = None
secret_access_key = None
host = None
port = None
protocol = None
vxnet_id = None
g_rdb_id = None






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

def create_rdb(vxnet_id,master_private_ip,topslave_private_ip):
    print("子线程启动")
    print("create_rdb")
    global conn
    global g_rdb_id
    print("master_private_ip == %s" %(master_private_ip))
    print("topslave_private_ip == %s" % (topslave_private_ip))
    if not master_private_ip:
        print("private_ips is null")
        ret = conn.create_rdb(
            # vxnet='vxnet-glp08w9',
            vxnet=vxnet_id,
            rdb_engine='psql',
            engine_version='9.4',
            rdb_username='yunify',
            rdb_password='Zhu88jie',
            rdb_type=2,
            storage_size=10,
            rdb_name='vdi-portal-postgresql'
        )
    else:
        print("private_ips is not null")
        #private_ips = [{“master”:”192.168.100.14”,”topslave”:”192.168.100.17”}]
        private_ips_list = {"master":master_private_ip,"topslave":topslave_private_ip}
        print("private_ips_list == %s" %(private_ips_list))
        ret = conn.create_rdb(
            vxnet=vxnet_id,
            rdb_engine='psql',
            engine_version='9.4',
            rdb_username='yunify',
            rdb_password='Zhu88jie',
            rdb_type=2,
            storage_size=10,
            rdb_name='vdi-portal-postgresql',
            private_ips=[private_ips_list]
        )
    print("ret==%s" % (ret))
    #check ret_code
    ret_code = ret.get("ret_code")
    print("ret_code==%s" % (ret_code))
    if ret_code!=0:
        print("create_rdb failed")
        exit(-1)

    g_rdb_id = ret.get("rdb")
    print("g_rdb_id=%s" %(g_rdb_id))

    if not g_rdb_id:
        print("create rdb fail")
        exit(-1)
    status = "pending"
    num = 0
    while status != "active" and num <=120:
        time.sleep(1)
        status = get_rdb_status()
        num = num + 1
        print("num=%d" %(num))
    if status!="active":
        print("create_rdb timeout")
        create_rdb_status =  "False"
        # create_rdb_status 写入文件
        create_rdb_status_conf = "/opt/create_rdb_status_conf"
        with open(create_rdb_status_conf, "w+") as f1:
            f1.write("CREATE_RDB_STATUS %s" % (create_rdb_status))
        exit(-1)

    #create_rdb ok
    create_rdb_status = "True"
    # create_rdb_status 写入文件
    create_rdb_status_conf = "/opt/create_rdb_status_conf"
    with open(create_rdb_status_conf, "w+") as f1:
        f1.write("CREATE_RDB_STATUS %s" % (create_rdb_status))

    #master_ip 写入文件
    master_ip_conf = "/opt/master_ip_conf"
    ret = get_rdb_master_ip()
    with open(master_ip_conf, "w+") as f1:
        f1.write("POSTGRESQL_ADDRESS %s" %(ret))

    #user_id 写入文件
    user_id_conf = "/opt/user_id_conf"
    ret = get_user_id()
    with open(user_id_conf, "w+") as f1:
        f1.write("USER_ID %s" %(ret))
    print("子线程结束")




def get_rdb_status():
    print("get_rdb_status")
    global conn
    global g_rdb_id
    ret = conn.describe_rdbs(rdbs=[g_rdb_id])
    print("ret==%s" % (ret))
    # check ret_code
    ret_code = ret.get("ret_code")
    print("ret_code==%s" % (ret_code))
    if ret_code != 0:
        print("describe_rdbs failed")
        exit(-1)

    matched_rdb = ret['rdb_set']
    print("matched_rdb==%s"%(matched_rdb))

    print("************************************")

    wanted_rdb = matched_rdb[0]
    print("wanted_rdb==%s" % (wanted_rdb))

    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    status = wanted_rdb.get('status')
    master_ip = wanted_rdb.get('master_ip')
    print("status=%s master_ip=%s" % (status, master_ip))
    return status



def get_rdb_master_ip():
    print("get_rdb_master_ip")
    global conn
    global g_rdb_id
    ret = conn.describe_rdbs(rdbs=[g_rdb_id])
    print("ret==%s" % (ret))
    # check ret_code
    ret_code = ret.get("ret_code")
    print("ret_code==%s" % (ret_code))
    if ret_code != 0:
        print("describe_rdbs failed")
        exit(-1)

    matched_rdb = ret['rdb_set']
    print("matched_rdb==%s"%(matched_rdb))
    if not matched_rdb:
        print("describe_rdbs is NULL")
        exit(-1)

    print("************************************")
    wanted_rdb = matched_rdb[0]
    print("wanted_rdb==%s" % (wanted_rdb))

    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    master_ip = wanted_rdb.get('master_ip',0)
    print("master_ip=%s" % (master_ip))
    return master_ip


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
    connect_iaas(zone_id, access_key_id, secret_access_key, host,port,protocol)


    #创建子线程执行创建数据库的操作
    t = threading.Thread(target=create_rdb,args=(vxnet_id,master_private_ip,topslave_private_ip,))
    t.start()
    t.join()


    print("主线程结束")

