#!/usr/bin/python
#! _*_ coding:utf-8 _*_

import os,re
import sys
import time
import random,string
import subprocess
passw='xxxx'
vers='4.4.18' #MongoDB版本
dataroot='/data' #安装的数据目录
account_verify = 1 # Cluster validation start ,0 关闭验证(Turn off validation) / １开启验证(Enable verification)

#mongos IP, port:30000
iplist_so = '''
172.xx.xxx.160
 172.xx.xxx.5
172.xx.xxx.35
'''
#config IP,port:27017
iplist_co = '''
  172.xx.xxx.177
172.xx.xxx.139
 172.xx.xxx.95
'''
#shard IP shard are separated by '|',port 40001-4000n
iplisto = '''
172.xx.xxx.186
172.xx.xxx.127
172.xx.xxx.151
|
 172.xx.xxx.117
172.xx.xxx.181
172.xx.xxx.193
|
172.xx.xxx.197
172.xx.xxx.58
172.xx.xxx.178
'''


def ip_handle_shard(ip_list):#shard副本集的ip串处理函数
   slist = []
   slistz = []
   for s in ip_list.split('|'):
      slist.append(s.strip().replace("\n", " "))
      slistz.append(slist)
      slist = []
   return slistz
def ip_handle_sc(ip_list):#mongos/config的ip串处理函数
   slist = []
   for s in ip_list.split('\n'):
      slist.append(s.strip())
   clean_iplist = [item for item in slist if item]
   clean_iplist_clsp = ' '.join(clean_iplist)
   iplist_ss = []
   iplist_ss.append(clean_iplist_clsp)
   return iplist_ss

iplist_s = ip_handle_sc(iplist_so)
iplist_c = ip_handle_sc(iplist_co)
iplist = ip_handle_shard(iplisto)

def main(argv): #外部程序调入逻辑,获取密码和ip地址串
   if len(argv) < 2:
       return argv
   argument = argv[1]
   ts = ' '
   sip = ''
   for shad_ip in iplist:
      if shad_ip != iplist[-1]:
         sip = sip + shad_ip[0] + ts
      else:
         sip = sip + shad_ip[0]
   ipsc = iplist_s[0] + ' ' + iplist_c[0] + ' ' + sip
   print('ips:'+ipsc+'|sshpassword:'+passw)
   sys.exit(1)
if __name__ == "__main__":
    main(sys.argv)

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

os.system('openssl rand -base64 753 > keyFile;chmod 400 keyFile')
shardname='rsshd'

shards = 0
# extype部署类型 1.mongod 2.config 3.mongos
extype = 1
port = 40000
add_user_ip = []
for ips in iplist:
   shards += 1
   shardnamez = shardname+str(shards)
   ip1=ips[0].split(' ')[0]
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
         if successfuls.count('successful_install') == len(ips[0].split()) and list(set(successfuls))[0] == 'successful_install':
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
   port = port + 1
   #  副本集IP拼接
   st = ','
   ipstr = ''
   for i in range(len(ips[0].split(' '))):
      print(i)
      ip=ips[0].split(' ')[i]
      print ip
      if ip != ips[0].split(' ')[-1]:
         ipst = '{\\"_id\\": %s,\\"host\\" : \\"%s:%s\\"}'%(i,ip,port)
         ipstr = ipstr + ipst + st
      elif ip == ips[0].split(' ')[-1]:
         ipst = '{\\"_id\\": %s,\\"host\\" : \\"%s:%s\\"}'%(i,ip,port)
         ipstr = ipstr + ipst
   rsinit_coun =  rsinit_head + ipstr + rsinit_tail
   time.sleep(3)
   # 1.3 副本集初始化操作
   print('副本集 '+ips[0]+' 初始化开始......')
   os.system('sshpass -p\'%s\'  ssh  root@%s -o StrictHostKeyChecking=no "echo \'%s\'|/usr/local/mongodb/bin/mongo %s:%s"' %(passw,ip1,rsinit_coun,ip1,port))
   #判断shard的副本集是否产生主节点
   while True:
      primary_node = function_primary(ip1,passw,port)
      for n in range(60):
         time.sleep(n)
         if primary_node == 'PRIMARY':
            pd = 'PRIMARY'
            # 获取副本集主节点IP地址
            ip_str = os.popen('sshpass -p\'%s\'  ssh  root@%s -o StrictHostKeyChecking=no "echo \'rs.status()\'|/usr/local/mongodb/bin/mongo localhost:%s|grep -E \'name|stateStr\'|sed \'N;s/\\n//\'|grep PRIMARY"'%(passw,ip1,port)).read().strip().split(':')[1].replace('"','')
            ipList = re.findall( r'[0-9]+(?:\.[0-9]+){3}',ip_str)[0]
            os.system('sshpass -p %s scp %s  root@%s:/root/' %(passw,'create_user.js',ipList))
            #副本集主节点创建管理账号
            os.system('sshpass -p\'%s\'  ssh  root@%s -o StrictHostKeyChecking=no  "/usr/local/mongodb/bin/mongo %s:%s/admin < create_user.js"' %(passw,ipList,ipList,port))
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

#检查config副本集实例安装结果
while True:
   successfuls = []
   for ip in iplist_c[0].split(' '):
      example_ps = function_psef(ip,passw)
      successfuls.append(example_ps)
   for n in range(60):
      time.sleep(n)
      if successfuls.count('successful_install') == len(iplist_c[0].split()) and list(set(successfuls))[0] == 'successful_install':
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

# config副本集IP拼接
st = ','
ipstr = ''
ipstc = ''
portc = '27017'
for i in range(len(iplist_c[0].split(' '))):
   print i
   ip=iplist_c[0].split(' ')[i]
   print ip
   if ip != iplist_c[0].split(' ')[-1]:
      ipst = '{\\"_id\\": %s,\\"host\\" : \\"%s:%s\\"}'%(i,ip,portc)
      ipsc = ip + ':' + portc
      ipstc = ipstc + ipsc + st
      ipstr = ipstr + ipst + st
   elif ip == iplist_c[0].split(' ')[-1]:
      ipst = '{\\"_id\\": %s,\\"host\\" : \\"%s:%s\\"}'%(i,ip,portc)
      ipsc = ip + ':' + portc
      ipstc = ipstc + ipsc
      ipstr = ipstr + ipst
rsinit_coun =  rsinit_head + ipstr + rsinit_tail
# 2.2 config副本集初始化
os.system('sshpass -p \'%s\'  ssh  root@%s -o StrictHostKeyChecking=no "echo \'%s\'|/usr/local/mongodb/bin/mongo %s:%s"' %(passw,ip1,rsinit_coun,ip1,portc))

#判断config的副本集是否已产生主节点
while True:
   primary_node = function_primary(ip,passw,portc)
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
ip_str = os.popen('sshpass -p\'%s\'  ssh  root@%s -o StrictHostKeyChecking=no "echo \'rs.status()\'|/usr/local/mongodb/bin/mongo %s:%s|grep -E \'name|stateStr\'|sed \'N;s/\\n//\'|grep PRIMARY"' %(passw,ip1,ip1,portc)).read().strip().split(':')[1].replace('"','')
ipList = re.findall( r'[0-9]+(?:\.[0-9]+){3}',ip_str)[0]
#副本集主节点创建管理账号
os.system('sshpass -p %s scp %s  root@%s:/root/' %(passw,'create_user.js',ipList))
time.sleep(1)
os.system('sshpass -p\'%s\'  ssh  root@%s -o StrictHostKeyChecking=no  "/usr/local/mongodb/bin/mongo %s:%s/admin < create_user.js"' %(passw,ipList,ipList,portc))
time.sleep(1)

#// 3、 mongos节点部署
extype = 3
cfdbs = '  configDB: '+replSetName+'/'+ipstc
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
port = 40000
# 3.2 添加集群分片
for ips in iplist:
   shardn += 1
   port = port + 1
   addshard_head = 'sh.addShard(\\"'
   # 添加分片的副本集ip串拼接
   ipsts = ''
   st= ','
   for i in range(len(ips[0].split(' '))):
      print(i)
      ip=ips[0].split(' ')[i]
      print ip
      if ip != ips[0].split(' ')[-1]:
         ipss = ip+':'+str(port)
         ipsts = ipsts + ipss + st
      elif ip == ips[0].split(' ')[-1]:
         ipss = ip+':'+str(port)
         ipsts = ipsts + ipss
   addshard = shardname+str(shardn)+'/'+ipsts 
   addshard_tail = '\\")'
   addshardc = addshard_head + addshard + addshard_tail
   shows = 'sh.status()'
   os.system('sshpass -p \'%s\'  ssh  root@%s -o StrictHostKeyChecking=no "echo \'%s\'|/usr/local/mongodb/bin/mongo localhost:30000"' %(passw,iplist_s[0].split(' ')[0],addshardc))
   time.sleep(3)
#将密码写入日志中，方便后续查看
file = open('/data/mongodb/logs/mongo_route.log','a')
file.write('%s mongodb_password: %s \n' %(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()),password))
file.close()
#把mognodb集群信息记录到集群config库的mongodb_configs集合中
os.system("echo 'db.mongodb_configs.insert({\"mongos_30000\" : \"%s\",\"config_%s\" : \"%s\",\"shards_40001-%s\":\"%s\"})'|/usr/local/mongodb/bin/mongo localhost:30000/config" %(iplist_s,portc,iplist_c,port,iplist))

# 获取IP
mongos = os.popen("echo 'db.mongodb_configs.find({},{\"mongos_30000\":1, \"_id\":0})'|/usr/local/mongodb/bin/mongo localhost:30000/config|grep mongos_30000|grep -Po '(?<=\[).*?(?=\])'|tail -n1").read().strip()
config = os.popen("echo 'db.mongodb_configs.find({},{\"config_27017\":1, \"_id\":0})'|/usr/local/mongodb/bin/mongo localhost:30000/config|grep config_27017|grep -Po '(?<=\[).*?(?=\])'|tail -n1").read().strip()
shards = os.popen("echo 'db.mongodb_configs.find({},{\"shards_40001-%s\":1, \"_id\":0})'|/usr/local/mongodb/bin/mongo localhost:30000/config|grep shards_40001|grep -Po '(?<=\"\[).*?(?=\]\")'|grep -Po '(?<=\[).*?(?=\])'" %(port)).read().strip().replace("\n", " ")
all_ip = mongos + ' ' + config + ' ' + shards
print all_ip
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
if account_verify == 1:
   os.system("sh cluster_add_security_key.sh \'%s\' \'%s\' \'%s\' \'%s\' %s " %(mongos,config,shards,all_ip,passw))
elif account_verify == 0:
   exit()
