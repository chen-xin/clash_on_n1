# DOCKER_BUILDKIT=1 docker build . -t chen_x/clash
# DOCKER_BUILDKIT=1 docker build . --build-arg CN_MIRROR=1 -t chen_x/clash:alpine # if you are in China mainland

# NOTE: download clash core and name it ./clash/clash-linux

FROM alpine

ARG CN_MIRROR=0

RUN if [ $CN_MIRROR=1 ] ; then OS_VER=$(grep main /etc/apk/repositories | sed 's#/#\n#g' | grep "v[0-9]\.[0-9]") \
    && echo "using mirrors for $OS_VER" \
    && echo https://mirrors.ustc.edu.cn/alpine/$OS_VER/main/ > /etc/apk/repositories; fi

RUN apk add --no-cache curl openssl iptables
COPY clash/entrypoint.sh /clash/
COPY clash/clash-linux /clash/
COPY clash/Country.mmdb /clash/

RUN echo "Using clash ${CLASH_VERSION}" \
    && chmod +x /clash/entrypoint.sh

ENTRYPOINT ["/clash/entrypoint.sh"]


