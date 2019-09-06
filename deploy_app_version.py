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
import json

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


def deploy_app_version(app_ids,vxnet_id,zone_id):
    print("子线程启动")
    print("deploy_app_version")
    global conn
    user_id = get_user_id()

    if app_ids and not isinstance(app_ids, list):
        app_ids = [app_ids]
    app_type = ["cluster"]
    cluster_id = ["cl-73h9g7zc"]
    status = ["active"]
    global_uuid = "32082219583369087"
    print("app_ids == %s" % (app_ids))
    print("app_type == %s" % (app_type))
    print("cluster_id == %s" % (cluster_id))
    print("status == %s" % (status))
    print("vxnet_id == %s" % (vxnet_id))
    print("global_uuid == %s" % (global_uuid))
    print("zone_id == %s" % (zone_id))


    # DescribeApps
    action = const.ACTION_DESCRIBE_APPS
    print("action == %s" % (action))
    ret = conn.describe_apps(app=app_ids[0],app_type=app_type)
    # print("describe_apps ret == %s" % (ret))
    check_ret_code(ret, action)

    # DescribeClusters
    action = const.ACTION_DESCRIBE_CLUSTERS
    print("action == %s" % (action))
    ret = conn.describe_clusters(apps=app_ids,clusters=cluster_id)
    # print("describe_clusters ret == %s" % (ret))
    check_ret_code(ret, action)

    # DescribeAppVersions
    action = const.ACTION_DESCRIBE_APP_VERSIONS
    print("action == %s" % (action))
    ret = conn.describe_app_versions(app_ids=app_ids,status=status,limit=1)
    # print("describe_app_versions ret == %s" % (ret))
    check_ret_code(ret, action)
    version_set = ret['version_set']
    # print("version_set==%s" % (version_set))
    if version_set is None or len(version_set) == 0:
        print("describe_app_versions version_set is None")
        exit(-1)
    for version in version_set:
        version_id = version.get("version_id")
        resource_kit = version.get("resource_kit")
    print("version_id == %s" %(version_id))
    print("resource_kit == %s" % (resource_kit))

    #DeployAppVersion
    action = const.ACTION_DEPLOY_APP_VERSION
    print("action == %s" % (action))
    # conf = {"cluster": {"name":"PostgreSQL11 Cluster","description":"test-001","auto_backup_time":"-1","pg":{"cpu":2,"memory":4096,"instance_class":0,"volume_size":50},
    #                   "ri":{"cpu":2,"memory":4096,"instance_class":1,"count":0,"volume_size":20},
    #                   "pgpool":{"cpu":2,"memory":4096,"instance_class":1,"count":0,"volume_size":20},"vxnet":"vxnet-za3ludg","global_uuid":"32082219583369087"},
    #         "version":"appv-7f3zbdc5","resource_group":"Standard","zone":"gd2a",
    #         "env":{"db_name":"vdi","user_name":"yunify","password":"Zhu88jie",
    #         "pg_version":"11","serialize_accept":"off","pgpool_port":9999,"child_life_time":300,"connection_life_time":600,"client_idle_limit":0,
    #         "max_pool":2,"num_init_children":100,"sync_stream_repl":"Yes","load_read_request_to_primary":"Yes","auto_failover":"Yes","max_connections":"auto-optimized-conns",
    #         "wal_buffers":"8MB","work_mem":"4MB","maintenance_work_mem":"64MB","effective_cache_size":"4GB","wal_keep_segments":256,"checkpoint_timeout":"5min","autovacuum":"on",
    #         "vacuum_cost_delay":0,"autovacuum_naptime":"1min","vacuum_cost_limit":200,"bgwriter_delay":200,"bgwriter_lru_multiplier":2,"wal_writer_delay":200,"fsync":"on",
    #         "commit_delay":0,"commit_siblings":5,"enable_bitmapscan":"on","enable_seqscan":"on","full_page_writes":"on","log_min_messages":"warning","deadlock_timeout":1,
    #         "log_lock_waits":"off","log_min_duration_statement":-1,"temp_buffers":"8MB","max_prepared_transactions":0,"max_wal_senders":10,"bgwriter_lru_maxpages":100,
    #         "log_statement":"none","shared_preload_libraries":"passwordcheck","wal_level":"replica","shared_buffers":"auto-optimized-sharedbuffers","jit":"off"},
    #         "toggle_passwd":"on"}

    conf = {
        "cluster": {
            "name": "PostgreSQL11 Cluster",
            "description": "vdi-portal-postgresql",
            "auto_backup_time": "-1",
            "pg": {
                "cpu": 2,
                "memory": 4096,
                "instance_class": 0,
                "volume_size": 50
            },
            "ri": {
                "cpu": 2,
                "memory": 4096,
                "instance_class": 1,
                "count": 0,
                "volume_size": 20
            },
            "pgpool": {
                "cpu": 2,
                "memory": 4096,
                "instance_class": 1,
                "count": 0,
                "volume_size": 20
            },
            "vxnet": vxnet_id,
            "global_uuid": global_uuid
        },
        "version": version_id,
        "resource_group": "Standard",
        "zone": zone_id,
        "env": {
            "db_name": "vdi",
            "user_name": "yunify",
            "password": "Zhu88jie",
            "pg_version": "11",
            "serialize_accept": "off",
            "pgpool_port": 9999,
            "child_life_time": 300,
            "connection_life_time": 600,
            "client_idle_limit": 0,
            "max_pool": 2,
            "num_init_children": 100,
            "sync_stream_repl": "Yes",
            "load_read_request_to_primary": "Yes",
            "auto_failover": "Yes",
            "max_connections": "auto-optimized-conns",
            "wal_buffers": "8MB",
            "work_mem": "4MB",
            "maintenance_work_mem": "64MB",
            "effective_cache_size": "4GB",
            "wal_keep_segments": 256,
            "checkpoint_timeout": "5min",
            "autovacuum": "on",
            "vacuum_cost_delay": 0,
            "autovacuum_naptime": "1min",
            "vacuum_cost_limit": 200,
            "bgwriter_delay": 200,
            "bgwriter_lru_multiplier": 2,
            "wal_writer_delay": 200,
            "fsync": "on",
            "commit_delay": 0,
            "commit_siblings": 5,
            "enable_bitmapscan": "on",
            "enable_seqscan": "on",
            "full_page_writes": "on",
            "log_min_messages": "warning",
            "deadlock_timeout": 1,
            "log_lock_waits": "off",
            "log_min_duration_statement": -1,
            "temp_buffers": "8MB",
            "max_prepared_transactions": 0,
            "max_wal_senders": 10,
            "bgwriter_lru_maxpages": 100,
            "log_statement": "none",
            "shared_preload_libraries": "passwordcheck",
            "wal_level": "replica",
            "shared_buffers": "auto-optimized-sharedbuffers",
            "jit": "off"
        },
        "toggle_passwd": "on"
    }

    # conf python dictionary conversion JSON format
    jconf = json.dumps(conf)
    print("jconf == %s" % (jconf))
    ret = conn.deploy_app_version(app_type=app_type,app_id=app_ids,version_id=version_id,conf=jconf,charge_mode="elastic",debug=0,owner=user_id)
    print("deploy_app_version ret == %s" % (ret))
    check_ret_code(ret, action)

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
    t = threading.Thread(target=deploy_app_version,args=(app_ids,vxnet_id,zone_id,))
    t.start()
    t.join()

    print("主线程结束")

