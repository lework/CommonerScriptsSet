# ceph 巡检


> all.yml  # 巡检代码入口  
> filter_plugins # 数据处理插件


### 执行巡检
- ansible-playbook -i /etc/ansible/hosts/00-nodes all.yml

### 执行后返回结果

```json

"ceph": {
            "info": "pg load is not balanced; because Small and 150 or greater than 300", 
            "meta": {
                "cluster_health": {
                    "info": "ceph cluster OK", 
                    "meta": "HEALTH_OK", 
                    "status": "OK"
                }, 
                "osd_blance": {
                    "info": "osd load balancing is normal", 
                    "meta": "hdd:0.90 0.77 0.95 0.80 0.86 0.78 0.81 0.96", 
                    "status": "OK"
                }, 
                "osd_pg_balance": {
                    "info": "pg load is not balanced; because Small and 150 or greater than 300", 
                    "meta": "176 160 175 172 90 99 90 101 178 168 184 174 88", 
                    "status": "WARNNING"
                }, 
                "osd_status": {
                    "info": "osd status is normal", 
                    "meta": "[]", 
                    "status": "OK"
                }, 
                "osd_used_rate": {
                    "info": "osd used rate is normal", 
                    "meta": "0.90 0.77 0.95 0.80 0.11 0.11 0.11 0.11 0.86 0.78", 
                    "status": "OK"
                }
            }, 
            "status": "WARNNING"
        }
    }
```


### 数据格式解释

```json

"ceph": {
		    "status":  " " # 如果巡检是OK，则不往meta里取信息；如果巡检是WARNNING，则往meta取每个巡检值
            "info": " ",  # 如果巡检是正确或者错误地信息
            "meta": {
                "cluster_health": {   # 巡检的一个实例
                    "info": "ceph cluster OK",   # 巡检后实例状态的描述
                    "meta": "HEALTH_OK",  # 巡检获取的源信息
                    "status": "OK"  # 巡检后这个实例的状态
                }，
            }
        }
```



