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


def get_user_id():
    print("get_user_id")
    global conn
    global access_key_id

    ret = conn.describe_access_keys(access_keys=[access_key_id])
    ret_code = ret.get("ret_code")
    if ret_code != 0:
        print("describe_access_keys failed")
        exit(-1)
    matched_access_key = ret['access_key_set']
    wanted_access_key = matched_access_key[0]
    user_id = wanted_access_key.get('owner')
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


def get_job_status(job_id):
    print("get_job_status")
    global conn
    ret = conn.describe_jobs(jobs=[job_id],verbose=1)

    # check ret_code
    print("ret==%s" % (ret))
    ret_code = ret.get("ret_code")
    print("ret_code==%s" % (ret_code))
    if ret_code != 0:
        print("describe_jobs failed")
        exit(-1)

    matched_job_set = ret['job_set']
    print("matched_job_set == %s"%(matched_job_set))

    print("************************************")

    wanted_job_set = matched_job_set[0]
    print("wanted_job_set == %s" % (wanted_job_set))

    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    status = wanted_job_set.get('status')
    print("status=%s" % (status))
    return status


def capture_instance_from_snapshot(snapshots_id):
    print("子线程启动")
    print("capture_instance_from_snapshot")
    print("snapshots_id == %s" %(snapshots_id))
    user_id = get_user_id()
    snapshots_id_string = snapshots_id[0]
    print("snapshots_id_string == %s" % (snapshots_id_string))

    #将指定备份导出为映像
    ret = conn.capture_instance_from_snapshot(snapshot=snapshots_id_string,image_name="image_from_snapshot_1750")

    # check ret_code
    print("ret==%s" % (ret))
    ret_code = ret.get("ret_code")
    print("ret_code==%s" % (ret_code))
    if ret_code != 0:
        print("capture_instance_from_snapshot failed")
        exit(-1)

    # check job status
    num = 0
    if ret.get("ret_code") == 0:
        job_id = ret.get('job_id')
        while num < 300:
            num = num + 1
            print("num == %d" % (num))
            time.sleep(1)
            status = get_job_status(job_id)
            if status == "successful":
                print("capture_instance_from_snapshot successful")
                break
    #check image_id
    image_id = ret.get("image_id",0)
    print("image_id == %s" %(image_id))

    print("子线程结束")


def describe_snapshot(snapshots_id):
    print("子线程启动")
    print("describe_snapshot")
    print("snapshots_id == %s" %(snapshots_id))
    user_id = get_user_id()

    # 查询备份
    ret = conn.describe_snapshots(snapshots=snapshots_id,owner=user_id,offset=0,limit=1,verbose=1)

    # check ret_code
    print("ret==%s" % (ret))
    ret_code = ret.get("ret_code")
    print("ret_code==%s" % (ret_code))
    if ret_code != 0:
        print("describe_snapshots failed")
        exit(-1)

    #check snapshot_name and description
    matched_snapshot_set = ret['snapshot_set']
    print("matched_snapshot_set == %s" % (matched_snapshot_set))

    print("************************************")

    wanted_snapshot_set = matched_snapshot_set[0]
    print("wanted_snapshot_set == %s" % (wanted_snapshot_set))

    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    snapshot_name = wanted_snapshot_set.get('snapshot_name')
    print("snapshot_name == %s" % (snapshot_name))
    description = wanted_snapshot_set.get('description')
    print("description == %s" % (description))


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

    opt_parser.add_option("-n", "--snapshots_id", action="store", type="string", \
                          dest="snapshots_id", help='snapshots id', default="")


    (options, _) = opt_parser.parse_args(sys.argv)

    zone_id = options.zone_id
    access_key_id = options.access_key_id
    secret_access_key = options.secret_access_key
    host = options.host
    port = options.port
    protocol = options.protocol
    snapshots_id = explode_array(options.snapshots_id or "")

    print("zone_id:%s" % (zone_id))
    print("access_key_id:%s" % (access_key_id))
    print("secret_access_key:%s" % (secret_access_key))
    print("host:%s" % (host))
    print("port:%s" % (port))
    print("protocol:%s" % (protocol))
    print("snapshots_id:%s" % (snapshots_id))


    #连接iaas后台
    connect_iaas(zone_id, access_key_id, secret_access_key, host,port,protocol)


    #创建子线程--将指定备份导出为映像。请注意，此备份点必须为主机的备份点才能导出为映像。
    t = threading.Thread(target=capture_instance_from_snapshot,args=(snapshots_id,))
    t.start()
    t.join()

    #创建子线程--查询备份
    t1 = threading.Thread(target=describe_snapshot,args=(snapshots_id,))
    t1.start()
    t1.join()


    print("主线程结束")

