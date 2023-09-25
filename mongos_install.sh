#!/bin/bash
# config install
# /data/mongodb /{data,logs,conf}

dataroot=$1
ver=$2
setip='0.0.0.0'
addcmd(){
addText=$1
file=$2
#判断 file.sh 文件中是否存在该字符串  # Check whether the character string exists in the file.sh file
if ! grep "$addText" $file  >/dev/null
then
#不存在，添加字符串  # Does not exist, add a string
   echo $addText >> $file
else
#存在，不做处理 # Exist, do not process
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
mkdir ${dataroot}/mongodb/conf

addcmd 'export PATH=$PATH:/usr/local/mongodb/bin' ~/.bash_profile
source ~/.bash_profile
groupadd mongodb
useradd -g mongodb mongodb
cat > /usr/lib/systemd/system/mongod_multiple_servers@.service << EOF
[Unit]
Description=MongoDB Database Server
Documentation=https://docs.mongodb.org/manual
After=network-online.target
Wants=network-online.target
[Service]
User=mongodb
Group=mongodb
#EnvironmentFile=-$basedir/etc/default/mongod
ExecStart=$basedir/bin/mongos --config ${dataroot}/mongodb/conf/mongo_route.yml
ExecStop=$basedir/bin/mongos --config ${dataroot}/mongodb/conf/mongo_route.yml --shutdown
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
    if [ ! -f $basedir/conf/mongo_route.yml ]; then
    touch ${dataroot}/mongodb/conf/mongo_route.yml
    fi
    cat > ${dataroot}/mongodb/conf/mongo_route.yml << EOF
systemLog:
  destination: file
#  注意修改路径  # Note the modification path
  path: "/data/mongodb/logs/mongo_route.log"
  logAppend: true
processManagement:
  fork: false
net:
  bindIp: 0.0.0.0
#  注意修改端口 # Notice Modifying the port
  port: 30000
setParameter:
  enableLocalhostAuthBypass: true
replication:
  localPingThresholdMs: 15
sharding:
#  关联配置服务  # Associated configuration service
  configDB: rscnf/172.21.231.246:27017,172.21.231.247:27017,172.21.231.248:27017
#security:
#  keyFile: "/data/mongodb/conf/keyFile"
EOF

cat >  /root/.mongorc.js << EOF
//host=db.serverStatus().host;
host=\``hostname`\`
cmdCount=1;
prompt=function(){
return db+"@"+host+" "+(cmdCount++) +">";
}

function showDate(){

var today = new Date();
var year = today.getFullYear() + "年";
var month = (today.getMonth() +1) + "月";
var date = today.getDate() + "日";
var week = '星期' + today.getDay();
var quarter = "一年中的第" + Math.floor((today.getMonth() +3) / 3) + "个季度";

var text = "[ 欢迎回来,今天是" + year + month + date  + week +"," + quarter + "。]";
print(text);

}

showDate();
EOF

    chown -R mongodb:mongodb $dataroot/mongodb
    chown -R mongodb:mongodb $basedir
    cd $basedir
    rpath=`pwd -P`
    chown -R mongodb:mongodb $rpath
    systemctl restart mongod_multiple_servers@1.service
    systemctl enable mongod_multiple_servers@1.service
