
#!/bin/bash

# /data/mongodb /{data,logs,conf}

dataroot=$1
ver=$2
shardid=$3
setip='0.0.0.0'
if [ $# -ne 3 ];then
    echo "Error: please use $0 dataroot ver shardid"
    exit 1
fi
addcmd(){
addText=$1
file=$2
#判断 file.sh 文件中是否存在该字符串 # Check whether the character string exists in the file.sh file
if ! grep "$addText" $file  >/dev/null
then
#不存在，添加字符串 # Does not exist, add a string
   echo $addText >> $file
else
#存在，不做处理
   echo $addText" exist in "$file
fi
}
# shardno3rd=`expr $shardid \* 3`
#shardno1st=`expr $shardno3rd - 2`
shardno1st=$shardid
#wget mongodb-linux-x86_64-rhel70-4.4.18.tgz
tar xzvf mongodb-linux-x86_64-rhel70-$ver.tgz -C /opt
ln -snf /opt/mongodb-linux-x86_64-rhel70-$ver /usr/local/mongodb
basedir='/usr/local/mongodb'
datadir=$dataroot'/mongodb/data'
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
ExecStart=$basedir/bin/mongod --config ${dataroot}/mongodb/conf/mongo_shard%i.yml
ExecStop=$basedir/bin/mongod --config ${dataroot}/mongodb/conf/mongo_shard%i.yml --shutdown
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
j=$shardno1st
for ((i=1; i<=j; i++))
do
    mkdir -p $datadir/shard$i
    if [ ! -f $basedir/conf/mongo_shard$i.yml ]; then
    touch ${dataroot}/mongodb/conf/mongo_shard$i.yml
    fi
    port=`expr $i + 40000`
    cat > ${dataroot}/mongodb/conf/mongo_shard$i.yml << EOF
systemLog:
  destination: file
  path: "$logdir/mongo_shard$i.log"
  logAppend: true
  logRotate: rename
storage:
  journal:
    enabled: true
    commitIntervalMs: 162
  dbPath: "$datadir/shard$i"
  syncPeriodSecs: 67
  engine: wiredTiger
  wiredTiger:
    engineConfig:
         cacheSizeGB: 6
processManagement:
  fork: false
net:
  bindIp: $setip
  #注意修改端口  # Notice Modifying the port
  port: $port
setParameter:
  enableLocalhostAuthBypass: true
replication:
  #复制集名称 # Replication set name
  replSetName: "rsshd3"
  oplogSizeMB: 24576
sharding:
  #作为分片服务 # As a shard service
  clusterRole: shardsvr
EOF
sed -i "s|`grep cacheSizeGB ${dataroot}/mongodb/conf/mongo_shard$i.yml|sed 's/^[ \t]*//g'`|cacheSizeGB: "$(echo `free -m|grep Mem|awk -F' ' '{print $4}'`*0.85/1000|bc|cut -d'.' -f1)"|g"  ${dataroot}/mongodb/conf/mongo_shard$i.yml

    chown -R mongodb:mongodb $dataroot/mongodb
    chown -R mongodb:mongodb $basedir
    cd $basedir
    rpath=`pwd -P`
    chown -R mongodb:mongodb $rpath
    systemctl restart mongod_multiple_servers@$i.service
    systemctl enable mongod_multiple_servers@$i.service
done

