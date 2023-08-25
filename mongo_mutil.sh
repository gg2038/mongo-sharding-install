#!/bin/bash


shardid=1
vers='4.4.18'
dataroot='/data'
passw='xxxxx'


if [ "$2" == 1 ];then # mongod
  ips=$1
  for ip in $ips
  do
     {
      ipp=$(ip a|grep  'inet 172'|awk -F' ' '{print $2}'|cut -d'/' -f1)
      if [ "$ipp" == "$ip" ];then
         sh  mongodb_install.sh ${dataroot} ${vers} ${shardid}
      elif [ "$ipp" != "$ip" ];then
         shardnamen='rsshd'$3
         shardnamey=$(grep replSetName mongodb_install.sh|cut -d':' -f2|grep -Po '(?<=\").*?(?=\")'|tail -n1)
         sed -i "s|$shardnamey|$shardnamen|g" mongodb_install.sh
         sshpass -p ${passw}  ssh  root@${ip} -o StrictHostKeyChecking=no "if [ ! -d ${dataroot} ];then  mkdir ${dataroot};fi"
         sshpass -p ${passw} scp mongodb_install.sh mongodb-linux-x86_64-rhel70-${vers}.tgz  root@${ip}:${dataroot}
         sshpass -p ${passw}  ssh  root@${ip} -o StrictHostKeyChecking=no "cd ${dataroot}/;sh  mongodb_install.sh ${dataroot} ${vers} ${shardid}"
      fi
 echo 'install mongod ......'
     } &
 done
 wait

elif [ "$2" == 2 ];then # config
  ips=$1
  for ip in $ips
  do
    {
    ipp=$(ip a|grep  'inet 172'|awk -F' ' '{print $2}'|cut -d'/' -f1)
    if [ "$ipp" == "$ip" ];then
       sh config_install.sh ${dataroot} ${vers}
    elif [ "$ipp" != "$ip" ];then
      sshpass -p ${passw}  ssh  root@${ip} -o StrictHostKeyChecking=no "if [ ! -d ${dataroot} ];then  mkdir ${dataroot};fi"
      sshpass -p ${passw} scp config_install.sh mongodb-linux-x86_64-rhel70-${vers}.tgz  root@${ip}:${dataroot}
      sshpass -p ${passw}  ssh  root@${ip} -o StrictHostKeyChecking=no "cd ${dataroot}/;sh  config_install.sh ${dataroot} ${vers}"
    fi
  echo 'install config ......'
    } &
  done
  wait
 
elif [ "$2" == 3 ];then # mongos
  ips=$1
  for ip in $ips
  do
    {
    ipp=$(ip a|grep  'inet 172'|awk -F' ' '{print $2}'|cut -d'/' -f1)
    if [ "$ipp" == "$ip" ];then
       sh mongos_install.sh ${dataroot} ${vers}
    elif [ "$ipp" != "$ip" ];then
      sshpass -p ${passw}  ssh  root@${ip} -o StrictHostKeyChecking=no "if [ ! -d ${dataroot} ];then  mkdir ${dataroot};fi"
      sshpass -p ${passw} scp mongos_install.sh mongodb-linux-x86_64-rhel70-${vers}.tgz  root@${ip}:${dataroot}
      sshpass -p ${passw}  ssh  root@${ip} -o StrictHostKeyChecking=no "cd ${dataroot}/;sh mongos_install.sh ${dataroot} ${vers}"
    fi
  echo 'install mongos ......'
    } &
  done
  wait
fi
