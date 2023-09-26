#!/usr/bin/bash

sshuser='root'
sshpassword=$5
/usr/bin/which sshpass ;if [[ "$?" != "0" ]];then  yum -y install sshpass ;fi
ips=$4
for ip in $ips
do
    {
         sshpass -p $sshpassword  scp  keyFile  ${sshuser}@${ip}:/data/mongodb/conf/
         sshpass -p $sshpassword  ssh  ${sshuser}@${ip} -o StrictHostKeyChecking=no "chown mongodb.mongodb  /data/mongodb/conf/keyFile"
         sshpass -p $sshpassword  ssh  ${sshuser}@${ip} -o StrictHostKeyChecking=no "sed -i 's/#security/security/g' /data/mongodb/conf/mongo_*.yml;sed -i 's/#  keyFile/  keyFile/g' /data/mongodb/conf/mongo_*.yml;sed -i 's/#  authorization/  authorization/g' /data/mongodb/conf/mongo_*.yml"
          sshpass -p $sshpassword  ssh  ${sshuser}@${ip} -o StrictHostKeyChecking=no "sed -i '/mongod/d' /etc/rc.local;echo '/usr/bin/systemctl start mongod_multiple_servers@1.service'>>/etc/rc.local;chmod +x /etc/rc.local"

    } &
done
wait


#重启sharding节点机器
ips=$3
for ip in $ips
do
  {
    sshpass -p $sshpassword ssh ${sshuser}@${ip} -o StrictHostKeyChecking=no "reboot"
  } &
done
wait

sleep 300

#重启元数据节点
ips=$2
for ip in $ips
do
  {
    sshpass -p $sshpassword ssh ${sshuser}@${ip} -o StrictHostKeyChecking=no "reboot"
  } &
done
wait
sleep 300
#重启mongos节点
ips=$1
for ip in $ips
do
 {
   sshpass -p $sshpassword ssh ${sshuser}@${ip} -o StrictHostKeyChecking=no "reboot"
 } &
done
wait
