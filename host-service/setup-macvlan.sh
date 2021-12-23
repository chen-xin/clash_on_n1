#!/bin/bash

# modify this line to fit your environment
host_nic=eth0
ip link set eth0 promisc on

ip link add link $host_nic dev mac1 type macvlan mode bridge
# ip link add link $host_nic dev mac_lan type macvlan mode bridge

ip addr add 192.168.211.1/24 dev mac1
ip link set mac1 up
