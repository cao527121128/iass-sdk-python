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
import common.common as Common

def get_postgresql_cluster_topslave_rdb_instance_id(conn, cluster_id):
    print("get_postgresql_cluster_topslave_rdb_instance_id cluster_id == %s" %(cluster_id))

    topslave_rdb_instance_id = None
    # DescribeClusterDisplayTabs
    action = const.ACTION_DESCRIBE_CLUSTER_DISPLAY_TABS
    print("action == %s" % (action))
    ret = conn.describe_cluster_display_tabs(cluster=cluster_id,verbose=1,display_tabs="node_details")
    print("describe_cluster_display_tabs ret == %s" % (ret))
    Common.check_ret_code(ret, action)
    display_tabs = ret['display_tabs']
    if display_tabs is None or len(display_tabs) == 0:
        print("describe_cluster_display_tabs display_tabs is None")
        return None
    datas = display_tabs['data']
    print("datas == %s" % (datas))

    for data in datas:
        print("data == %s" % (data))
        if "Standby" in data or "standby" in data:
            topslave_rdb_instance_id = data[0]

    print("topslave_rdb_instance_id == %s" %(topslave_rdb_instance_id))
    return topslave_rdb_instance_id

def get_postgresql_cluster_master_rdb_instance_id(conn, cluster_id):
    print("get_postgresql_cluster_master_rdb_instance_id cluster_id == %s" %(cluster_id))

    master_rdb_instance_id = None
    # DescribeClusterDisplayTabs
    action = const.ACTION_DESCRIBE_CLUSTER_DISPLAY_TABS
    print("action == %s" % (action))
    ret = conn.describe_cluster_display_tabs(cluster=cluster_id,verbose=1,display_tabs="node_details")
    print("describe_cluster_display_tabs ret == %s" % (ret))
    Common.check_ret_code(ret, action)
    display_tabs = ret['display_tabs']
    if display_tabs is None or len(display_tabs) == 0:
        print("describe_cluster_display_tabs display_tabs is None")
        return None
    datas = display_tabs['data']
    print("datas == %s" % (datas))

    for data in datas:
        print("data == %s" % (data))
        if "Master" in data or "primary" in data:
            master_rdb_instance_id = data[0]

    print("master_rdb_instance_id == %s" %(master_rdb_instance_id))
    return master_rdb_instance_id

def get_postgresql_cluster_standby_ip(conn,cluster_id):
    print("get_postgresql_cluster_standby_ip cluster_id == %s" %(cluster_id))

    standby_ip = None
    # DescribeClusterDisplayTabs
    action = const.ACTION_DESCRIBE_CLUSTER_DISPLAY_TABS
    print("action == %s" % (action))
    ret = conn.describe_cluster_display_tabs(cluster=cluster_id,verbose=1,display_tabs="node_details")
    print("describe_cluster_display_tabs ret == %s" % (ret))
    Common.check_ret_code(ret, action)
    display_tabs = ret['display_tabs']
    if display_tabs is None or len(display_tabs) == 0:
        print("describe_cluster_display_tabs display_tabs is None")
        return None
    datas = display_tabs['data']
    print("datas == %s" % (datas))

    for data in datas:
        print("data == %s" % (data))
        if "Standby" in data or "standby" in data:
            standby_ip = data[1]

    print("standby_ip == %s" %(standby_ip))
    return standby_ip

def get_postgresql_cluster_primary_ip(conn,cluster_id):
    print("get_postgresql_cluster_primary_ip cluster_id == %s" %(cluster_id))

    primary_ip = None
    # DescribeClusterDisplayTabs
    action = const.ACTION_DESCRIBE_CLUSTER_DISPLAY_TABS
    print("action == %s" % (action))
    ret = conn.describe_cluster_display_tabs(cluster=cluster_id,verbose=1,display_tabs="node_details")
    print("describe_cluster_display_tabs ret == %s" % (ret))
    Common.check_ret_code(ret, action)
    display_tabs = ret['display_tabs']
    if display_tabs is None or len(display_tabs) == 0:
        print("describe_cluster_display_tabs display_tabs is None")
        return None
    datas = display_tabs['data']
    print("datas == %s" % (datas))

    for data in datas:
        print("data == %s" % (data))
        if "Master" in data or "primary" in data:
            primary_ip = data[1]

    print("primary_ip == %s" %(primary_ip))
    return primary_ip

def get_memcached_cluster_private_ip(conn,cluster_id):
    print("get_memcached_cluster_private_ip cluster_id == %s" %(cluster_id))
    private_ip = None

    # DescribeClusterNodes
    action = const.ACTION_DESCRIBE_CLUSTER_NODES
    print("action == %s" % (action))
    ret = conn.describe_cluster_nodes(cluster=cluster_id,verbose=1,limit=1)
    print("describe_cluster_nodes ret == %s" % (ret))
    Common.check_ret_code(ret, action)

    node_set = ret['node_set']
    if node_set is None or len(node_set) == 0:
        print("describe_cluster_nodes node_set is None")
        exit(-1)
    for node in node_set:
        private_ip = node.get("private_ip")

    print("private_ip == %s" %(private_ip))
    return private_ip

def get_memcached_cluster_cache_node_id(conn,cluster_id):
    print("get_memcached_cluster_cache_node_id cluster_id == %s" %(cluster_id))
    cache_node_id = None

    # DescribeClusterNodes
    action = const.ACTION_DESCRIBE_CLUSTER_NODES
    print("action == %s" % (action))
    ret = conn.describe_cluster_nodes(cluster=cluster_id,verbose=1,limit=1)
    print("describe_cluster_nodes ret == %s" % (ret))
    Common.check_ret_code(ret, action)

    node_set = ret['node_set']
    if node_set is None or len(node_set) == 0:
        print("describe_cluster_nodes node_set is None")
        exit(-1)
    for node in node_set:
        cache_node_id = node.get("node_id")

    print("cache_node_id == %s" %(cache_node_id))
    return cache_node_id

def deploy_app_version(conn,user_id,vxnet_id,zone_id,app_ids,primary_private_ip,standby_private_ip):
    print("子线程启动")
    print("deploy_app_version")

    if app_ids and not isinstance(app_ids, list):
        app_ids = [app_ids]
    app_type = ["cluster"]
    status = ["active"]
    print("app_ids == %s" % (app_ids))
    print("primary_private_ip == %s" % (primary_private_ip))
    print("standby_private_ip == %s" % (standby_private_ip))

    # # DescribeApps
    action = const.ACTION_DESCRIBE_APPS
    print("action == %s" % (action))
    ret = conn.describe_apps(app=app_ids[0],app_type=app_type)
    print("describe_apps ret == %s" % (ret))
    Common.check_ret_code(ret, action)

    # DescribeAppVersions
    action = const.ACTION_DESCRIBE_APP_VERSIONS
    print("action == %s" % (action))
    ret = conn.describe_app_versions(app_ids=app_ids,status=status,limit=1)
    print("describe_app_versions ret == %s" % (ret))
    Common.check_ret_code(ret, action)
    version_set = ret['version_set']
    if version_set is None or len(version_set) == 0:
        print("describe_app_versions version_set is None")
        exit(-1)
    for version in version_set:
        version_id = version.get("version_id")

    # GetGlobalUniqueId
    action = const.ACTION_GET_GLOBAL_UNIQUE_ID
    print("action == %s" % (action))
    ret = conn.get_global_unique_id(owner=user_id,zone=zone_id)
    print("get_global_unique_id ret == %s" % (ret))
    Common.check_ret_code(ret, action)
    global_uuid = ret['uuid']

    #DeployAppVersion
    action = const.ACTION_DEPLOY_APP_VERSION
    print("action == %s" % (action))
    print("app_ids == %s version_id == %s" % (app_ids,version_id))
    if app_ids == [const.POSTGRESQL_APP_IDS]:
        if primary_private_ip:
            print("primary_private_ip is not None.The cluster uses the specified private IP")
            # "private_ips":"192.168.15.100,192.168.15.101"
            private_ips_list = primary_private_ip + "," + standby_private_ip
            print("private_ips_list == %s" % (private_ips_list))
            conf = {
                "cluster": {
                    "name": "数据库服务",
                    "description": "postgresql",
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
                "private_ips":[{"role":"pg","private_ips":private_ips_list}],
                "env": {
                    "db_name": "test_vdi",
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
        else:
            print("primary_private_ip is None.The cluster uses automatically assigns private IP")
            conf = {
                "cluster": {
                    "name": "数据库服务",
                    "description": "postgresql",
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
                    "db_name": "test_vdi",
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

    elif app_ids == [const.MEMCACHED_APP_IDS]:
        if primary_private_ip:
            print("primary_private_ip is not None.The cluster uses the specified private IP")
            # "private_ips":"192.168.15.102"
            private_ips_list = primary_private_ip
            print("private_ips_list == %s" % (private_ips_list))
            conf = {
                "cluster":{
                    "name":"缓存服务",
                    "description":"memcached",
                    "memcached_node":{
                        "cpu":1,
                        "memory":1024,
                        "instance_class":0,
                        "count":1
                    },
                    "vxnet":vxnet_id,
                    "global_uuid":global_uuid
                },
                "version":version_id,
                "zone":zone_id,
                "private_ips":[{"role":"memcached_node","private_ips":private_ips_list}],
                "env":{
                    "-p":11211,
                    "-U":11211,
                    "-c":65000,
                    "-m":716,
                    "-n":48,
                    "-f":1.25,
                    "-t":1,
                    "-M":0
                }
            }
        else:
            print("primary_private_ip is None.The cluster uses automatically assigns private IP")
            conf = {
                "cluster": {
                    "name": "缓存服务",
                    "description": "memcached",
                    "memcached_node": {
                        "cpu": 1,
                        "memory": 1024,
                        "instance_class": 0,
                        "count": 1
                    },
                    "vxnet": vxnet_id,
                    "global_uuid": global_uuid
                },
                "version": version_id,
                "zone": zone_id,
                "env": {
                    "-p": 11211,
                    "-U": 11211,
                    "-c": 65000,
                    "-m": 716,
                    "-n": 48,
                    "-f": 1.25,
                    "-t": 1,
                    "-M": 0
                }
            }
    else:
        print("app_ids %s is invalid" %(app_ids))

    #conf python dictionary conversion JSON format
    jconf = json.dumps(conf)
    print("jconf == %s" % (jconf))
    ret = conn.deploy_app_version(app_type=app_type,app_id=app_ids,version_id=version_id,conf=jconf,charge_mode="elastic",debug=0,owner=user_id)
    print("deploy_app_version ret == %s" % (ret))
    Common.check_ret_code(ret, action)
    cluster_id = ret['cluster_id']
    job_id = ret['job_id']
    print("cluster_id == %s" % (cluster_id))
    print("job_id == %s" % (job_id))

    # check job status
    num = 0
    while num < 300:
        num = num + 1
        print("num == %d" % (num))
        time.sleep(1)
        status = Common.get_job_status(conn,job_id)
        if status == "successful":
            print("deploy_app_version successful")
            break
    print("status == %s" % (status))

    # Record node IP through file
    if app_ids == [const.POSTGRESQL_APP_IDS]:
        if status == "successful":
            print("deploy_app_version postresql successful")
            # create_rdb ok
            create_rdb_status = "True"
            # create_rdb_status 写入文件
            create_rdb_status_conf = "/opt/create_rdb_status_conf"
            with open(create_rdb_status_conf, "w+") as f:
                f.write("CREATE_RDB_STATUS %s" % (create_rdb_status))

            # cluster_id 写入文件
            rdb_cluster_id_conf = "/opt/rdb_cluster_id_conf"
            with open(rdb_cluster_id_conf, "w+") as f:
                f.write("RDB_CLUSTER_ID %s" % (cluster_id))

            # cluster_id 写入文件
            rdb_id_conf = "/opt/rdb_id_conf"
            with open(rdb_id_conf, "w+") as f:
                f.write("RDB_ID %s" % (cluster_id))

            # rdb_master_ip 写入文件
            rdb_master_ip_conf = "/opt/rdb_master_ip_conf"
            rdb_master_ip = get_postgresql_cluster_primary_ip(conn,cluster_id)
            print("get_postgresql_cluster_primary_ip == %s" % (rdb_master_ip))
            if rdb_master_ip:
                with open(rdb_master_ip_conf, "w+") as f:
                    f.write("POSTGRESQL_ADDRESS %s" % (rdb_master_ip))

            # rdb_topslave_ip 写入文件
            rdb_topslave_ip_conf = "/opt/rdb_topslave_ip_conf"
            rdb_topslave_ip = get_postgresql_cluster_standby_ip(conn,cluster_id)
            print("get_postgresql_cluster_standby_ip rdb_topslave_ip == %s" % (rdb_topslave_ip))
            if rdb_topslave_ip:
                with open(rdb_topslave_ip_conf, "w+") as f:
                    f.write("RDB_TOPSLAVE_IP %s" % (rdb_topslave_ip))

            # master_rdb_instance_id 写入文件
            master_rdb_instance_id_conf = "/opt/master_rdb_instance_id_conf"
            master_rdb_instance_id = get_postgresql_cluster_master_rdb_instance_id(conn, cluster_id)
            print("get_postgresql_cluster_master_rdb_instance_id master_rdb_instance_id == %s" % (master_rdb_instance_id))
            if master_rdb_instance_id:
                with open(master_rdb_instance_id_conf, "w+") as f:
                    f.write("MASTER_RDB_INSTANCE_ID %s" % (master_rdb_instance_id))

            # topslave_rdb_instance_id 写入文件
            topslave_rdb_instance_id_conf = "/opt/topslave_rdb_instance_id_conf"
            topslave_rdb_instance_id = get_postgresql_cluster_topslave_rdb_instance_id(conn, cluster_id)
            print("get_postgresql_cluster_topslave_rdb_instance_id topslave_rdb_instance_id == %s" % (topslave_rdb_instance_id))
            if topslave_rdb_instance_id:
                with open(topslave_rdb_instance_id_conf, "w+") as f:
                    f.write("TOPSLAVE_RDB_INSTANCE_ID %s" % (topslave_rdb_instance_id))

            # attach tags
            current_time = time.strftime("%Y-%m-%d", time.localtime())
            tag_name = '桌面云数据库 %s' % (current_time)
            Common.attach_tags_to_resource(conn, user_id=user_id,tag_name=tag_name, resource_type='cluster', resource_id=cluster_id)

        else:
            print("deploy_app_version postresql timeout")
            create_rdb_status =  "False"
            # create_rdb_status 写入文件
            create_rdb_status_conf = "/opt/create_rdb_status_conf"
            with open(create_rdb_status_conf, "w+") as f1:
                f1.write("CREATE_RDB_STATUS %s" % (create_rdb_status))

    elif app_ids == [const.MEMCACHED_APP_IDS]:
        if status == "successful":
            print("deploy_app_version memcached successful")
            # create_memcached ok
            create_memcached_status = "True"
            create_memcached_status_conf = "/opt/create_memcached_status_conf"
            with open(create_memcached_status_conf, "w+") as f:
                f.write("CREATE_MEMCACHED_STATUS %s" % (create_memcached_status))

            # cluster_id 写入文件
            cache_cluster_id_conf = "/opt/cache_cluster_id_conf"
            with open(cache_cluster_id_conf, "w+") as f:
                f.write("CACHE_CLUSTER_ID %s" % (cluster_id))

            # cache_id 写入文件
            cache_id_conf = "/opt/cache_id_conf"
            with open(cache_id_conf, "w+") as f:
                f.write("CACHE_ID %s" % (cluster_id))

            # cache_master_ip 写入文件
            cache_master_ip_conf = "/opt/cache_master_ip_conf"
            cache_master_ip = get_memcached_cluster_private_ip(conn, cluster_id)
            print("get_memcached_cluster_private_ip cache_master_ip == %s" % (cache_master_ip))
            if cache_master_ip:
                with open(cache_master_ip_conf, "w+") as f:
                    f.write("MEMCACHED_ADDRESS %s" % (cache_master_ip))

            # cache_node_id 写入文件
            cache_node_id_conf = "/opt/cache_node_id_conf"
            cache_node_id = get_memcached_cluster_cache_node_id(conn, cluster_id)
            print("get_memcached_cluster_cache_node_id cache_node_id == %s" % (cache_node_id))
            if cache_node_id:
                with open(cache_node_id_conf, "w+") as f:
                    f.write("CACHE_NODE_ID %s" % (cache_node_id))

            # attach tags
            current_time = time.strftime("%Y-%m-%d", time.localtime())
            tag_name = '桌面云缓存 %s' % (current_time)
            Common.attach_tags_to_resource(conn,user_id=user_id, tag_name=tag_name, resource_type='cluster', resource_id=cluster_id)
        else:
            print("deploy_app_version memcached timeout")
            create_memcached_status = "False"
            # create_memcached_status 写入文件
            create_memcached_status_conf = "/opt/create_memcached_status_conf"
            with open(create_memcached_status_conf, "w+") as f1:
                f1.write("CREATE_MEMCACHED_STATUS %s" % (create_memcached_status))
    else:
        print("app_ids %s doesn't support" % (app_ids))
        exit(-1)

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

    opt_parser.add_option("-m", "--primary_private_ip", action="store", type="string", \
                          dest="primary_private_ip", help='primary private ip', default="")

    opt_parser.add_option("-t", "--standby_private_ip", action="store", type="string", \
                          dest="standby_private_ip", help='standby private ip', default="")

    (options, _) = opt_parser.parse_args(sys.argv)

    zone_id = options.zone_id
    access_key_id = options.access_key_id
    secret_access_key = options.secret_access_key
    host = options.host
    port = options.port
    protocol = options.protocol
    vxnet_id = options.vxnet_id
    app_ids = options.app_ids
    primary_private_ip = options.primary_private_ip or ""
    standby_private_ip = options.standby_private_ip or ""

    print("zone_id:%s" % (zone_id))
    print("access_key_id:%s" % (access_key_id))
    print("secret_access_key:%s" % (secret_access_key))
    print("host:%s" % (host))
    print("port:%s" % (port))
    print("protocol:%s" % (protocol))
    print("vxnet_id:%s" % (vxnet_id))
    print("app_ids:%s" % (app_ids))
    print("primary_private_ip:%s" % (primary_private_ip))
    print("standby_private_ip:%s" % (standby_private_ip))

    #连接iaas后台
    conn = Common.connect_iaas(zone_id, access_key_id, secret_access_key, host,port,protocol)
    print("connect_iaas conn == %s" % (conn))

    # 获取账号ID
    user_id = Common.get_user_id(conn,access_key_id)
    print("get_user_id user_id == %s" % (user_id))

    #创建子线程通过appcenter创建postgresql集群 部署指定数据库应用版本的集群
    t = threading.Thread(target=deploy_app_version,args=(conn,user_id,vxnet_id,zone_id,app_ids,primary_private_ip,standby_private_ip,))
    t.start()
    t.join()

    print("主线程结束")

