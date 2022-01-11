#!/bin/bash
# 30 05 * * 1 /home/xin/projects/clash_on_n1/autoupdater/clash_updater.sh
WORK_DIR=/home/xin/projects/clash_on_n1
UPDATER_VOLUME=${WORK_DIR}/volume/updater
cd ${WORK_DIR}
mkdir -p ${UPDATER_VOLUME}/{data,bak}
rm ${UPDATER_VOLUME}/data/updater.log
docker run --rm -v ${UPDATER_VOLUME}:/autoupdater chenxinaz/clash_updater > ${UPDATER_VOLUME}/data/updater.log
cat ${UPDATER_VOLUME}/data/updater.log
cat ${UPDATER_VOLUME}/data/updater.log >> ${UPDATER_VOLUME}/data/updater_all.log
cat "==================================" >> ${UPDATER_VOLUME}/data/updater_all.log
if grep -Fxq "FAIL::" ${UPDATER_VOLUME}/data/updater.log; then
    echo "Some provider config download fail, please check."
else
    DT=$(date +%Y%m%d-%H%M%S)
    sed "s/🔰 节点选择/🔰 节点选择${DT}/g" ${UPDATER_VOLUME}/data/config.yaml > ${UPDATER_VOLUME}/data/config1.yaml
    cp ${UPDATER_VOLUME}/data/config1.yaml ${UPDATER_VOLUME}/bak/config.${DT}.yaml
    cp ${UPDATER_VOLUME}/data/config1.yaml ${WORK_DIR}/volume/clash/config.yaml
    docker-compose restart
fi

