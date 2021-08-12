# 基线漏洞安全整改

> 修复环境：centos7及以上

#### 修复基线漏洞名称 
- 口令锁定策略
- 登陆超时时间设置
- 限制root用户SSH远程登录
- 使用SSH协议进行远程维护
- 文件与目录缺省权限控制
- 账号文件权限设置
- 口令生存期
- 禁止UID为0的用户存在多个
- 口令复杂度
- root用户环境变量的安全性
- 限制root用户TELNET远程登录
- 启用远程日志功能
- 修改SSH的Banner信息
- 删除无关帐号
- 配置用户最小授权
- 记录安全事件日志
- 设置账户组
- 修改SSH的Banner警告信息
- 禁止IP路由转发
- 控制远程访问的IP地址
- 禁止存在空密码的帐户
- 禁止ICMP重定向
- 关闭不必要启动项
- 记录帐户登录日志
- 日志文件安全
- 口令重复次数限制
- 禁止root用户登录FTP
- 配置su命令使用情况记录
- 限制FTP用户登录后能访问的目录
- 使用PAM认证模块禁止wheel组之外的用户su为root
- 修改TELNET的Banner信息
- 禁止IP源路由
- 历史命令设置 
- 对root为ls、rm设置别名
- 修改目标主机SSH服务存在RC4、CBC或None弱加密算法
- 检查别名文件/etc/aliase（或/etc/mail/aliases）配置

#### 修复步骤

```
1、vim roles/security/defaults/main.yml(修改变量,按照实际需求修改)
# allow host login
hosts_allow: {ssh: ['1.*.*.*']}

# admin user password
admin_password: "123456"

# root login
permit_root_login: "no"

# host deny
hosts_deny: {ssh: {'192.168.1.*'}}

# ssh timeout
ssh_timeout: "90"

# ip version
ip_version: "4"

# Centralized log collect
remote_log_ip: ""

2、执行修复
ansible-playbook -i hosts config.yml

```
