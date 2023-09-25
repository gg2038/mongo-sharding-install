#!/usr/bin/python
#! _*_ coding:utf-8 _*_

import os,re
import sys
import time
import random,string
import subprocess

passw='xxx'

iplist_s = ['172.x.xxx.243 172.x.xxx.244 172.x.xxx.245'] #location mongos port:30000
iplist_c = ['172.x.xxx.246 172.x.xxx.247 172.x.xxx.248'] #location config port:27017
iplist = [['172.x.xxx.105 172.x.xxx.106 172.x.xxx.107'], ['172.x.xxx.108 172.x.xxx.109 172.x.xxx.110'], ['172.x.xxx.111 172.x.xxx.112 172.x.xxx.113']] #location sharding port 40001

os.system('/usr/bin/which sshpass;if [[ "$?" != "0" ]];then  yum -y install sshpass ;fi')
# update your ip search location
num = string.ascii_letters+string.digits
password =  "".join(random.sample(num,12))
if os.path.exists('create_user.js'):
   os.remove('create_user.js')
file = open('create_user.js', 'a')
file.write('db.createUser({user:"admin", pwd:"%s", roles:[{role:"userAdminAnyDatabase",db:"admin"}]});\n' %(password))
file.write('db.createUser({user: "root",pwd: "%s",roles:[{role: "root", db: "admin"}]});\n' %(password))
file.close()
#检实例安装结果函数
def function_psef(ip,passw):
   # 执行命令
   command = "sshpass -p\'%s\'  ssh  root@%s -o StrictHostKeyChecking=no 'netstat -tnlp|grep mongo'"%(passw,ip)
   process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   # 等待命令执行完成
   stdout, stderr = process.communicate()
   # 检查命令是否执行成功
   if process.returncode == 0:
      return 'successful_install'
   else:
      return "failure_install"

#检副本集是否已经选举出 PRIMARY-函数
def function_primary(ip,passw,port):
   command = 'sshpass -p\'%s\'  ssh  root@%s -o StrictHostKeyChecking=no "echo \'rs.status()\'|/usr/local/mongodb/bin/mongo %s:%s|grep PRIMARY"'%(passw,ip,ip,port)
   process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   stdout, stderr = process.communicate()
   if process.returncode == 0:
      return 'PRIMARY'
   else:
      return 'SECONDARY'

#    cluster_mongodb_mutil.py
#    mongo_mutil.sh
#    mongodb_install.sh
#    config_install.sh
#    mongos_install.sh
# 列表中一个元素包含一个分片集群地址
os.system('openssl rand -base64 753 > keyFile;chmod 400 keyFile')
shardname='rsshd'

shards = 0
# extype部署类型 1.mongod 2.config 3.mongos
extype = 1
add_user_ip = []
for ips in iplist:
   shards += 1
   shardnamez = shardname+str(shards)
   ip1=ips[0].split(' ')[0]
   ip2=ips[0].split(' ')[1]
   ip3=ips[0].split(' ')[2]
   add_user_ip.append(ip1)
   #1.1 副本集批量安装
   #传送副本集IP组给脚本安装副本集
   os.system("sh mongo_mutil.sh  \'%s\' %s %s %s" %(ips[0],extype,passw,shards))
   #判断副本集实例都安装成功
   while True:
      successfuls = []
      for ip in ips[0].split(' '):
         example_ps = function_psef(ip,passw)
         successfuls.append(example_ps)
      for n in range(60):
         time.sleep(n)
         if successfuls.count('successful_install') == 3 and list(set(successfuls))[0] == 'successful_install':
            pd = 'successful_install'
            break
         else:
            pd = ''
            if n == 30:#判断sharding副本集节点部署没有全部成功，退出脚本
               print('安装副本集'+ips[0]+'失败!')
               exit()
            break
      if pd == 'successful_install':
         print('副本集 '+ips[0]+' 实例安装成功!')
         break

   #1.2. 副本集初始化命令拼接
   rsinit_head = 'rs.initiate({\\"_id\\": \\"%s\\",\\"members\\" :[' %(shardnamez)
   rsinit_tail = ']})'
   #  一主二从
   ipstr = '{\\"_id\\": 0,\\"host\\" : \\"%s:40001\\"},''{\\"_id\\": 1,\\"host\\" : \\"%s:40001\\"},''{\\"_id\\": 2,\\"host\\" : \\"%s:40001\\"}'%(ip1,ip2,ip3)
   #  一主一从
#   ipstr = '{\\"_id\\": 0,\\"host\\" : \\"%s:40001\\"},''{\\"_id\\": 1,\\"host\\" : \\"%s:40001\\"}'%(ip1,ip2)
   rsinit_coun =  rsinit_head + ipstr + rsinit_tail
   time.sleep(5)
   # 1.3 副本集初始化操作
   print('副本集 '+ips[0]+' 初始化开始......')
   os.system('sshpass -p\'%s\'  ssh  root@%s -o StrictHostKeyChecking=no "echo \'%s\'|/usr/local/mongodb/bin/mongo %s:40001"' %(passw,ip1,rsinit_coun,ip1))
   #判断shard的副本集是否产生主节点
   while True:
      port = 40001
      primary_node = function_primary(ip1,passw,port)
      for n in range(60):
         time.sleep(n)
         if primary_node == 'PRIMARY':
            pd = 'PRIMARY'
            # 获取副本集主节点IP地址
            ip_str = os.popen('sshpass -p\'%s\'  ssh  root@%s -o StrictHostKeyChecking=no "echo \'rs.status()\'|/usr/local/mongodb/bin/mongo localhost:40001|grep -E \'name|stateStr\'|sed \'N;s/\\n//\'|grep PRIMARY"'%(passw,ip1)).read().strip().split(':')[1].replace('"','')
            ipList = re.findall( r'[0-9]+(?:\.[0-9]+){3}',ip_str)[0]
            os.system('sshpass -p %s scp %s  root@%s:/root/' %(passw,'create_user.js',ipList))
            #副本集主节点创建管理账号
            os.system('sshpass -p\'%s\'  ssh  root@%s -o StrictHostKeyChecking=no  "/usr/local/mongodb/bin/mongo %s:40001/admin < create_user.js"' %(passw,ipList,ipList))
            break
         else:
            pd = ''
            if n == 30:#判断副本集在30秒内没有选举出primary，退出脚本
               print('安装sharding副本集'+ips[0]+'在30秒内没有选举出primary，退出脚本.')
               exit()
            break
      if pd == 'PRIMARY':
         break

#// 2、 config节点部署
extype = 2
# 2.1 config节点复制集部署
os.system("sh mongo_mutil.sh  \'%s\' %s %s" %(iplist_c[0],extype,passw))

replSetName = "rscnf" #config复制集名
rsinit_head = 'rs.initiate({\\"_id\\": \\"%s\\",\\"members\\" :[' %(str(replSetName))
rsinit_tail = ']})'
ip1=iplist_c[0].split(' ')[0]
ip2=iplist_c[0].split(' ')[1]
ip3=iplist_c[0].split(' ')[2]

#检查config副本集实例安装结果
while True:
   successfuls = []
   for ip in iplist_c[0].split(' '):
      example_ps = function_psef(ip,passw)
      successfuls.append(example_ps)
   for n in range(60):
      time.sleep(n)
      if successfuls.count('successful_install') == 3 and list(set(successfuls))[0] == 'successful_install':
         print('config副本集'+iplist_c[0]+'实例部署成功!')
         pd = 'successful_install'
         break
      else:
         pd = ''
         if n == 30:#判断副本集节点部署没有全部成功，退出脚本
            print('安装config副本集'+iplist_c[0]+'失败!,退出脚本.')
            exit()
         break
   if pd == 'successful_install':
      print('副本集 '+iplist_c[0]+' 实例安装成功!')
      break

# 一主二从
ipstr = '{\\"_id\\": 0,\\"host\\" : \\"%s:27017\\"},''{\\"_id\\": 1,\\"host\\" : \\"%s:27017\\"},''{\\"_id\\": 2,\\"host\\" : \\"%s:27017\\"}'%(ip1,ip2,ip3)
# 一主一从
#ipstr = '{\\"_id\\": 0,\\"host\\" : \\"%s:27017\\"},''{\\"_id\\": 1,\\"host\\" : \\"%s:27017\\"}'%(ip1,ip2)
rsinit_coun =  rsinit_head + ipstr + rsinit_tail
# 2.2 config副本集初始化
os.system('sshpass -p \'%s\'  ssh  root@%s -o StrictHostKeyChecking=no "echo \'%s\'|/usr/local/mongodb/bin/mongo %s:27017"' %(passw,ip1,rsinit_coun,ip1))

#判断config的副本集是否已产生主节点
while True:
   port = 27017
   primary_node = function_primary(ip,passw,port)
   for n in range(60):
      time.sleep(n)
      if primary_node == 'PRIMARY':
         pd = 'PRIMARY'
         break
      else:
         pd = ''
         if n == 30:#判断config副本集在30秒内没有选举出primary，退出脚本
            print('初始化config副本集'+iplist_c[0]+'在30秒内没有选举出primary，退出脚本.')
            exit()
         break
   if pd == 'PRIMARY':
      break

# 获取副本集主节点IP地址
ip_str = os.popen('sshpass -p\'%s\'  ssh  root@%s -o StrictHostKeyChecking=no "echo \'rs.status()\'|/usr/local/mongodb/bin/mongo %s:27017|grep -E \'name|stateStr\'|sed \'N;s/\\n//\'|grep PRIMARY"' %(passw,ip1,ip1)).read().strip().split(':')[1].replace('"','')
ipList = re.findall( r'[0-9]+(?:\.[0-9]+){3}',ip_str)[0]
#副本集主节点创建管理账号
os.system('sshpass -p %s scp %s  root@%s:/root/' %(passw,'create_user.js',ipList))
time.sleep(2)
os.system('sshpass -p\'%s\'  ssh  root@%s -o StrictHostKeyChecking=no  "/usr/local/mongodb/bin/mongo %s:27017/admin < create_user.js"' %(passw,ipList,ipList))
time.sleep(2)

#// 3、 mongos节点部署
ip1=iplist_c[0].split(' ')[0]
ip2=iplist_c[0].split(' ')[1]
ip3=iplist_c[0].split(' ')[2]
extype = 3
cfdbs = '  configDB: '+replSetName+'/'+ip1+':27017,'+ip2+':27017,'+ip3+':27017'
print('开始部署mongos......')
os.system('sed -i "s|`grep configDB mongos_install.sh`|%s|g" mongos_install.sh'%(cfdbs))

#// 3.1 安装mongos节点
os.system("sh mongo_mutil.sh  \'%s\' %s %s" %(iplist_s[0],extype,passw))

while True:
   successfuls = []
   for ip in ips[0].split(' '):
      example_ps = function_psef(ip,passw)
      successfuls.append(example_ps)
   for n in range(60):
      print(n)
      time.sleep(n)
      if successfuls.count('successful_install') == 3 and list(set(successfuls))[0] == 'successful_install':
         print('mongos实例节点部署成功!')
         pd = 'successful_install'
         break
      else:
         pd = ''
         if n == 30:#判断安装mongos在30秒内没有选举出primary，退出脚本
            print('安装mongos'+iplist_s[0]+'失败!,退出脚本.')
            exit()
         break
   if pd == 'successful_install':
      print('mongos '+iplist_s[0]+' 实例安装成功!')
      break
time.sleep(3)
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
   shows = 'sh.status()'
   os.system('sshpass -p \'%s\'  ssh  root@%s -o StrictHostKeyChecking=no "echo \'%s\'|/usr/local/mongodb/bin/mongo localhost:30000"' %(passw,iplist_s[0].split(' ')[0],addshardc))
   time.sleep(5)
#将密码写入日志中，方便后续查看
file = open('/data/mongodb/logs/mongo_route.log','a')
file.write('%s mongodb_password: %s \n' %(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()),password))
file.close()
#把mognodb集群信息记录到集群ev_test库的mongodb_configs集合中
os.system("echo 'db.mongodb_configs.insert({\"mongos_30000\" : \"%s\",\"config_27017\" : \"%s\",\"shards_40001\":\"%s\"})'|/usr/local/mongodb/bin/mongo localhost:30000/config" %(iplist_s,iplist_c,iplist))


# 获取IP
mongos = os.popen("echo 'db.mongodb_configs.find({},{\"mongos_30000\":1, \"_id\":0})'|/usr/local/mongodb/bin/mongo localhost:30000/config|grep mongos_30000|grep -Po '(?<=\[).*?(?=\])'|tail -n1").read().strip()
config = os.popen("echo 'db.mongodb_configs.find({},{\"config_27017\":1, \"_id\":0})'|/usr/local/mongodb/bin/mongo localhost:30000/config|grep config_27017|grep -Po '(?<=\[).*?(?=\])'|tail -n1").read().strip()
shards = os.popen("echo 'db.mongodb_configs.find({},{\"shards_40001\":1, \"_id\":0})'|/usr/local/mongodb/bin/mongo localhost:30000/config|grep shards_40001|grep -Po '(?<=\"\[).*?(?=\]\")'|grep -Po '(?<=\[).*?(?=\])'").read().strip().replace("\n", " ")
all_ip = mongos + ' ' + config + ' ' + shards

#是否开启验证
#secpd = raw_input("请问需要开启验证吗/Do I need to turn on verification?(y/n): ")
#if secpd == "y":
#   print(secpd)

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
print('\033[1;33;40m%s\033[0m''分片集群已经部署完成''\033[1;34;40m%s\033[0m''~ 集群重启中~' %(s,x))
print('MongoDB集群密码在日志里-_- mongodb_password')
#添加验证功能和重启集群
os.system("sh cluster_add_security_key.sh \'%s\' \'%s\' \'%s\' \'%s\' %s " %(mongos,config,shards,all_ip,passw))
