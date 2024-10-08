#!/bin/bash
# config install
# /data/mongodb /{data,logs,conf}

dataroot=$1
ver=$2
setip='0.0.0.0'
addcmd(){
addText=$1
file=$2
#判断 file.sh 文件中是否存在该字符串
#Check whether the character string exists in the file.sh file
if ! grep "$addText" $file  >/dev/null
then
#不存在，添加字符串
# Does not exist, add a string
   echo $addText >> $file
else
#存在，不做处理
#Exist, do not process
   echo $addText" exist in "$file
fi
}
#wget mongodb-linux-x86_64-rhel70-4.4.18.tgz
tar xzvf mongodb-linux-x86_64-rhel70-$ver.tgz -C /opt
ln -snf /opt/mongodb-linux-x86_64-rhel70-$ver /usr/local/mongodb
basedir='/usr/local/mongodb'
datadir=$dataroot'/mongodb'
logdir=$dataroot'/mongodb/logs'


# rm $datadir/* -rf
mkdir -p $logdir

#mkdir -p ${dataroot}/mongodb/config
mkdir ${dataroot}/mongodb/{conf,config}

addcmd 'export PATH=$PATH:/usr/local/mongodb/bin' ~/.bash_profile
source ~/.bash_profile
groupadd mongodb
useradd -g mongodb mongodb
cat > /usr/lib/systemd/system/mongod_multiple_config@.service << EOF
[Unit]
Description=MongoDB Database Server
Documentation=https://docs.mongodb.org/manual
After=network-online.target
Wants=network-online.target
[Service]
User=mongodb
Group=mongodb
#EnvironmentFile=-$basedir/etc/default/mongod
ExecStart=$basedir/bin/mongod --config ${dataroot}/mongodb/conf/mongo_config.yml
ExecStop=$basedir/bin/mongod --config ${dataroot}/mongodb/conf/mongo_config.yml --shutdown
PIDFile=$datadir/%i/mongo_%i.pid
# file size
LimitFSIZE=infinity
# cpu time
LimitCPU=infinity
# virtual memory size
LimitAS=infinity
# open files
LimitNOFILE=64000
# processes/threads
LimitNPROC=64000
# locked memory
LimitMEMLOCK=infinity
# total threads (user+kernel)
TasksMax=infinity
TasksAccounting=false
# Recommended limits for mongod as specified in
# https://docs.mongodb.com/manual/reference/ulimit/#recommended-ulimit-settings

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
    if [ ! -f $basedir/conf/mongo_config.yml ]; then
    touch ${dataroot}/mongodb/conf/mongo_config.yml
    fi
    cat > ${dataroot}/mongodb/conf/mongo_config.yml << EOF
systemLog:
  destination: file
#注意修改路径
#Note the modification path
  path: "$logdir/mongo_config.log"
  logAppend: true
storage:
  journal:
    enabled: true
#注意修改路径
#Note the modification path
  dbPath: "$datadir/config"
  engine: wiredTiger
  wiredTiger:
    engineConfig:
         cacheSizeGB: 1
processManagement:
  fork: false
net:
  bindIp: 0.0.0.0
#注意修改端口
#Notice Modifying the port
  port: 27017
setParameter:
  enableLocalhostAuthBypass: true
replication:
#复制集名称
#Replication set name
  replSetName: "rscnf"
sharding:
#作为配置服务
#As configuration service
  clusterRole: configsvr
#security:
#  keyFile: "/data/mongodb/conf/keyFile"
#  authorization: enabled
EOF
sed -i "s|`grep cacheSizeGB ${dataroot}/mongodb/conf/mongo_config.yml|sed 's/^[ \t]*//g'`|cacheSizeGB: "$(echo `free -m|grep Mem|awk -F' ' '{print $4}'`*0.85/1000|bc|cut -d'.' -f1)"|g"  ${dataroot}/mongodb/conf/mongo_config.yml

    chown -R mongodb:mongodb $dataroot/mongodb
    chown -R mongodb:mongodb $basedir
    cd $basedir
    rpath=`pwd -P`
    chown -R mongodb:mongodb $rpath
    systemctl restart mongod_multiple_config@1.service
    systemctl enable mongod_multiple_config@1.service
