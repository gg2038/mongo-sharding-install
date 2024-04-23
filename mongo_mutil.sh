#!/bin/bash


#shardid=1
vers='4.4.18'
dataroot='/data'
passw=$3

function  install_shard(){
  IFS='|' read -ra elements <<< "$1"
  for ip in "${elements[@]}"; do
     {
      ipp=$(ping `hostname` -c 1|grep PING|grep -Po '(?<=\().*?(?=\))'|grep -E -o "([0-9]{1,3}[\.]){3}[0-9]{1,3}"|head -n 1)
      if [ "$ipp" == "$ip" ];then
         sh  mongodb_install.sh $2 $3 $4
      elif [ "$ipp" != "$ip" ];then
         shardnamen='rsshd'$4
         shardnamey=$(grep replSetName mongodb_install.sh|cut -d':' -f2|grep -Po '(?<=\").*?(?=\")'|tail -n1)
         sed -i "s|$shardnamey|$shardnamen|g" mongodb_install.sh
         sshpass -p $5  ssh  root@${ip} -o StrictHostKeyChecking=no "if [ ! -d $2 ];then  mkdir $2;fi"
         sshpass -p $5 scp mongodb_install.sh mongodb-linux-x86_64-rhel70-$3.tgz  root@${ip}:$2
         echo '副本集节点传入shards '$4
         sshpass -p $5  ssh  root@${ip} -o StrictHostKeyChecking=no "cd $2;sh  mongodb_install.sh $2 $3 $4"
      fi
 echo 'install mongod ......'
     } &
 done
 wait
}

function  install_config(){
  IFS='|' read -ra elements <<< "$1"
  for ip in "${elements[@]}"; do
    {
    ipp=$(ping `hostname` -c 1|grep PING|grep -Po '(?<=\().*?(?=\))'|grep -E -o "([0-9]{1,3}[\.]){3}[0-9]{1,3}"|head -n 1)
    if [ "$ipp" == "$ip" ];then
       sh config_install.sh $2 $3
    elif [ "$ipp" != "$ip" ];then
      sshpass -p $4  ssh  root@${ip} -o StrictHostKeyChecking=no "if [ ! -d $2 ];then  mkdir $2;fi"
      sshpass -p $4  scp config_install.sh mongodb-linux-x86_64-rhel70-$3.tgz  root@${ip}:$2
      sshpass -p $4  ssh  root@${ip} -o StrictHostKeyChecking=no "cd $2;sh  config_install.sh $2 $3"
    fi
  echo 'install config ......'
    } &
  done
  wait
}

function  install_mongos(){
  IFS='|' read -ra elements <<< "$1"
  for ip in "${elements[@]}"; do
    {
    ipp=$(ping `hostname` -c 1|grep PING|grep -Po '(?<=\().*?(?=\))'|grep -E -o "([0-9]{1,3}[\.]){3}[0-9]{1,3}"|head -n 1)
    if [ "$ipp" == "$ip" ];then
       sh mongos_install.sh $2 $3
    elif [ "$ipp" != "$ip" ];then
      sshpass -p $4  ssh  root@${ip} -o StrictHostKeyChecking=no "if [ ! -d $2 ];then  mkdir $2;fi"
      sshpass -p $4 scp mongos_install.sh mongodb-linux-x86_64-rhel70-${vers}.tgz  root@${ip}:$2
      sshpass -p $4  ssh  root@${ip} -o StrictHostKeyChecking=no "cd $2;sh mongos_install.sh $2 $3"
    fi
  echo 'install mongos ......'
    } &
  done
  wait
}


if [ "$2" == 1 ];then # mongod
  ips=`echo $1|sed 's/ /|/g'`
  rss=$4
  install_shard $ips ${dataroot} ${vers} ${rss} ${passw}
elif [ "$2" == 2 ];then # config
  ips=`echo $1|sed 's/ /|/g'`
  install_config $ips ${dataroot} ${vers} ${passw}

elif [ "$2" == 3 ];then # mongos
  ips=`echo $1|sed 's/ /|/g'`
  install_mongos $ips ${dataroot} ${vers} ${passw}
fi
