# Setup my clash router #

My network architecture be like:
```
wan1:China Telecomm
       |     wan2: reserved
   +===|======|==========================+
   |   |      |    Mercury SG105pro      |
   |  (1)    (2)    (3)    (4)    (5)    |
   |                 |      |      |     |
   +=================|======|======|=====+
              PhicommN1     |      |
          downsteam wifi router    |
                      Desktop computer
```


# Setup switch (Mercury SG105pro)

This switch support 802.1Q vpn, here is my settings:

|  Port           | 1 | 2 | 3 | 4 | 5 |
|-----------------|---|---|---|---|---|
|  vlan1(default) | u | u | u | u | u |
|  vlan2(wan)     | u | u | u | - | - |
|  vlan3(lan)     | - | - | u | u | u |
|  pvid           | 2 | 2 | 1 | 3 | 3 |
|  connections    | wan | wan | armbian | client | client |

- t: tagged
- u: untagged
- -: not member of this vlan

ref: [2 settings on vlan: tagged or untagged and PVID](https://www.dell.com/community/Networking-General/Confused-about-PVID/m-p/2523824/highlight/true#M8746)

According the the above link, vlan across tag aware device like switches
use tags to descide they should comminucate or not, while most computers
cannot deal with tags. In my case, port 3-5 are connect to computers, 
thus should be untagged; port 1 connect to upstream router, can be tagged, 
but the upstream should also set to the same tag of this port on SG105pro,
for convinence, I set it untagged.

Now a client computer, say from port 4, sent a packet. The switch
broadcast it to the vlan with same id of it's pvid(3), Port 3-5 are of
vlan 3, then they can receive the packet; while port 1-2 cannot. Same
condition as port 1 send packets. If port 3 sent a packet, the switch
broadcast it to vlan 1(same as port2's pvid), then port 1-5 can receive
the packet. Thus implemented vlan seperation, and make port 3 a "trunk" port.

## Pitfalls on configuring SG105pro
1. Do not remove working port from default vlan.
2. Do not alt working port from untagged to tagged.

The above `working port` means the port your manage client is connecting
to. If you do the above, you will not be able to connect to the manage
site(http://192.168.0.1) after apply the setting, plug and unplug wire
does not work. The mis-setting will not be saved, because you are
disconnected and don't have a chance to click the save button. Thus the
only thing you can do is power off and on SG105pro, to have the old
setting will bring up.

# Install armbian and docker(Phicomm N1)

There are a lot of instructions, pick one fit you needs.

Here are some ref links:

- [docker 中运行 openwrt](https://github.com/lisaac/openwrt-in-docker)
- another[docker 运行 openwrt](https://github.com/luoqeng/OpenWrt-on-Docker)
- [Use macvlan networks](https://docs.docker.com/network/macvlan/)
- [斐讯N1 – 完美刷机Armbian教程](https://yuerblog.cc/2019/10/23/%e6%96%90%e8%ae%afn1-%e5%ae%8c%e7%be%8e%e5%88%b7%e6%9c%baarmbian%e6%95%99%e7%a8%8b/)
- [N1刷Armbian系统并在Docker中安装OpenWrt旁路由的详细教程](https://www.right.com.cn/forum/thread-1347921-1-1.html)
- [N1盒子做旁路由刷OpenWRT系统（小白专用）](https://www.cnblogs.com/neobuddy/p/n1-setup.html)
- [Docker上运行Lean大源码编译的OpenWRT（初稿）](https://openwrt.club/93.html)
- [engineerlzk 的CSDN博客](https://me.csdn.net/engineerlzk)
- [我在用的armbian版本](https://github.com/kuoruan/Build-Armbian/releases/tag/v5.99-20200408)

## Config docker log

It's recommended to limit docker daemon's log size, or you will soon runout of disk space.
Modify your `/etc/docker/daemon.json` like the following:

```
{
    "registry-mirrors": ["https://docker.mirrors.ustc.edu.cn/"],
        "log-driver": "json-file",
          "log-opts": {"max-size":"100m", "max-file":"3"}
}
```

# Armbian settings

## Upstream ehternet

My upstream ethernet connection is automatic set to dhcp, here is partial of my `/etc/network/interface`:

```
allow-hotplug eth0
no-auto-down eth0
iface eth0 inet dhcp
```

## Remove networkmanager

Networkmanager is not needed, and it automatic delete my static ip
settings, as my nic has both dhcp and static ips, and dhcp server
temporary unavailable.

## Setup vlan

Create a systemd service to bring up macvlan interface each time the system boots.
Refer to `host-service` directory for details.

## TODOS:

- [ ] explain why a vlan is needed, difference between vlan and dual-ips.
- [ ] explain why a script is needed, instead of network configure file.

# Docker dhcpd and clash service settings

- Create dhcpd image as `dhcpd/Dockerfile`
- Create clash image as `clash/Dockerfile`
- Create iptables script `clash/entrypoint.sh` and copy to `./volume/clash/entrypoint.sh`
- Create docker compose config `docker-compose.yml`
- Prepare your clash config `./volume/clash/config.yml`
- Download clash core, Country.mmdb into `./volume/clash/clash-linux`, `./volume/clash/Country.mmdb`

Now run `docker-compose up`, 

## TODOS:
- [ ] Why host network
- [ ] Why dns redirect in iptables not work(connection refused)

## refs

> Host mode networking can be useful to optimize performance, and in situations where a container needs to handle a large range of ports, as it does not require network address translation (NAT), and no “userland-proxy” is created for each port.
>
> The host networking driver only works on Linux hosts, and is not supported on Docker Desktop for Mac, Docker Desktop for Windows, or Docker EE for Windows Server. -- [Docker host document](https://docs.docker.com/network/host/)

# TODO

- [ ] script to update clash profile, clash core, Country.mmdb
- [ ] ipv6
- [ ] wireguard
