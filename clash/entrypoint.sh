#!/bin/sh

proxy_port=7892
clash_dns_port=1053

iptables -t nat -N CLASH
iptables -t nat -F CLASH
# redirect upstream lan
iptables -t nat -A CLASH -p tcp -s 192.168.211.0/24 -d 172.16.0.0/16 -j REDIRECT --to-ports 7892
# Bypass private IP address ranges
iptables -t nat -A CLASH -d 0.0.0.0/8 -j RETURN
iptables -t nat -A CLASH -d 10.0.0.0/8 -j RETURN
iptables -t nat -A CLASH -d 127.0.0.0/8 -j RETURN
iptables -t nat -A CLASH -d 169.254.0.0/16 -j RETURN
iptables -t nat -A CLASH -d 172.16.0.0/12 -j RETURN
iptables -t nat -A CLASH -d 192.168.0.0/16 -j RETURN
iptables -t nat -A CLASH -d 224.0.0.0/4 -j RETURN
iptables -t nat -A CLASH -d 240.0.0.0/4 -j RETURN

# Redirect all TCP traffic to 7892 port, where Clash listens
iptables -t nat -A CLASH -p tcp -j REDIRECT --to-ports 7892
iptables -t nat -A PREROUTING -p tcp -j CLASH

##在nat表中新建一个clash_dns规则链
#iptables -t nat -N CLASH_DNS
##清空clash_dns规则链
#iptables -t nat -F CLASH_DNS
##重定向udp流量到本机1053端口
#iptables -t nat -A CLASH_DNS -p udp -j REDIRECT --to-port $clash_dns_port
##抓取本机产生的53端口流量交给clash_dns规则链处理
#iptables -t nat -I OUTPUT -p udp --dport 53 -j CLASH_DNS
##拦截外部upd的53端口流量交给clash_dns规则链处理
#iptables -t nat -I PREROUTING -p udp --dport 53 -j CLASH_DNS

# iptables -t nat -I clash -p tcp -j LOG --log-prefix \"Clash IPT\"
/clash/clash-linux -d /clash
