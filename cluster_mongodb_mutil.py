#!/usr/bin/python
#! _*_ coding:utf-8 _*_

import os
import sys
import time
passw='xxxxxx'

#    cluster_mongodb_mutil.py
#    mongo_mutil.sh
#    mongodb_install.sh
#    config_install.sh
#    mongos_install.sh
# 列表中一个元素包含一个分片集群地址

os.system('/usr/bin/which sshpass;if [[ "$?" != "0" ]];then  yum -y install sshpass ;fi')

iplist = [["172.xx.xx.xx3 172.xx.xx.xx4 172.xx.xx.xx5"],["172.xx.xx.xx6 172.xx.xx.xx7 172.xx.xx.xx8"],["172.xx.xx.xx9 172.xx.xx.170 172.xx.xx.171"]]
shardname='rsshd'

shards = 0
# extype部署类型 1.mongod 2.config 3.mongos
os.system('yum -y install sshpass')
time.sleep(3)
extype = 1
for ips in iplist:
   shards += 1
   #1.1 副本集批量安装
    #传送副本集IP组给脚本安装副本集
   shardnamez = shardname+str(shards)
   os.system("sh mongo_mutil.sh  \'%s\' %s %s" %(ips[0],extype,shards))
   time.sleep(5)
   #1.2. 副本集初始化命令拼接
   rsinit_head = 'rs.initiate({\\"_id\\": \\"%s\\",\\"members\\" :[' %(shardnamez)
   rsinit_tail = ']})'
   ip1=ips[0].split(' ')[0]
   ip2=ips[0].split(' ')[1]
   ip3=ips[0].split(' ')[2]
   #  一主二从
   ipstr = '{\\"_id\\": 0,\\"host\\" : \\"%s:40001\\"},''{\\"_id\\": 1,\\"host\\" : \\"%s:40001\\"},''{\\"_id\\": 2,\\"host\\" : \\"%s:40001\\"}'%(ip1,ip2,ip3)
   #  一主一从
#   ipstr = '{\\"_id\\": 0,\\"host\\" : \\"%s:40001\\"},''{\\"_id\\": 1,\\"host\\" : \\"%s:40001\\"}'%(ip1,ip2)
   rsinit_coun =  rsinit_head + ipstr + rsinit_tail
   # 1.3 副本集初始化操作
   os.system('sshpass -p\'%s\'  ssh  root@%s -o StrictHostKeyChecking=no "echo \'%s\'|/usr/local/mongodb/bin/mongo %s:40001"' %(passw,ip1,rsinit_coun,ip1))
   time.sleep(3)
   rs_status = 'rs.status()'
   os.system('sshpass -p\'%s\'  ssh  root@%s -o StrictHostKeyChecking=no "echo \'%s\'|/usr/local/mongodb/bin/mongo %s:40001"' %(passw,ip1,rs_status,ip1))

time.sleep(2)

#// 2、 config节点部署
iplist_c = ["172.xx.xx.xx0 172.xx.xx.xx1 172.xx.xx.xx2"]
extype = 2
# 2.1 config节点复制集部署
os.system("sh mongo_mutil.sh  \'%s\' %s" %(iplist_c[0],extype))
time.sleep(5) #让子脚本运行完
replSetName = "rscnf" #config复制集名
rsinit_head = 'rs.initiate({\\"_id\\": \\"%s\\",\\"members\\" :[' %(str(replSetName))
rsinit_tail = ']})'
ip1=iplist_c[0].split(' ')[0]
ip2=iplist_c[0].split(' ')[1]
ip3=iplist_c[0].split(' ')[2]
# 一主二从
ipstr = '{\\"_id\\": 0,\\"host\\" : \\"%s:27017\\"},''{\\"_id\\": 1,\\"host\\" : \\"%s:27017\\"},''{\\"_id\\": 2,\\"host\\" : \\"%s:27017\\"}'%(ip1,ip2,ip3)
# 一主一从
#ipstr = '{\\"_id\\": 0,\\"host\\" : \\"%s:27017\\"},''{\\"_id\\": 1,\\"host\\" : \\"%s:27017\\"}'%(ip1,ip2)
rsinit_coun =  rsinit_head + ipstr + rsinit_tail
# 2.2 config副本集初始化
os.system('sshpass -p \'%s\'  ssh  root@%s -o StrictHostKeyChecking=no "echo \'%s\'|/usr/local/mongodb/bin/mongo localhost:27017"' %(passw,ip1,rsinit_coun))
time.sleep(3)

#// 3、 mongos节点部署
iplist_s = ["172.xx.xx.157 172.xx.xx.158 172.xx.xx.159"]
ip1=iplist_c[0].split(' ')[0]
ip2=iplist_c[0].split(' ')[1]
ip3=iplist_c[0].split(' ')[2]
extype = 3
cfdbs = '  configDB: '+replSetName+'/'+ip1+':27017,'+ip2+':27017,'+ip3+':27017'
os.system('sed -i "s|`grep configDB mongos_install.sh`|%s|g" mongos_install.sh'%(cfdbs))

#// 3.1 安装mongos节点
os.system("sh mongo_mutil.sh  \'%s\' %s" %(iplist_s[0],extype))
time.sleep(8) # 让安装程序跑一会

shardn = 0
# 3.2 添加集群分片
for ips in iplist:
   shardn += 1
   addshard_head = 'sh.addShard(\\"'
   # 分片副本集一主二从
   addshard = shardname+str(shardn)+'/'+ips[0].split(' ')[0]+':40001,'+ips[0].split(' ')[1]+':40001,'+ips[0].split(' ')[2]+':40001'
   # 分片副本集一主一从
   #addshard = shardname+str(shardn)+'/'+ips[0].split(' ')[0]+':40001,'+ips[0].split(' ')[1]+':40001'
   addshard_tail = '\\")'
   addshardc = addshard_head + addshard + addshard_tail
   print(addshardc)
   print(iplist_s[0].split(' ')[0])
   shows = 'sh.status()'
   os.system('sshpass -p \'%s\'  ssh  root@%s -o StrictHostKeyChecking=no "echo \'%s\'|/usr/local/mongodb/bin/mongo localhost:30000"' %(passw,iplist_s[0].split(' ')[0],addshardc))
   time.sleep(3) 

#把mognodb集群信息记录到集群ev_test库的mongodb_configs集合中
os.system("echo 'db.mongodb_configs.insert({\"mongos_30000\" : \"%s\",\"config_27017\" : \"%s\",\"shards_40001\":\"%s\"})'|/usr/local/mongodb/bin/mongo localhost:30000/config" %(iplist_s,iplist_c,iplist))

# Closing remarks
n = 1
for i in range(20,14,-1):
   print(' '*i+'*'*n)
   n = n + 2
n = 11
for i in range(15,19):
   print(' '*i+'*'*n)
   n = n - 2
for i in range(3):
   print(' '*19+'*'*1+' '+'*'*1)
print(' '*20+'*'*1)
s = "[ MongoDB ]"
x = '★★★'
print('\033[1;33;40m%s\033[0m''分片集群已经部署完成''\033[1;34;40m%s\033[0m''~' %(s,x))
