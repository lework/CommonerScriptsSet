#!/bin/bash

systemctl stop kube-scheduler
systemctl stop kube-controller-manager
systemctl stop kubelet
systemctl stop etcd
systemctl stop docker
systemctl status kube-apisever
rm -rf /var/lib/kubelet
rm -rf /var/log/kubernetes
rm -rf /etc/kubernetes
rm -rf /var/lib/kube-proxy
rm -rf /var/lib/etcd
rm -rf /etc/etcd
rm -rf /etc/docker
rm -rf /root/.kube
rm -rf /var/lib/docker
rm -rf /etc/cni/net.d
rm -rf /etc/systemd/system/kube-*
rm -rf /etc/systemd/system/etcd.service
rm -rf /etc/systemd/system/docker.service
