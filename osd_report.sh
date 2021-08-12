

#!/bin/bash

set -e

OSD_LIST=$(docker exec ceph_mon ceph osd tree | awk '/down/{print $4}')
CLUSTER_STATUS=$(docker exec ceph_mon ceph health)
OSD_TEXT=$(pwd)/osdinfo.text

> ${OSD_TEXT}

if [[ ${OSD_LIST} == '' ]];then
  echo "Ceph Cluster: ${CLUSTER_STATUS}"
  exit 0
fi


echo -e "
osd report
----------
  ####   ####  #####     #####  ###### #####   ####  #####  ##### 
#    # #      #    #    #    # #      #    # #    # #    #   #   
#    #  ####  #    #    #    # #####  #    # #    # #    #   #   
#    #      # #    #    #####  #      #####  #    # #####    #   
#    # #    # #    #    #   #  #      #      #    # #   #    #   
 ####   ####  #####     #    # ###### #       ####  #    #   #  

" >> ${OSD_TEXT}




# 获取osd error log
function get_osd_error_log(){

	osd_log_path="/var/lib/docker/volumes/kolla_logs/_data/ceph/ceph-osd.$1.log"
	error_log=$(ssh $2 "grep -inE $(date '+%Y-%m') ${osd_log_path} | grep -E 'Input/output error|error' | tail -n 20")
	dmesg_log=$(ssh $2 "LANG=en_US.UTF-8 && dmesg -T | grep -inE $(date +%b) | grep -E $3 | tail -n 20")

}

# 获取osd目标主机信息、磁盘信息
function get_target_osd_host_info(){

	product_name=$(ssh $2 "cat /sys/devices/virtual/dmi/id/product_name")
	serial_number=$(ssh $2 "cat /sys/devices/virtual/dmi/id/board_serial")
	disk_serial_number=$(ssh $2 "lsblk $1 -t -o SERIAL -P -s | cut -d'\"' -f2")
	unique_identifier=$(ssh $2 "lsblk $1 -t -o WWN -P -s | cut -d'\"' -f2")
	host_ip=$(ssh $2 " hostname -i")
}

# 获取osd的属性
function osd_metadata(){

	for osd in ${OSD_LIST};
	do
		osd_md=$(docker exec ceph_mon ceph osd metadata ${osd})
		osd_device=$(echo ${osd_md} | python -m json.tool | awk -F'\"' '/devices/{print $4}')
		osd_objectstore=$(echo ${osd_md} | python -m json.tool | awk -F'\"' '/osd_objectstore/{print $4}')
		osd_hostname=$(echo ${osd_md} | python -m json.tool | awk -F'\"' '/hostname/{print $4}')
		osd_id=$(echo $osd | cut -d'.' -f2)
		get_target_osd_host_info /dev/${osd_device} ${osd_hostname}
		get_osd_error_log ${osd_id} ${osd_hostname} ${osd_device}
		info >> ${OSD_TEXT}
	done
}

# 打印osd日志、设备、节点信息
function info(){
	echo -e "
 Information as of: $(date +"%Y-%m-%d %T")

 IP Addresses.......: ${host_ip}
 Product............: ${product_name}
 Serial Number......: ${serial_number}
 Disk Serial........: ${disk_serial_number}
 Unique Identifier..: ${unique_identifier}
 Osd Name...........: ${osd}
 Device.............: /dev/${osd_device}
 Osd Objectstore....: ${osd_objectstore}
"
	echo -e "
Osd Error Information
---------------------
Log Source: ${osd_log_path}
${error_log:-None}

Log Source: dmesg -T | grep -inE $(export LANG=en_US.UTF-8 && date +%b)
${dmesg_log:-None}
"
}

osd_metadata



