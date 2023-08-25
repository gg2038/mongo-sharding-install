#!/bin/bash

sshuser='root'
sshpassword='xxxx'
dataroot='/root'

/usr/bin/which sshpass ;if [[ "$?" != "0" ]];then  yum -y install sshpass ;fi
ips="172.xx.xx.x04 172.xx.xx.x05 172.xx.xx.x06 172.xx.xx.x07 172.xx.xx.x08 172.xx.xx.x09 172.xx.xx.x10 172.xx.xx.x11 172.xx.xx.x12 172.xx.xx.x13 172.xx.xx.x14 172.xx.xx.x15 172.xx.xx.x16 172.xx.xx.x17 172.xx.xx.x18"
for ip in $ips
do
    {
       ipp=$(ip a|grep  'inet 172'|awk -F' ' '{print $2}'|cut -d'/' -f1)
      if [ "$ipp" == "$ip" ];then
          sh os_optimiz.sh /data 0 0
      elif [ "$ipp" != "$ip" ];then
         /usr/bin/sshpass -p ${sshpassword} scp os_optimiz.sh  root@${ip}:${dataroot}
        sshpass -p $sshpassword  ssh  ${sshuser}@${ip} -o StrictHostKeyChecking=no "sh os_optimiz.sh /data 0 0"
     fi
    } &
done
wait
