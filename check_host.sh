#!/bin/bash

sshuser='root'
sshpassword='xxxx'
ips="172.xx.xx.x04 172.xx.xx.x05 172.xx.xx.x06 172.xx.xx.x07 172.xx.xx.x08 172.xx.xx.x09 172.xx.xx.x10 172.xx.xx.x11 172.xx.xx.x12 172.xx.xx.x13 172.xx.xx.x14 172.xx.xx.x15 172.xx.xx.x16 172.xx.xx.x17 172.xx.xx.x18"
/usr/bin/which sshpass ;if [[ "$?" != "0" ]];then  yum -y install sshpass ;fi

for ip in $ips
do
    {
#      sshpass -p $sshpassword  ssh  ${sshuser}@${ip} -o StrictHostKeyChecking=no "ps -ef|grep mongo;grep rsshd /data/mongodb/conf/mongo_shard1.yml"
      cpu=$(sshpass -p $sshpassword  ssh  ${sshuser}@${ip} -o StrictHostKeyChecking=no "cat /proc/cpuinfo | grep 'process'|wc -l")
      sshpass -p $sshpassword  ssh  ${sshuser}@${ip} -o StrictHostKeyChecking=no "df -h|grep data"
      fre=$(sshpass -p $sshpassword  ssh  ${sshuser}@${ip} -o StrictHostKeyChecking=no "free -m|sed -n 2p|awk -F' ' '{print \$2}'")
      dik=$(sshpass -p $sshpassword  ssh  ${sshuser}@${ip} -o StrictHostKeyChecking=no "df -h|awk -F' ' '{print \$2}' |grep G|cut -d'G' -f1|awk '{if(NR == 1) {max = \$1} else {if(\$1 > max) {max = \$1}}} END {print max}'")
      dik_free=$(sshpass -p $sshpassword  ssh  ${sshuser}@${ip} -o StrictHostKeyChecking=no "df -h|grep ${dik}|awk -F' ' '{print \$4}'")
      echo ${ip}': '${cpu}'c,'${fre}m,${dik}g,'磁盘可用'$dik_free
    } &
done
wait
