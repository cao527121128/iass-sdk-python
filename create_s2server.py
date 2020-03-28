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

g_s2_server_id = None

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

def get_instance_class(conn,user_id,vdi_resource_id):
    print("get_instance_class user_id == %s vdi_resource_id == %s" %(user_id,vdi_resource_id))
    instance_class = 0

    if vdi_resource_id and not isinstance(vdi_resource_id, list):
        vdi_resource_id = [vdi_resource_id]
    print("vdi_resource_id == %s" %(vdi_resource_id))

    # DescribeInstances
    action = const.ACTION_DESCRIBE_INSTANCES
    print("action == %s" % (action))
    ret = conn.describe_instances(owner=user_id,instances=vdi_resource_id,verbose=1)
    print("describe_instances ret == %s" % (ret))
    Common.check_ret_code(ret, action)

    # get instance_class
    instance_set = ret['instance_set']
    if instance_set is None or len(instance_set) == 0:
        print("describe_instances instance_set is None")
        exit(-1)
    for instance in instance_set:
        instance_class = instance.get("instance_class")

    return instance_class

def create_new_volume(conn,user_id,volume_type):
    print("create_new_volume user_id == %s volume_type == %s" %(user_id,volume_type))
    volume_id = ""

    # CreateVolumes
    action = const.ACTION_CREATE_VOLUMES
    print("action == %s" % (action))
    ret = conn.create_volumes(owner=user_id,volume_name="vdi-portal-nas",volume_type=volume_type,count=1,size=100,target_user=user_id)
    print("create_volumes ret == %s" % (ret))
    Common.check_ret_code(ret, action)

    job_id = ret['job_id']
    volume_id = ret['volumes']
    print("job_id == %s" % (job_id))
    print("volume_id == %s" % (volume_id))
    # check job status
    num = 0
    while num < 300:
        num = num + 1
        print("num == %d" % (num))
        time.sleep(1)
        status = Common.get_job_status(conn, job_id)
        if status == "successful":
            print("create_volumes successful")
            break
    print("status == %s" % (status))

    return volume_id

def create_s2_shared_target(conn,user_id,vxnet_id,s2_server_id,instance_class):
    print("子线程启动")
    print("create_s2_shared_target user_id == %s vxnet_id == %s s2_server_id == %s instance_class == %s" % (user_id,vxnet_id,s2_server_id,instance_class))

    # get the volume_type corresponding to the instance class
    volume_type = const.INSTANCE_CLASS_VOLUME_TYPE_MAP[instance_class]
    print("instance_class == %s" % (instance_class))
    print("volume_type == %s" % (volume_type))

    # get available volume_id
    volume_id = create_new_volume(conn,user_id,volume_type)
    print("create_new_volume volume_id == %s" % (volume_id))
    if not volume_id:
        print("volume_id is not available. and create volume failed")
        exit(-1)
    if volume_id and not isinstance(volume_id, list):
        volume_id = [volume_id]
    print("volume_id == %s" %(volume_id))

    # CreateS2SharedTarget
    action = const.ACTION_CREATE_S2_SHARED_TARGET
    print("action == %s" % (action))
    ret = conn.create_s2_shared_target(owner=user_id,vxnet=vxnet_id,s2_server_id=s2_server_id,target_type='NFS',export_name_nfs='nas',export_name='/mnt/nas',volumes=volume_id)
    print("create_s2_shared_target ret == %s" % (ret))
    Common.check_ret_code(ret, action)

    s2_shared_target_id = ret['s2_shared_target']
    print("s2_shared_target_id == %s" % (s2_shared_target_id))

    # s2_shared_target_id 写入文件
    shared_target_id_conf = "/opt/shared_target_id_conf"
    with open(shared_target_id_conf, "w+") as f:
        f.write("SHARED_TARGET_ID %s" % (s2_shared_target_id))

    print("子线程结束")

def create_s2server(conn,user_id,vxnet_id,private_ips,instance_class):
    print("子线程启动")
    print("create_s2server user_id == %s vxnet_id == %s private_ips == %s instance_class == %s" % (user_id,vxnet_id,private_ips,instance_class))
    global g_s2_server_id

    # get the s2_class corresponding to the instance class
    s2_class = const.INSTANCE_CLASS_S2_CLASS_MAP[instance_class]
    print("instance_class == %s" % (instance_class))
    print("s2_class == %s" % (s2_class))

    if not private_ips:
        print("private_ips is None")
        # CreateS2Server
        action = const.ACTION_CREATE_S2_SERVER
        print("action == %s" % (action))
        ret = conn.create_s2_server(owner=user_id,vxnet=vxnet_id,service_type='vnas',s2_server_name='文件服务器',s2_server_type=0,description='文件存储vNAS',s2_class=s2_class)
        print("create_s2_server ret == %s" % (ret))
        Common.check_ret_code(ret, action)
    else:
        print("private_ips is %s" %(private_ips))
        # CreateS2Server
        action = const.ACTION_CREATE_S2_SERVER
        print("action == %s" % (action))
        ret = conn.create_s2_server(owner=user_id,vxnet=vxnet_id,service_type='vnas',s2_server_name='文件服务器',s2_server_type=0,description='文件存储vNAS',s2_class=s2_class,private_ip=private_ips)
        print("create_s2_server ret == %s" % (ret))
        Common.check_ret_code(ret, action)

    job_id = ret['job_id']
    s2_server_id = ret['s2_server']
    print("job_id == %s" % (job_id))
    print("s2_server_id == %s" % (s2_server_id))
    # check job status
    num = 0
    while num < 300:
        num = num + 1
        print("num == %d" % (num))
        time.sleep(1)
        status = Common.get_job_status(conn,job_id)
        if status == "successful":
            print("create_s2_server successful")
            break
    print("status == %s" % (status))

    if status == "successful":
        print("create_s2_server s2_server successful")
        g_s2_server_id = s2_server_id
        print("g_s2_server_id == %s" % (g_s2_server_id))

        # s2_server_id 写入文件
        s2server_id_conf = "/opt/s2server_id_conf"
        with open(s2server_id_conf, "w+") as f1:
            f1.write("S2SERVER_ID %s" % (s2_server_id))

        # attach tags
        current_time = time.strftime("%Y-%m-%d", time.localtime())
        tag_name = '桌面云文件服务器 %s' %(current_time)
        Common.attach_tags_to_resource(conn,user_id=user_id,tag_name=tag_name,resource_type='s2_server',resource_id=s2_server_id)

    else:
        print("create_s2_server s2_server failed")
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

    opt_parser.add_option("-i", "--vdi0_ip", action="store", type="string", \
                          dest="vdi0_ip", help='vdi0 ip', default="")

    opt_parser.add_option("-d", "--vdi1_ip", action="store", type="string", \
                          dest="vdi1_ip", help='vdi1 ip', default="")

    opt_parser.add_option("-m", "--private_ips", action="store", type="string", \
                          dest="private_ips", help='private ips', default="")

    opt_parser.add_option("-r", "--vdi_resource_id", action="store", type="string", \
                          dest="vdi_resource_id", help='vdi resource id', default="")

    (options, _) = opt_parser.parse_args(sys.argv)

    zone_id = options.zone_id
    access_key_id = options.access_key_id
    secret_access_key = options.secret_access_key
    host = options.host
    port = options.port
    protocol = options.protocol
    vxnet_id = options.vxnet_id
    g_vdi0_ip = options.vdi0_ip
    g_vdi1_ip = options.vdi1_ip
    private_ips = options.private_ips
    vdi_resource_id = options.vdi_resource_id

    print("zone_id:%s" % (zone_id))
    print("access_key_id:%s" % (access_key_id))
    print("secret_access_key:%s" % (secret_access_key))
    print("host:%s" % (host))
    print("port:%s" % (port))
    print("protocol:%s" % (protocol))
    print("vxnet_id:%s" % (vxnet_id))
    print("g_vdi0_ip:%s" % (g_vdi0_ip))
    print("g_vdi1_ip:%s" % (g_vdi1_ip))
    print("private_ips:%s" % (private_ips))
    print("vdi_resource_id:%s" % (vdi_resource_id))

    #连接iaas后台
    conn = Common.connect_iaas(zone_id, access_key_id, secret_access_key, host,port,protocol)
    print("connect_iaas conn == %s" % (conn))

    # 获取账号ID
    user_id = Common.get_user_id(conn,access_key_id)
    print("get_user_id user_id == %s" % (user_id))

    # 获取VDI主机类型 get_instance_class
    instance_class = get_instance_class(conn,user_id,vdi_resource_id)
    print("get_instance_class instance_class == %s" % (instance_class))

    #创建子线程--创建共享存储服务器
    t = threading.Thread(target=create_s2server,args=(conn,user_id,vxnet_id,private_ips,instance_class,))
    t.start()
    t.join()

    if g_s2_server_id:

        #创建子线程--新建共享存储目标
        t2 = threading.Thread(target=create_s2_shared_target,args=(conn,user_id,vxnet_id,g_s2_server_id,instance_class,))
        t2.start()
        t2.join()

        #创建子线程--创建vnas服务访问资源账号 vdi0 vdi1客户端
        t3 = threading.Thread(target=create_s2_account_vdi_host,args=(conn,user_id,[g_vdi0_ip,g_vdi1_ip],))
        t3.start()
        t3.join()

        #创建子线程--更新共享存储服务器的配置信息
        t4 = threading.Thread(target=update_s2_servers,args=(conn,user_id,g_s2_server_id,))
        t4.start()
        t4.join()

    print("主线程结束")

