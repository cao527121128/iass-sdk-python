'''
Created on 2019-9-8

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

# ---------------------------------------------
#       Here puts common functions used in API
# ---------------------------------------------

def connect_iaas(zone_id, access_key_id, secret_access_key, host,port,protocol):
    print("connect_iaas")
    print("starting connect_to_zone ...")

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
    return conn

def get_user_id(conn, access_key_id):
    print("get_user_id")

    # DescribeAccessKeys
    action = const.ACTION_DESCRIBE_ACCESS_KEYS
    print("action == %s" % (action))
    ret = conn.describe_access_keys(access_keys=[access_key_id])
    print("describe_access_keys ret == %s" % (ret))
    check_ret_code(ret, action)
    access_key_set = ret['access_key_set']
    if access_key_set is None or len(access_key_set) == 0:
        print("describe_access_keys access_key_set is None")
        exit(-1)
    for access_key in access_key_set:
        user_id = access_key.get("owner")
    return user_id

def get_vxnet_id(conn,vxnet_type):
    print("get_vxnet_id")

    # DescribeVxnets
    action = const.ACTION_DESCRIBE_VXNETS
    print("action == %s" % (action))
    ret = conn.describe_vxnets(limit=1, vxnet_type=2)
    print("describe_vxnets ret == %s" % (ret))
    check_ret_code(ret, action)
    vxnet_set = ret['vxnet_set']
    if vxnet_set is None or len(vxnet_set) == 0:
        print("describe_vxnets vxnet_set is None")
        exit(-1)
    for vxnet in vxnet_set:
        vxnet_id = vxnet.get("vxnet_id")
    return vxnet_id

def check_ret_code(ret,action):
    ret_code = ret.get("ret_code")
    if ret_code != 0:
        print("%s failed" %(action))
        exit(-1)

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

def get_job_status(conn,job_id):
    print("get_job_status job_id == %s" %(job_id))

    if job_id and not isinstance(job_id, list):
        job_id = [job_id]

    # DescribeJobs
    action = const.ACTION_DESCRIBE_JOBS
    print("action == %s" % (action))
    ret = conn.describe_jobs(jobs=job_id,verbose=1)
    check_ret_code(ret, action)
    job_set = ret['job_set']
    if job_set is None or len(job_set) == 0:
        print("describe_jobs job_set is None")
        return None
    for job in job_set:
        status = job.get("status")
    print("status == %s" %(status))
    return status