# coding:utf-8

import datetime
import json
import os
import shlex
import subprocess
import sys
import threading
import uuid
from datetime import timedelta

import pymongo
from celery import Celery, platforms
from celery.schedules import crontab
from qaenv import eventmq_amqp, mongo_ip, mongo_port
from QAPUBSUB.consumer import subscriber, subscriber_routing

platforms.C_FORCE_ROOT = True  # 加上这一行


class celeryconfig():
    broker_url = eventmq_amqp 
    RESULT_BACKEND = "rpc://"
    task_default_queue = 'default'
    task_serializer = 'json'
    result_serializer = 'json'
    accept_content = ['application/json']
    task_compression ='gzip'
    timezone = "Asia/Shanghai"  # 时区设置
    enable_utc = False
    worker_hijack_root_logger = False  # celery默认开启自己的日志，可关闭自定义日志，不关闭自定义日志输出为空
    result_expires = 60 * 60 * 24  # 存储结果过期时间（默认1天）


app = Celery('quantaxis_jobschedule')
app.config_from_object(celeryconfig)


@app.task(bind=True)
def node(self, shell_cmd):
    """run shell
    Arguments:
        shell_cmd {[type]} -- [description]
    Node

    """
    node_id = uuid.uuid4()

    listener = subscriber_routing(
        exchange='qaschedule', routing_key=str(node_id))

    def callback(a, b, c, d, data):
        data = json.loads(data)
        try:
            threading.Thread(do_task(data['cmd'])).start()
        except:
            pass

    listener.callback = callback
    listener.start()

def do_task(shell_cmd):
    cmd = shlex.split(shell_cmd)
    p = subprocess.Popen(
        cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while p.poll() is None:
        line = p.stdout.readline()
        pass



def submit_task(taskfile):
    pass