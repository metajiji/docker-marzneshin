# syntax=docker/dockerfile:1.7-labs
ARG DEBIAN_VERSION=13

FROM gcr.io/distroless/python3-debian$DEBIAN_VERSION:nonroot AS distroless

FROM debian:$DEBIAN_VERSION-slim AS build
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update \
    && apt-get install -y --no-install-suggests --no-install-recommends -o Binary::apt::APT::Keep-Downloaded-Packages=true \
        ca-certificates \
        curl \
        gcc \
        libc-dev \
        python3-pip \
        python3-dev

ARG MARZNODE_VERSION=0.5.7
RUN mkdir -p /rootfs/app/data \
    && curl -fsSL https://github.com/marzneshin/marznode/tarball/v${MARZNODE_VERSION:?err} | (\
        tar -xz --strip-components=1 --wildcards --anchored \
            --transform='s|/xray_config\.json$|/data/xray_config.json|' \
            -C /rootfs/app \
            marzneshin-marznode-*/marznode \
            marzneshin-marznode-*/marznode.py \
            marzneshin-marznode-*/requirements.txt \
        ) \
    && ( \
        cd /rootfs/app/data \
        && curl -fsSLRO https://github.com/Loyalsoldier/v2ray-rules-dat/releases/latest/download/geoip.dat \
        && curl -fsSLRO https://github.com/Loyalsoldier/v2ray-rules-dat/releases/latest/download/geosite.dat \
    ) \
# Set nonroot owner for data dir
    && chown -R 65532:65532 /rootfs/app/data

RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 --disable-pip-version-check install --prefix=/rootfs/usr --ignore-installed --root-user-action=ignore \
        -r /rootfs/app/requirements.txt

FROM scratch

COPY --from=distroless --parents \
    /bin \
    /etc \
    /home/nonroot \
    /lib \
    /lib64 \
    /usr/bin \
    /usr/lib \
    /usr/lib64 \
    /usr/share/zoneinfo \
    /var/run \
    /var/tmp \
    /

# https://hub.docker.com/r/tobyxdd/hysteria
COPY --from=tobyxdd/hysteria:v2.7.1 /usr/local/bin/hysteria /usr/local/bin/

# https://github.com/SagerNet/sing-box/pkgs/container/sing-box
COPY --from=ghcr.io/sagernet/sing-box:v1.13.2 /usr/local/bin/sing-box /usr/local/bin/

# https://github.com/xtls/Xray-core/pkgs/container/xray-core
COPY --from=ghcr.io/xtls/xray-core:26.2.6 /usr/local/bin/xray /usr/local/bin/

WORKDIR /app

ENV PATH=/usr/local/bin:/usr/bin:/bin
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONNOUSERSITE=1
ENV PYTHONUNBUFFERED=1

COPY --from=build /rootfs /

USER nonroot

ENTRYPOINT ["python"]
CMD ["marznode.py"]
