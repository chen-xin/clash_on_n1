自动更新clash配置文件

功能：
1. read configure from `data/providers.yaml`， merge provider proxies into one clash configure file.
2. sort proxies by rate.
3. create game proxy group

Usage:
=========
1. build dokerimage chenxinaz/clash_updater as Dockerfile
2. create data dir ../volume/updater/{data,bak}, the `clash_updater.sh` will do this for you.
3. create crontab task as `clash_updater.sh` comments.
