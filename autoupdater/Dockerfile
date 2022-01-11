# DOCKER_BUILDKIT=1 docker build . -t chenxinaz/clash_updater
# DOCKER_BUILDKIT=1 docker build . --build-arg CN_MIRROR=1 -t chenxinaz/clash_updater # if you are in China mainland

FROM python:alpine

ARG CN_MIRROR=0

RUN if [ $CN_MIRROR=1 ] ; then OS_VER=$(grep main /etc/apk/repositories | sed 's#/#\n#g' | grep "v[0-9]\.[0-9]") \
    && echo "using mirrors for $OS_VER" \
    && echo https://mirrors.ustc.edu.cn/alpine/$OS_VER/main/ > /etc/apk/repositories \
    && pip install pyyaml -i https://pypi.tuna.tsinghua.edu.cn/simple; \
    else pip install pyyaml; fi

RUN mkdir -p autoupdater
COPY . /autoupdater

ENTRYPOINT ["/usr/local/bin/python", "/autoupdater/clash_updater.py"]


