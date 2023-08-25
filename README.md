# MongoDB_cluster_install
### HGR_HLN_HJQ ###

1.1 集群所有机器配置 检查脚本 check_host.sh
1.1 Configuration check script for all machines in the cluster

1.2 集群所有机器OS层的优化脚本　dbenvset_mult.sh
1.2 Optimize scripts for all machine OS layers in the cluster


1.3 MongoDB集群部署脚本 cluster_mongodb_mutil.py
1.3 MongoDB cluster deployment script

 例子：
example:
mongos: 172.21.14.157 172.21.14.158 172.21.14.159
config: 172.21.14.160 172.21.14.161 172.21.14.162

shard1: 172.21.14.163 172.21.14.164 172.21.14.165
shard2: 172.21.14.166 172.21.14.167 172.21.14.168
shard3: 172.21.14.169 172.21.14.170 172.21.14.171

#把cluster_mongodb_mutil.py脚本中的 iplist_s变量修改成mongs的IP
                          把脚本 中的iplist_c变量修改成config的IP
                          把脚本中的iplist变量修改成shard的IP
                         　注意IP以空格分隔，分片列表中每个子列表代表一个分片的副本集IP
#Change the iplist_s variable in the cluster_mongodb_mutil.py script to the IP of the mongs
                          Change the iplist_c variable in the script to the IP of config
                          Change the iplist variable in the script to the IP of the shard
                          Note IP addresses are separated by Spaces. Each sub-list in the fragment list represents the IP address of a fragment's replica set

["172.21.14.157 172.21.14.158 172.21.14.159"]
["172.21.14.160 172.21.14.161 172.21.14.162"]
["172.21.14.163 172.21.14.164 172.21.14.165"]["172.21.14.166 172.21.14.167 172.21.14.168"]["172.21.14.169 172.21.14.170 172.21.14.171"]

#脚本执行和调用顺序
#注:脚本中已经定义了mongod,config,mongos端口/安装目录/cacheSizeGB(脚本根据机器内存0.85设置)/副本集从节点数，如需修改可根据实际情况修改。
# Script execution and invocation order
Note: The mongod,config,mongos port/installation directory /cacheSizeGB(set according to the memory 0.85)/ number of secondary nodes in the replica set has been defined in the script. You can change the value based on site requirements.

                                              | 1.1 mongodb_install.sh
cluster_mongodb_mutil.py --> mongo_mutil.sh-->| 1.2 config_install.sh
                                              | 1.3 mongos_install.sh


1.5 运行安装脚本,等待脚本运行完提示安装完成。
1.5 Run the installation script and wait until the script is complete.

#python cluster_mongodb_mutil.py

#脚本运行完后会把集群的信息写入config库的集合mongodb_configs中
#When the script is finished, the cluster information is written to the mongodb_configs collection in the config library

config@host-172-21-14-157:30000 5>db.mongodb_configs.find()
[172.21.14.157 172.21.14.158 172.21.14.159][172.21.14.160 172.21.14.161 172.21.14.162][172.21.14.163 172.21.14.164 172.21.14.165][172.21.14.166 172.21.14.167 172.21.14.168][172.21.14.169 172.21.14.170 172.21.14.171]

1.6 脚本mongodb_shard_join.py 是用python连接MongoDB集群 写入数据，方便验证集群地址中一个地址下线后不影响集群使用.
1.6 The script mongodb_shard_join.py connects to the MongoDB cluster using python to write data to facilitate the verification that the cluster usage will not be affected if an address in the cluster goes offline.
