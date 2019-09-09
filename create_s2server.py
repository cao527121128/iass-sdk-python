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
g_s2_shared_target_id = None

# # global
# zone_id = None
# conn=None
# access_key_id = None
# secret_access_key = None
# host = None
# port = None
# protocol = None
# vxnet_id = None
# g_s2_server_id = None
# g_s2_shared_target_id = None
# g_vdi0_ip = None
# g_vdi1_ip = None
# g_s2_account_id_vdi0_host = None
# g_s2_account_id_vdi1_host = None
# g_create_s2_server_flag = True

#
# def connect_iaas(zone_id, access_key_id, secret_access_key, host,port,protocol):
#     print("connect_iaas")
#     print("starting connect_to_zone ...")
#     global conn
#     conn = qingcloud.iaas.connect_to_zone(
#         zone_id,
#         access_key_id,
#         secret_access_key,
#         host,
#         port,
#         protocol
#     )
#     if conn < 0:
#         print("connect_to_zone fail")
#         exit(-1)
#     print("conn==%s" %(conn))
#
#     user_id=get_user_id()
#     if not user_id:
#         print("user_id is null")
#         exit(-1)
#
# def create_s2server(vxnet_id,private_ips):
#     print("子线程启动")
#     print("create_s2server")
#     global conn
#     global g_s2_server_id
#     global g_create_s2_server_flag
#
#     print("vxnet_id == %s" % (vxnet_id))
#     print("private_ips == %s" % (private_ips))
#
#     if not private_ips:
#         print("private_ips is null")
#         ret = conn.create_s2_server(
#             vxnet=vxnet_id,
#             service_type='vnas',
#             s2_server_name='vdi-portal-nas',
#             s2_server_type=1,
#             description='vdi portal nas',
#             s2_class=0
#         )
#
#     else:
#         print("private_ips is not null")
#         ret = conn.create_s2_server(
#             vxnet=vxnet_id,
#             service_type='vnas',
#             s2_server_name='vdi-portal-nas',
#             s2_server_type=1,
#             description='vdi portal nas',
#             s2_class=0,
#             private_ip=private_ips
#         )
#
#
#     # check ret_code
#     print("ret==%s" % (ret))
#     ret_code = ret.get("ret_code")
#     print("ret_code==%s" % (ret_code))
#     if ret_code != 0:
#         print("create_s2_server failed")
#         g_create_s2_server_flag = False
#         exit(-1)
#
#     #get s2_server_id
#     g_s2_server_id = ret.get("s2_server")
#     print("g_s2_server_id=%s" % (g_s2_server_id))
#     if not g_s2_server_id:
#         print("create_s2server fail")
#         exit(-1)
#
#     #check create_s2_server status
#     status = "pending"
#     num = 0
#     while status != "active" and num <= 300:
#         time.sleep(1)
#         status = get_s2_server_status()
#         num = num + 1
#         print("num=%d" %(num))
#
#     if status!="active":
#         print("create_s2server timeout")
#         exit(-1)
#     print("子线程结束")


#
#
# def get_s2_server_status():
#     print("get_s2_server_status")
#     global conn
#     global g_s2_server_id
#     ret = conn.describe_s2_servers(s2_servers=[g_s2_server_id],verbose=1)
#
#     # check ret_code
#     print("ret==%s" % (ret))
#     ret_code = ret.get("ret_code")
#     print("ret_code==%s" % (ret_code))
#     if ret_code != 0:
#         print("describe_s2_servers failed")
#         exit(-1)
#
#     matched_s2_server = ret['s2_server_set']
#     print("matched_s2_server==%s"%(matched_s2_server))
#
#     print("************************************")
#
#     wanted_s2_server = matched_s2_server[0]
#     print("wanted_s2_server==%s" % (wanted_s2_server))
#
#     print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
#     status = wanted_s2_server.get('status')
#     print("status=%s" % (status))
#     return status
#
# def get_job_status(job_id):
#     print("get_job_status")
#     global conn
#     ret = conn.describe_jobs(jobs=[job_id],verbose=1)
#
#     # check ret_code
#     print("ret==%s" % (ret))
#     ret_code = ret.get("ret_code")
#     print("ret_code==%s" % (ret_code))
#     if ret_code != 0:
#         print("describe_jobs failed")
#         exit(-1)
#
#     matched_job_set = ret['job_set']
#     print("matched_job_set == %s"%(matched_job_set))
#
#     print("************************************")
#
#     wanted_job_set = matched_job_set[0]
#     print("wanted_job_set == %s" % (wanted_job_set))
#
#     print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
#     status = wanted_job_set.get('status')
#     print("status=%s" % (status))
#     return status
#
#
# def get_s2_servers_transition_status():
#     print("get_s2_servers_transition_status")
#     global conn
#     global g_s2_server_id
#     global g_s2_shared_target_id
#
#     ret = conn.describe_s2_servers(s2_servers=[g_s2_server_id])
#
#     # check ret_code
#     print("ret==%s" % (ret))
#     ret_code = ret.get("ret_code")
#     print("ret_code==%s" % (ret_code))
#     if ret_code != 0:
#         print("describe_s2_servers failed")
#         exit(-1)
#
#     matched_s2_server = ret['s2_server_set']
#     print("matched_s2_server==%s"%(matched_s2_server))
#
#     print("************************************")
#
#     wanted_s2_server = matched_s2_server[0]
#     print("wanted_s2_server==%s" % (wanted_s2_server))
#
#     print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
#     transition_status = wanted_s2_server.get('transition_status')
#     print("transition_status==%s" % (transition_status))
#     return transition_status
#
#
# def get_s2_server_ip():
#     print("get_s2_server_ip")
#     global conn
#     global g_s2_server_id
#     ret = conn.describe_s2_servers(s2_servers=[g_s2_server_id], verbose=1)
#
#     # check ret_code
#     print("ret==%s" % (ret))
#     ret_code = ret.get("ret_code")
#     print("ret_code==%s" % (ret_code))
#     if ret_code != 0:
#         print("describe_s2_servers failed")
#         exit(-1)
#
#     matched_s2_server = ret['s2_server_set']
#     print("matched_s2_server==%s"%(matched_s2_server))
#
#     print("************************************")
#     wanted_s2_server = matched_s2_server[0]
#     print("wanted_s2_server==%s" % (wanted_s2_server))
#
#     print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
#     s2_server_ip = wanted_s2_server.get('private_ip')
#     print("s2_server_ip==%s" % (s2_server_ip))
#     return s2_server_ip
#
# def get_vxnet_id():
#     print("get_vxnet_id")
#     global conn
#     #查看基础网络vxnet_id
#     ret = conn.describe_vxnets(limit=1, vxnet_type=2)
#
#     # check ret_code
#     print("ret==%s" % (ret))
#     ret_code = ret.get("ret_code")
#     print("ret_code==%s" % (ret_code))
#     if ret_code != 0:
#         print("describe_vxnets failed")
#         exit(-1)
#
#     matched_vxnet = ret['vxnet_set']
#     print("matched_vxnet==%s" % (matched_vxnet))
#
#     print("************************************")
#
#     wanted_vxnet = matched_vxnet[0]
#     print("wanted_vxnet==%s" % (wanted_vxnet))
#
#     print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
#     vxnet_id = wanted_vxnet.get('vxnet_id')
#     print("vxnet_id=%s" % (vxnet_id))
#     return vxnet_id
#
# def get_user_id():
#     print("get_user_id")
#     global conn
#     global access_key_id
#     #查看access_keys详情
#     ret = conn.describe_access_keys(access_keys=[access_key_id])
#
#     # check ret_code
#     print("ret==%s" % (ret))
#     ret_code = ret.get("ret_code")
#     print("ret_code==%s" % (ret_code))
#     if ret_code != 0:
#         print("describe_access_keys failed")
#         exit(-1)
#
#     matched_access_key = ret['access_key_set']
#     print("matched_access_key==%s" % (matched_access_key))
#
#     print("************************************")
#
#     wanted_access_key = matched_access_key[0]
#     print("wanted_access_key==%s" % (wanted_access_key))
#
#     print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
#     user_id = wanted_access_key.get('owner')
#     print("user_id=%s" % (user_id))
#     return user_id
#
# def get_volume_id(user_id):
#     print("get_volume_id")
#     global conn
#
#     ret = conn.describe_volumes(volume_type=0, status=['available'], owner=user_id,limit=1)
#
#     # check ret_code
#     print("ret==%s" % (ret))
#     ret_code = ret.get("ret_code")
#     print("ret_code==%s" % (ret_code))
#     if ret_code != 0:
#         print("describe_volumes failed")
#         exit(-1)
#
#     matched_volume = ret['volume_set']
#     if  not matched_volume:
#         print("matched_volume is null")
#         return None
#
#     print("matched_volume == %s" % (matched_volume))
#     print("************************************")
#
#     wanted_volume = matched_volume[0]
#     print("wanted_volume == %s" % (wanted_volume))
#     print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
#
#     volume_id = wanted_volume.get('volume_id')
#     print("volume_id == %s" % (volume_id))
#     return volume_id
#
# def create_new_volumes(user_id):
#     print("create_new_volumes")
#     global conn
#     volume_id = None
#
#     ret = conn.create_volumes(size=10, volume_name='vdi-portal-nas-disk', volume_type=0,count=1,target_user=user_id)
#
#     # check ret_code
#     print("ret==%s" % (ret))
#     ret_code = ret.get("ret_code")
#     print("ret_code==%s" % (ret_code))
#     if ret_code != 0:
#         print("create_volumes failed")
#         exit(-1)
#
#     num = 0
#     if ret.get("ret_code") == 0:
#         volume_id = ret.get('volumes')[0]
#         job_id = ret.get('job_id')
#         while num < 300:
#             num = num + 1
#             print("num == %d" %(num))
#             time.sleep(1)
#             status = get_job_status(job_id)
#             if status == "successful":
#                 print("create_volumes successful")
#                 break
#
#     print("volume_id == %s" % (volume_id))
#     return volume_id
#
#
# def get_s2_groups_id():
#     print("get_s2_groups_id")
#     global conn
#
#     ret = conn.describe_s2_groups(group_types=['NFS_GROUP'], limit=1)
#
#     # check ret_code
#     print("ret==%s" % (ret))
#     ret_code = ret.get("ret_code")
#     print("ret_code==%s" % (ret_code))
#     if ret_code != 0:
#         print("describe_s2_groups failed")
#         exit(-1)
#
#     matched_s2_groups = ret['s2_group_set']
#     if  not matched_s2_groups:
#         print("matched_s2_groups is null")
#         exit(-1)
#
#     print("matched_s2_groups == %s" % (matched_s2_groups))
#     print("************************************")
#
#     wanted_s2_groups = matched_s2_groups[0]
#     print("wanted_s2_groups == %s" % (wanted_s2_groups))
#     print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
#
#     s2_groups_id = wanted_s2_groups.get('group_id')
#     print("s2_groups_id == %s" % (s2_groups_id))
#     return s2_groups_id
#
#
#
# def create_s2_shared_target():
#     print("子线程启动")
#     print("create_s2_shared_target")
#     global conn
#     global g_s2_server_id
#     global g_s2_shared_target_id
#     volume_id = None
#
#     #get availlable volume 10G
#     user_id = get_user_id()
#     volume_id = get_volume_id(user_id)
#     if not volume_id:
#         print("can't get available volume")
#         print("it will start create_volumes")
#         volume_id = create_new_volumes(user_id)
#         if not volume_id:
#             print("can't create new volumes")
#             exit(-1)
#     print("get available volume volume_id == %s" %(volume_id))
#     ret = conn.create_s2_shared_target(
#         s2_server_id=g_s2_server_id,
#         volumes=[volume_id],
#         export_name='/mnt/nas',
#         target_type='NFS',
#         description='create s2 shared target'
#     )
#     # check ret_code
#     print("ret==%s" % (ret))
#     ret_code = ret.get("ret_code")
#     print("ret_code==%s" % (ret_code))
#     if ret_code != 0:
#         print("create_s2_shared_target failed")
#         exit(-1)
#
#     g_s2_shared_target_id = ret.get("s2_shared_target")
#     if  not  g_s2_shared_target_id:
#         print("g_s2_shared_target_id == %s" % (g_s2_shared_target_id))
#         print("can't get g_s2_shared_target_id")
#         exit(-1)
#
#     print("g_s2_shared_target_id==%s" % (g_s2_shared_target_id))
#     print("子线程结束")
#
#
#
# def describe_s2_account_vdi0_host():
#     print("子线程启动")
#     print("describe_s2_account_vdi0_host")
#     global conn
#     global g_s2_server_id
#     global g_s2_shared_target_id
#     global g_vdi0_ip
#     global g_vdi1_ip
#     global g_s2_account_id_vdi0_host
#     global g_s2_account_id_vdi1_host
#
#
#     ret = conn.describe_s2_accounts(search_word= g_vdi0_ip,verbose=1)
#     # check ret_code
#     print("ret==%s" % (ret))
#     ret_code = ret.get("ret_code")
#     print("ret_code==%s" % (ret_code))
#     if ret_code != 0:
#         print("describe_s2_accounts failed")
#         exit(-1)
#
#     if ret.get('ret_code') == 0:
#         if ret.get('total_count') == 1:
#             print("account ipaddr[%s] already existed" %(g_vdi0_ip))
#             # g_s2_account_id_vdi0_host = ret.get('s2_account_id')
#             matched_s2_account_set = ret['s2_account_set']
#             if not matched_s2_account_set:
#                 print("matched_s2_account_set is null")
#                 exit(-1)
#
#             print("matched_s2_account_set == %s" % (matched_s2_account_set))
#             print("************************************")
#
#             wanted_s2_account_set = matched_s2_account_set[0]
#             print("wanted_s2_account_set == %s" % (wanted_s2_account_set))
#             print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
#             g_s2_account_id_vdi0_host = wanted_s2_account_set.get('account_id')
#             print("g_s2_account_id_vdi0_host == %s" %(g_s2_account_id_vdi0_host))
#     return g_s2_account_id_vdi0_host
#     print("子线程结束")
#
# def describe_s2_account_vdi1_host():
#     print("子线程启动")
#     print("describe_s2_account_vdi1_host")
#     global conn
#     global g_s2_server_id
#     global g_s2_shared_target_id
#     global g_vdi0_ip
#     global g_vdi1_ip
#     global g_s2_account_id_vdi0_host
#     global g_s2_account_id_vdi1_host
#
#
#     ret = conn.describe_s2_accounts(search_word= g_vdi1_ip,verbose=1)
#     # check ret_code
#     print("ret==%s" % (ret))
#     ret_code = ret.get("ret_code")
#     print("ret_code==%s" % (ret_code))
#     if ret_code != 0:
#         print("describe_s2_accounts failed")
#         exit(-1)
#
#     if ret.get('ret_code') == 0:
#         if ret.get('total_count') == 1:
#             print("account ipaddr[%s] already existed" %(g_vdi1_ip))
#             # g_s2_account_id_vdi0_host = ret.get('s2_account_id')
#             matched_s2_account_set = ret['s2_account_set']
#             if not matched_s2_account_set:
#                 print("matched_s2_account_set is null")
#                 exit(-1)
#
#             print("matched_s2_account_set == %s" % (matched_s2_account_set))
#             print("************************************")
#
#             wanted_s2_account_set = matched_s2_account_set[0]
#             print("wanted_s2_account_set == %s" % (wanted_s2_account_set))
#             print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
#             g_s2_account_id_vdi1_host = wanted_s2_account_set.get('account_id')
#             print("g_s2_account_id_vdi1_host == %s" %(g_s2_account_id_vdi1_host))
#     return g_s2_account_id_vdi1_host
#     print("子线程结束")
#
#
# def update_s2_servers():
#     print("子线程启动")
#     print("update_s2_servers")
#     global conn
#     global g_s2_server_id
#     global g_s2_shared_target_id
#
#     ret = conn.update_s2_servers(s2_servers=[g_s2_server_id])
#     # check ret_code
#     print("ret==%s" % (ret))
#     ret_code = ret.get("ret_code")
#     print("ret_code==%s" % (ret_code))
#     if ret_code != 0:
#         print("update_s2_servers failed")
#         exit(-1)
#
#     time.sleep(1)
#     transition_status = "updating"
#     while transition_status !="":
#         time.sleep(1)
#         transition_status = get_s2_servers_transition_status()
#
#     print("子线程结束")
#
#
# def create_s2_account_vdi0_host():
#     print("子线程启动")
#     print("create_s2_account_vdi0_host")
#     global conn
#     global g_s2_server_id
#     global g_s2_shared_target_id
#     global g_vdi0_ip
#     global g_vdi1_ip
#     global g_s2_account_id_vdi0_host
#     global g_s2_account_id_vdi1_host
#
#     g_s2_account_id_vdi0_host = describe_s2_account_vdi0_host()
#     if not g_s2_account_id_vdi0_host:
#         ret = conn.create_s2_account(account_type='NFS',account_name='vdi0-portal-account',nfs_ipaddr= g_vdi0_ip,description='create s2 account for vdi0')
#         # check ret_code
#         print("ret==%s" % (ret))
#         ret_code = ret.get("ret_code")
#         print("ret_code==%s" % (ret_code))
#         if ret_code != 0:
#             print("create_s2_account failed")
#             exit(-1)
#
#         g_s2_account_id_vdi0_host = ret.get('s2_account_id')
#
#     print("g_s2_account_id_vdi0_host == %s" %(g_s2_account_id_vdi0_host))
#     print("子线程结束")
#
#
#
# def create_s2_account_vdi1_host():
#     print("子线程启动")
#     print("create_s2_account_vdi1_host")
#     global conn
#     global g_s2_server_id
#     global g_s2_shared_target_id
#     global g_vdi0_ip
#     global g_vdi1_ip
#     global g_s2_account_id_vdi0_host
#     global g_s2_account_id_vdi1_host
#
#     g_s2_account_id_vdi1_host = describe_s2_account_vdi1_host()
#     if not g_s2_account_id_vdi1_host:
#         ret = conn.create_s2_account(account_type='NFS',account_name='vdi0-portal-account',nfs_ipaddr= g_vdi1_ip,description='create s2 account for vdi1')
#         # check ret_code
#         print("ret==%s" % (ret))
#         ret_code = ret.get("ret_code")
#         print("ret_code==%s" % (ret_code))
#         if ret_code != 0:
#             print("create_s2_account failed")
#             exit(-1)
#
#         g_s2_account_id_vdi1_host = ret.get('s2_account_id')
#
#     print("g_s2_account_id_vdi1_host == %s" %(g_s2_account_id_vdi1_host))
#     print("子线程结束")
#
# def associate_s2_account_group_vdi0_host():
#     print("子线程启动")
#     print("associate_s2_account_group_vdi0_host")
#     global conn
#     global g_s2_server_id
#     global g_s2_shared_target_id
#     global g_s2_account_id_vdi0_host
#     global g_s2_account_id_vdi1_host
#
#     #get availlable s2_groups_id
#     s2_groups_id = get_s2_groups_id()
#     if not s2_groups_id:
#         print("can't get available s2_groups_id")
#         exit(-1)
#     print("get available s2_groups_id == %s" %(s2_groups_id))
#
#     #get s2_accounts_list
#     # s2_accounts: the JSON form of accounts. e.g. '[{"account_id": "s2a-xxxx", "rw_flag": "rw"}]'
#     s2_accounts_list = {"account_id": g_s2_account_id_vdi0_host,"rw_flag": "rw"}
#
#     #start associate_s2_account_group
#     ret = conn.associate_s2_account_group(
#         s2_group=s2_groups_id,
#         s2_accounts=[s2_accounts_list]
#     )
#     # check ret_code
#     print("ret==%s" % (ret))
#     ret_code = ret.get("ret_code")
#     print("ret_code==%s" % (ret_code))
#     if ret_code != 0:
#         print("associate_s2_account_group failed")
#         exit(-1)
#
#     print("子线程结束")
#
#
# def associate_s2_account_group_vdi1_host():
#     print("子线程启动")
#     print("associate_s2_account_group_vdi1_host")
#     global conn
#     global g_s2_server_id
#     global g_s2_shared_target_id
#     global g_s2_account_id_vdi0_host
#     global g_s2_account_id_vdi1_host
#
#     #get availlable s2_groups_id
#     s2_groups_id = get_s2_groups_id()
#     if not s2_groups_id:
#         print("can't get available s2_groups_id")
#         exit(-1)
#     print("get available s2_groups_id == %s" %(s2_groups_id))
#
#     #get s2_accounts_list
#     # s2_accounts: the JSON form of accounts. e.g. '[{"account_id": "s2a-xxxx", "rw_flag": "rw"}]'
#     s2_accounts_list = {"account_id": g_s2_account_id_vdi1_host,"rw_flag": "rw"}
#
#     #start associate_s2_account_group
#     ret = conn.associate_s2_account_group(
#         s2_group=s2_groups_id,
#         s2_accounts=[s2_accounts_list]
#     )
#
#     # check ret_code
#     print("ret==%s" % (ret))
#     ret_code = ret.get("ret_code")
#     print("ret_code==%s" % (ret_code))
#     if ret_code != 0:
#         print("associate_s2_account_group failed")
#         exit(-1)
#     print("子线程结束")

# def get_volume_id(conn,user_id,volume_type):
#     print("get_volume_id user_id == %s volume_type == %s" %(user_id,volume_type))
#     volume_id = ""
#
#     # DescribeVolumes
#     action = const.ACTION_DESCRIBE_VOLUMES
#     print("action == %s" % (action))
#     ret = conn.describe_volumes(owner=user_id,volume_type=volume_type,status=['available'],limit=1)
#     print("describe_volumes ret == %s" % (ret))
#     Common.check_ret_code(ret, action)
#
#     # get volume_id
#     volume_set = ret['volume_set']
#     if volume_set is None or len(volume_set) == 0:
#         print("describe_volumes volume_set is None")
#         return volume_id
#     for volume in volume_set:
#         volume_id = volume.get("volume_id")
#
#     return volume_id

def get_instance_class(conn,user_id,vdi_resource_id):
    print("get_instance_class user_id == %s vdi_resource_id == %s" %(user_id,vdi_resource_id))
    instance_class = 0

    if vdi_resource_id and not isinstance(vdi_resource_id, list):
        vdi_resource_id = [vdi_resource_id]
    print("vdi_resource_id == %s" %(vdi_resource_id))

    # DescribeInstances
    action = const.ACTION_DESCRIBE_INSTANCES
    print("action == %s" % (action))
    ret = conn.describe_instances(instances=vdi_resource_id, verbose=1)
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
    ret = conn.create_volumes(owner=user_id,volume_name="vdi-portal-nas",volume_type=volume_type,count=1,size=20,target_user=user_id)
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

def create_s2_shared_target(conn,user_id,vxnet_id,g_s2_server_id,instance_class):
    print("子线程启动")
    global g_s2_shared_target_id
    global g_instance_class
    print("create_s2_shared_target user_id == %s vxnet_id == %s g_s2_server_id == %s instance_class == %s" % (user_id,vxnet_id,g_s2_server_id,instance_class))

    # get the volume_type corresponding to the instance class
    volume_type = const.INSTANCE_CLASS_VOLUME_TYPE_MAP[instance_class]
    print("instance_class == %s" % (instance_class))
    print("volume_type == %s" % (volume_type))

    # get available volume_id
    volume_id = create_new_volume(conn, user_id,volume_type)
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
    ret = conn.create_s2_shared_target(owner=user_id,vxnet=vxnet_id,s2_server_id=g_s2_server_id,target_type='NFS',export_name_nfs='nas',export_name='/mnt/nas',volumes=volume_id)
    print("create_s2_shared_target ret == %s" % (ret))
    Common.check_ret_code(ret, action)

    s2_shared_target_id = ret['s2_shared_target']
    print("s2_shared_target_id == %s" % (s2_shared_target_id))

    if s2_shared_target_id:
        print("create_s2_shared_target s2_shared_target successful")
        g_s2_shared_target_id = s2_shared_target_id
        print("g_s2_shared_target_id == %s" % (g_s2_shared_target_id))
    else:
        print("create_s2_shared_target s2_shared_target failed")
        exit(-1)

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
        ret = conn.create_s2_server(owner=user_id,vxnet=vxnet_id,service_type='vnas',s2_server_name='vdi-portal-nas',s2_server_type=0,description='vdi portal nas',s2_class=s2_class)
        print("create_s2_server ret == %s" % (ret))
        Common.check_ret_code(ret, action)
    else:
        print("private_ips is %s" %(private_ips))
        # CreateS2Server
        action = const.ACTION_CREATE_S2_SERVER
        print("action == %s" % (action))
        ret = conn.create_s2_server(owner=user_id,vxnet=vxnet_id,service_type='vnas',s2_server_name='vdi-portal-nas',s2_server_type=0,description='vdi portal nas',s2_class=s2_class,private_ip=private_ips)
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

    print("g_s2_server_id == %s" % (g_s2_server_id))
    if g_s2_server_id:
        #创建子线程--新建共享存储目标
        t2 = threading.Thread(target=create_s2_shared_target,args=(conn,user_id,vxnet_id,g_s2_server_id,instance_class,))
        t2.start()
        t2.join()

    print("g_s2_shared_target_id == %s" % (g_s2_shared_target_id))

    # #创建子线程--创建vnas服务访问资源账号 vdi0客户端
    # t3 = threading.Thread(target=create_s2_account_vdi0_host)
    # t3.start()
    # t3.join()
    #
    #
    # #创建子线程--创建vnas服务访问资源账号 vdi1客户端
    # t4 = threading.Thread(target=create_s2_account_vdi1_host)
    # t4.start()
    # t4.join()
    #
    #
    # #创建子线程--将访问NFS资源的用户账户和权限组进行关联，用户加入资源组之后，就可以访问共享目录的资源 vdi0客户端
    # t5 = threading.Thread(target=associate_s2_account_group_vdi0_host)
    # t5.start()
    # t5.join()
    #
    #
    # #创建子线程--将访问NFS资源的用户账户和权限组进行关联，用户加入资源组之后，就可以访问共享目录的资源 vdi1客户端
    # t6 = threading.Thread(target=associate_s2_account_group_vdi1_host)
    # t6.start()
    # t6.join()
    #
    # #创建子线程--更新共享存储服务器的配置信息
    # t7 = threading.Thread(target=update_s2_servers)
    # t7.start()
    # t7.join()
    #
    # #s2server 写入文件
    # s2server_ip_conf = "/opt/s2server_ip_conf"
    # ret = get_s2_server_ip()
    # with open(s2server_ip_conf, "w+") as f1:
    #     f1.write("S2SERVER_ADDRESS %s" %(ret))

    print("主线程结束")

