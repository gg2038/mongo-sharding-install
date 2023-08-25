#!/usr/bin/python
#! _*_ coding:utf-8 _*_

from pymongo import MongoClient
import threading
import time

# 连接单机 # Connecting single machine
# single mongo
# c = MongoClient(host="172.xx.xx.xx", port=27017)

# 连接集群 # Connected cluster
def worker():
    """线程执行的函数"""   """ A function executed by a thread """
    c = MongoClient('mongodb://172.xx.xx.204:30000,172.xx.xx.205:30000,172.xx.xx.206:30000')
    db = c.eoo
    myset = db.bar
    for i in range(1,1000):
        myset.insert({"u" :str(i), "name" : "sz"+str(i), "city" : "nn"+str(i),"type":'t'+str(i),"addr":"http://server"+str(i)})
    print("线程启动")

threads = []
for i in range(100):
    t = threading.Thread(target=worker)
    threads.append(t)
    t.start()

for t in threads:
    t.join()