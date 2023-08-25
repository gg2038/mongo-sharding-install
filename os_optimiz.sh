#!/bin/sh
addcmd(){
addText=$1
file=$2
#判断 file.sh 文件中是否存在该字符串
# Check whether the character string exists in the file.sh file
if ! grep -q "$addText" $file 
then
#不存在，添加字符串
#Does not exist, add a string
   echo "$addText" >> $file
else
#存在，不做处理
#Exist, do not process
   echo "$addText"" exist in "$file
fi
}

if [ $# -ne 3 ];then
    echo "Error: please use $0 datadir ishdd ispm"
fi
datadir=$1  #数据目录，当前规范/data # data directory, current specification /data
ishdd=$2    #机械硬盘为1，ssd为0  #The value of mechanical hard disk is 1, and the value of ssd is 0
ispm=$3     #物理机1，虚机0，容器2  # Physical machine 1, virtual machine 0, container 2
#source /etc/profile

if [ $ispm -ne 2 ];then
   systemctl stop tuned
   systemctl disable tuned
fi
if [ $ispm -eq 1 ];then
   systemctl enable cpupower.service
   systemctl restart cpupower.service
fi
yum install -y libaio wget telnet net-tools strace gdb lsof sysstat bc numactl grubby ntp traceroute s3cmd zstd jq
sudo systemctl stop firewalld.service
sudo systemctl disable firewalld.service
if [ $ispm -ne 2 ];then
   if [ $ishdd -eq 1 ];then
      #机械盘 # Mechanical disc
      #数据盘禁用atime  # Disable atime for data disks
      awk '$2=="'$datadir'"{$4="defaults,noatime"}1' /etc/fstab > tmp && mv tmp /etc/fstab -f
      mount -o remount,noatime $datadir
      #内核设置存储介质的 I/O 调度器  # The kernel sets up the I/O scheduler for the storage media
      grubby --update-kernel=ALL --args="elevator=deadline"
   else
      #ssd
      #数据盘禁用atime,discard for ssd del data  # discard for ssd del data when atime is disabled on a data disk
      awk '$2=="'$datadir'"{$4="defaults,noatime,discard"}1' /etc/fstab > tmp && mv tmp /etc/fstab -f
      mount -o remount,noatime,discard $datadir
      grubby --update-kernel=ALL --args="elevator=noop"
   fi
fi   
#设置当前不限制输出corefile，打开文件数，用户打开线程数 # Set the current unrestricted output corefile, the number of open files, and the number of threads opened by the user
ulimit -c unlimited
ulimit -n 1048576
ulimit -u 1024000
#设置不限制输出corefile，打开文件数，用户打开线程数永久生效  #The setting does not limit the output corefile, the number of open files, and the number of user open threads permanently take effect
addcmd '*  soft  core  unlimited' /etc/security/limits.conf
addcmd '*  hard  core  unlimited' /etc/security/limits.conf
addcmd '*  soft  nofile   1048576' /etc/security/limits.conf
addcmd '*  hard  nofile   1048576' /etc/security/limits.conf
addcmd '*  soft  nproc   1024000' /etc/security/limits.conf
addcmd '*  hard  nproc   1024000' /etc/security/limits.conf
addcmd '*  soft  stack   32768' /etc/security/limits.conf
addcmd '*  hard  stack   32768' /etc/security/limits.conf
#修改当前的内核配置立即关闭透明大页 # Modify the current kernel configuration to close transparent large pages immediately
echo never > /sys/kernel/mm/transparent_hugepage/enabled
echo never > /sys/kernel/mm/transparent_hugepage/defrag
#内核关闭透明大页 # Kernel closes transparent large page
grubby --args="transparent_hugepage=never" --update-kernel `grubby --default-kernel`
#设置操作系统预读扇区readahead（主要为了优化mongodb），/为数据盘目录，预读64个扇区为32k(网上资料说mongodb针对32k预读有优化，暂未从官方文档查实)，对应随机读多的应用较小预读可以提升性能。
# Set the readahead for the OS sector (mainly to optimize mongodb), / for the data disk directory, and set the readahead for the 64 sectors to 32k. (According to the online information, mongodb is optimized for 32k read-ahead, but it is not verified from the official documents.) The read-ahead can improve performance for applications with multiple random reads.
blockdev --setra 64 `df | grep -w $datadir | awk '{print $1}'`

cat > /etc/systemd/system.conf << EOF
#  This file is part of systemd.
#
#  systemd is free software; you can redistribute it and/or modify it
#  under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation; either version 2.1 of the License, or
#  (at your option) any later version.
#
# Entries in this file show the compile time defaults.
# You can change settings by editing this file.
# Defaults can be restored by simply deleting this file.
#
# See systemd-system.conf(5) for details.

[Manager]
#LogLevel=info
#LogTarget=journal-or-kmsg
#LogColor=yes
#LogLocation=no
DumpCore=yes
#CrashShell=no
#ShowStatus=yes
#CrashChVT=1
#CtrlAltDelBurstAction=reboot-force
#CPUAffinity=1 2
#JoinControllers=cpu,cpuacct net_cls,net_prio
#RuntimeWatchdogSec=0
#ShutdownWatchdogSec=10min
#CapabilityBoundingSet=
#SystemCallArchitectures=
#TimerSlackNSec=
#DefaultTimerAccuracySec=1min
#DefaultStandardOutput=journal
#DefaultStandardError=inherit
#DefaultTimeoutStartSec=90s
#DefaultTimeoutStopSec=90s
#DefaultRestartSec=100ms
#DefaultStartLimitInterval=10s
#DefaultStartLimitBurst=5
#DefaultEnvironment=
#DefaultCPUAccounting=no
#DefaultBlockIOAccounting=no
#DefaultMemoryAccounting=no
#DefaultTasksAccounting=no
#DefaultTasksMax=
#DefaultLimitCPU=
#DefaultLimitFSIZE=
#DefaultLimitDATA=
#DefaultLimitSTACK=
#DefaultLimitCORE=
#DefaultLimitRSS=
DefaultLimitNOFILE=1048576
#DefaultLimitAS=
DefaultLimitNPROC=1024000
#DefaultLimitMEMLOCK=
#DefaultLimitLOCKS=
#DefaultLimitSIGPENDING=
#DefaultLimitMSGQUEUE=
#DefaultLimitNICE=
#DefaultLimitRTPRIO=
#DefaultLimitRTTIME=
EOF
systemctl daemon-reexec
cat > /etc/sysctl.conf << EOF
# sysctl settings are defined through files in
# /usr/lib/sysctl.d/, /run/sysctl.d/, and /etc/sysctl.d/.
#
# Vendors settings live in /usr/lib/sysctl.d/.
# To override a whole file, create a new file with the same in
# /etc/sysctl.d/ and put new settings there. To override
# only specific settings, add a file with a lexically later
# name in /etc/sysctl.d/ and put new settings there.
#
# For more information, see sysctl.conf(5) and sysctl.d(5).
#表示内核允许分配所有的物理内存，而不管当前的内存状态如何
vm.overcommit_memory = 1
fs.file-max = 6553560
#关闭系统swap
vm.swappiness = 0
#服务端所能accept即处理数据的最大客户端数量，即完成连接上限，默认值是128
net.core.somaxconn=32768
#服务端所能接受SYN同步包的最大客户端数量，即半连接上限，默认值是128
net.core.netdev_max_backlog=16384
#处于SYN_RECV的TCP最大连接数,SYN_RECV状态的TCP连接数超过该值后丢弃后续的SYN报文
net.ipv4.tcp_max_syn_backlog=16384
#表示关闭SYN Cookies。避免不使用SYN半连接队列的情况下成功建立连接
net.ipv4.tcp_syncookies = 0
#为TCP socket预留用于接收缓冲的内存缺省值(以字节为单位)
net.core.rmem_default=262144
#为TCP socket预留用于发送缓冲的内存缺省值(以字节为单位)
net.core.wmem_default=262144
#为TCP socket预留用于接收缓冲的内存最大值
net.core.rmem_max=16777216
#为TCP socket预留用于发送缓冲的内存最大值
net.core.wmem_max=16777216
#表示每个套接字所允许的最大缓冲区的大小
net.core.optmem_max=16777216
#表示用于向外连接的端口范围.缺省情况下过窄:32768到61000,改为1024到65535
net.ipv4.ip_local_port_range=1024 65535
#自动调优所使用的接收缓冲区的值，最少字节数/默认值/最大字节数
net.ipv4.tcp_rmem=1024 4096 16777216
#自动调优所使用的发送缓冲区的值
net.ipv4.tcp_wmem=1024 4096 16777216
#不设0可能大量丢包
#net.ipv4.tcp_tw_recycle = 0
EOF

sysctl -p
swapoff -a

