#!/bin/bash

without=$(python  cluster_mongodb_mutil.py 'argument') #获取IP地址和密码
ips=$(echo $without|cut -d'|' -f1|cut -d':' -f2)
sshpassword=$(echo $without|cut -d'|' -f2|cut -d':' -f2)
sshuser='root'

/usr/bin/which sshpass ;if [[ "$?" != "0" ]];then  yum -y install sshpass ;fi

operation=1 # 1检查机器资源配置 0删除mongodb集群(生产环境禁止使用)
	
function mongo_clear(){

   IFS='|' read -ra elements <<< "$1"

   for ip in "${elements[@]}"; do
     pid=$(sshpass -p $2  ssh  $3@${ip} -o StrictHostKeyChecking=no "ps -ef|grep mongo|grep -vE 'grep'|awk -F' ' '{print \$2}'")
     if [ -n "$pid" ]; then
        sshpass -p $2  ssh  $3@${ip} -o StrictHostKeyChecking=no "kill -9 $pid"
     fi
     echo $ip
     sshpass -p $2   ssh  $3@${ip} -o StrictHostKeyChecking=no "userdel mongodb"
     sshpass -p $2  ssh  $3@${ip} -o StrictHostKeyChecking=no "rm -fr  /data/*"
     sshpass -p $2  ssh  $3@${ip} -o StrictHostKeyChecking=no "cd /usr/local/ && unlink mongodb"
     sshpass -p $2  ssh  $3@${ip} -o StrictHostKeyChecking=no "rm -fr /opt/mongodb-linux-x86_64-rhel70-4.4.18"
    done
}	

function mongo_check(){
   IFS='|' read -ra elements <<< "$1"
   for ip in "${elements[@]}"; do
     {
       cpu=$(sshpass -p $2  ssh  $3@${ip} -o StrictHostKeyChecking=no "cat /proc/cpuinfo | grep 'process'|wc -l")
       sshpass -p $2   ssh  $3@${ip} -o StrictHostKeyChecking=no "df -h|grep data"
       fre=$(sshpass -p $2  ssh  $3@${ip} -o StrictHostKeyChecking=no "free -m|sed -n 2p|awk -F' ' '{print \$2}'")
       dik=$(sshpass -p $2  ssh  $3@${ip} -o StrictHostKeyChecking=no "df -h|awk -F' ' '{print \$2}' |grep G|cut -d'G' -f1|awk '{if(NR == 1) {max = \$1} else {if(\$1 > max) {max = \$1}}} END {print max}'")
       dik_free=$(sshpass -p $2  ssh  $3@${ip} -o StrictHostKeyChecking=no "df -h|grep ${dik}|awk -F' ' '{print \$4}'")
       echo ${ip}': '${cpu}'c,'${fre}m,${dik}g,'磁盘可用'$dik_free
     } &
  done
  wait
}

ipss=`echo $ips|sed 's/ /|/g'`

if [ "$operation" == 0 ];then
   mongo_clear ${ipss} ${sshpassword} ${sshuser}
elif [ "$operation" == 1 ];then
   mongo_check $ipss $sshpassword $sshuser
fi
