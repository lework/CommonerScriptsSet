# kolla-ceph部署

> OS： Centos


#### 项目结构

```
Auto_Ceph
├── 00-hosts 部署的主机
├── README.md
├── action_plugins ansible插件
├── bin 安装kolla-ceph、docker
├── build 镜像构建
├── config 动态变量文件和ceph.conf个性化配置
├── group_vars 默认变量
├── library ansible模块
├── os.yml 主机初始化playbook
├── requirements.txt 
├── roles 部署代码
└── site.yml 部署ceph playbook
```
> 下载Auto_Ceph项目放在/root目录下    
> 3台Centos虚拟机

### 下载ceph镜像
> 部署节点：可以是任意一台mon组节点

1. 在线下载ceph镜像<部署节点操作>
  
  ```
  1. yum -y install wget
  2. wget https://bootstrap.pypa.io/pip/2.7/get-pip.py --no-check-certificate
  3. python get-pip.py
  4.ceph镜像下载安装依赖
     pip install -r /root/Auto_Ceph/requirements.txt --ignore-installed 
  5. 下载docker
      sh /root/Auto_Ceph/bin/install -D
  6. 运行docker
      sh /root/Auto_Ceph/bin/install -I
  7. 下载registry
      sh /root/Auto_Ceph/bin/install -R
  8. 运行registry
  	docker run -d -v /opt/registry:/var/lib/registry -p 5000:5000 --restart=always --name registry registry:latest
  7. 修改配置（2. 修改构建ceph镜像参数）
  8. 开始构建ceph镜像
      cd /root/Auto_Ceph/build/ && sh build.sh --tag nautilus
  9. yum install ansible
  10. 节点之间ssh免密配置
  11. 安装kolla-ceph工具 
      cd /root/Auto_Ceph/bin && sh install -K
  ```
  
2. 在线下载docker<其它节点操作>

```
1. wget https://bootstrap.pypa.io/pip/2.7/get-pip.py --no-check-certificate
2. python get-pip.py
3. 安装docker模块 
    pip install docker
4. 安装docker
    scp /root/Auto_Ceph/bin/install target_host:/root/
    sh /root/install -D &&  sh /root/install -I

```

3. 修改构建ceph镜像参数

```
1. vi /root/Auto_Ceph/build/ceph-build.conf
[DEFAULT]
base = centos
type = binary
regex =
profile = image_ceph

registry = 172.17.2.179:5000
username =
password =
email =

namespace = kolla-ceph
retries = 1
push_threads = 4
maintainer = Kolla Ceph Project
ceph_version = nautilus
ceph_release = 14.2.2 

[profiles]
image_ceph = ceph

```
> 可以按需求设置ceph_version、ceph_release参数下载需要的ceph版本. 

>  根据实际环境配置registry IP和端口.

> 其它默认即可



### 部署节点依赖安装
 



### 部署ceph集群
#### 1. 修改配置
1.1 vi /root/Auto_Ceph/00-hosts 修改主机文件

```
# storage_interface="eth0" ceph集群管理接口，必须配置 
# cluster_interface="eth1" ceph集群数据同步接口，为空默认就是storage_interface
[mon]
172.17.2.179 storage_interface=eth0 cluster_interface=eth1

[mgr]
172.17.2.179

[osd]
172.17.2.179

[mds]
172.17.2.179

[rgw]
172.17.2.179
 
```
 
   
1.2 vi /root/Auto_Ceph/config/globals.yml 修改文件以下参数

```
   ceph_tag: "ceph镜像标签"
   docker_registry: "仓库地址:端口"
   ceph_osd_store_type: "bluestore或者是filestore"
```
   
#### 2. kolla-ceph部署使用
	

##### 2.0. 安装kolla-ceph工具 : cd /root/Auto_Ceph/bin && sh install -K

2.1 初始化ceph主机节点

   * kolla-ceph -i 00-host os
   
2.2 部署前检查配置环境

   * kolla-ceph -i 00-host prechecks
   
2.3 部署ceph集群

   * 磁盘打标签(3. 磁盘打标签)
   * kolla-ceph -i 00-host deploy
   * docker exec ceph_mon ceph -s
   
2.4 删除操作: ceph集群容器和volume

  * kolla-ceph -i 00-host  destroy --yes-i-really-really-mean-it
  
2.5 升级操作

   * 下载ceph镜像
   * 修改最新ceph_tag
   * kolla-ceph -i 00-host upgrade
  
#### 3. 磁盘打标签

##### 3.1. bluestore wal db共用一块盘打标签方式

  *  parted  /dev/vdc  -s  -- mklabel  gpt  mkpart KOLLA_CEPH_OSD_BOOTSTRAP_BS  1 -1
    
##### 3.2. bluestore 分离db和wal打标签方式
>  为了提高 ceph 性能,且ssd磁盘数量有限，通常将db和wal存放在单独的 ssd 磁盘上

  * SSD磁盘：vdb vdd      HDD磁盘：vdc
    * 指定元数据分区 
    
        parted /dev/vdc -s -- mklabel  gpt mkpart KOLLA_CEPH_OSD_BOOTSTRAP_BS_BLUE1 1 100
    * 指定block 分区
    
       parted /dev/vdc -s -- mkpart KOLLA_CEPH_OSD_BOOTSTRAP_BS_BLUE1_B 101 100%
      
    * 指定block.wal分区
    
      parted /dev/vdb -s -- mklabel  gpt mkpart KOLLA_CEPH_OSD_BOOTSTRAP_BS_BLUE1_W 1 1000
    * 指定block.db分区
    
     parted /dev/vdd -s -- mklabel  gpt mkpart KOLLA_CEPH_OSD_BOOTSTRAP_BS_BLUE1_D 1 10000
    
> block.db 分区的大小为 block 分区 的 4%大小

##### 3.3 filestore 打标签方式
  * parted /dev/vdc -s -- mklabel gpt mkpart KOLLA_CEPH_OSD_BOOTSTRAP 1 -1
 
##### 3.4 filestore 指定日志单独分区
> filestore 为了提高 ceph 性能，通常将日志存放在单独的 ssd 磁盘上

* SSD磁盘：vdb    HDD磁盘：vdc vdd 
* vdc 作为数据盘
   * parted /dev/vdc -s -- mklabel gpt mkpart KOLLA_CEPH_OSD_BOOTSTRAP_FILE1 1 -1
* vdd 作为数据盘
   * parted /dev/vdd -s -- mklabel gpt mkpart KOLLA_CEPH_OSD_BOOTSTRAP_FILE2 1 -1
* vdb作为vdc、vdd 的journal盘
   *  parted /dev/vdb -s -- mklabel gpt
   *  parted /dev/vdb -s -- mkpart KOLLA_CEPH_OSD_BOOTSTRAP_FILE1_J 4M 2G
   *  parted /dev/vdb -s -- mkpart KOLLA_CEPH_OSD_BOOTSTRAP_FILE2_J 2G 4G


  
 
 

 



