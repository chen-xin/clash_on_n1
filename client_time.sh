#!/bin/bash

# macs="${macs} xiaoxin-air,74:DE:2B:44:2A:79"
macs="${macs} XiaoxinAir,3C:91:80:54:10:7F"
# macs="${macs} kpw4_black,08:A6:BC:60:04:4E kpw4_red,08:84:9D:D3:5E:88 "

# add the following cron job:
# 30 22  * * * /home/xin/projects/docker_clash/client_time.sh disable
# 00 07  * * * /home/xin/projects/docker_clash/client_time.sh enable

action=-A
action_name=disabled

if [ "$1" = "enable" ]; then
    action=-D
    action_name=enabled
fi

for m in $macs; do
    key=${m%,*}
    val=${m#*,}
    echo "${action_name}: [${key}]: [${val}]"
    docker exec docker_clash_clash_1 iptables ${action} INPUT -m mac --mac-source ${val} -j DROP
done


