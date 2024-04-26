# MongoDB_cluster_install
#HGR_HLN_HJQ

#///////////////////////////////////////////

版本迭代信息:
20240426新增功能:主程序python改变IP的输入方法和处理程序，新加检查程序从主程序获取ip串和密码，新加自动自适应获取副本集节点数IP串拼接。

#///////////////////////////////////////////

-  集群所有机器配置 检查脚本 check_host.sh 1.1 Configuration check script for all machines in the cluster

-  集群所有机器OS层的优化脚本　os_optimiz_mult.sh 1.2 Optimize scripts for all machine OS layers in the cluster

-  MongoDB集群部署脚本 cluster_mongodb_mutil.py 1.3 MongoDB cluster deployment script

- **例子： example:** 
1. mongos: 172.xx.xx.157 172.xx.xx.158 172.xx.xx.159
2. config: 172.xx.xx.160 172.xx.xx.161 172.xx.xx.162
3. shard1: 172.xx.xx.163 172.xx.xx.164 172.xx.xx.165 
4. shard2: 172.xx.xx.166 172.xx.xx.167 172.xx.xx.168 
5. shard3: 172.xx.xx.169 172.xx.xx.170 172.xx.xx.171
- 把cluster_mongodb_mutil.py脚本中的 iplist_s变量修改成mongs的IP
把脚本 中的iplist_c变量修改成config的IP
把脚本中的iplist变量修改成shard的IP
　注意IP以空格分隔，分片列表中每个子列表代表一个分片的副本集IP
Change the iplist_s variable in the cluster_mongodb_mutil.py script to the IP of the mongs

    Change the iplist_c variable in the script to the IP of config
                  Change the iplist variable in the script to the IP of the shard
                  Note IP addresses are separated by Spaces. Each sub-list in the fragment list represents the IP address of a fragment's replica set
1. ["172.xx.xx.157 172.xx.xx.158 172.xx.xx.159"] 
2. ["172.xx.xx.160 172.xx.xx.161 172.xx.xx.162"] 
3. ["172.xx.xx.163 172.xx.xx.164 172.xx.xx.165"] 
4. ["172.xx.xx.166 172.xx.xx.167 172.xx.xx.168"] 
5. ["172.xx.xx.169 172.xx.xx.170 172.xx.xx.171"] 
- 脚本执行和调用顺序 注:脚本中已经定义了mongod,config,mongos端口/安装目录/cacheSizeGB(脚本根据机器内存0.85设置)/副本集从节点数，如需修改可根据实际情况修改。 Script execution and invocation order

 Note: The mongod,config,mongos port/installation directory /cacheSizeGB(set according to the memory 0.85)/ number of secondary nodes in the replica set has been defined in the script. You can change the value based on site requirements.

- cluster_mongodb_mutil.py --> mongo_mutil.sh-->{ 1.1 mongodb_install.sh , 1.2 config_install.sh , 1.3 mongos_install.sh } --> cluster_add_security_key.sh

-  运行安装脚本,等待脚本运行完提示安装完成。 1.5 Run the installation script and wait until the script is complete. python cluster_mongodb_mutil.py 脚本运行完后会把集群的信息写入config库的集合mongodb_configs中 When the script is finished, the cluster information is written to the mongodb_configs collection in the config library


- 脚本mongodb_shard_join.py 是用python连接MongoDB集群 写入数据，方便验证集群地址中一个地址下线后不影响集群使用. 1.6 The script mongodb_shard_join.py connects to the MongoDB cluster using python to write data to facilitate the verification that the cluster usage will not be affected if an address in the cluster goes offline.
  ![image](https://github.com/gg2038/mongo-cluster-install/assets/142993593/0dec8d66-a000-4310-b106-9f85025e1309)

  ![image](https://github.com/gg2038/mongo-cluster-install/assets/142993593/1ab0c1c0-286f-4940-b0a6-ec0ca3615491)


-----Author email： hfh203812@gmail.com ----
