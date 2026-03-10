FROM python:3.12-slim AS base
WORKDIR /app

FROM base AS build
SHELL ["/bin/bash", "-eo", "pipefail", "-c"]

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update \
    && apt-get install -y --no-install-suggests --no-install-recommends -o Binary::apt::APT::Keep-Downloaded-Packages=true \
        curl \
        libc-dev

ARG MARZNODE_VERSION=0.5.7
RUN mkdir -p /rootfs/app/data \
    && curl -fsSL https://github.com/marzneshin/marznode/tarball/v${MARZNODE_VERSION:?err} | (\
        tar -xz --strip-components=1 --wildcards --anchored \
            --transform='s|/xray_config\.json$|/data/xray_config.json|' \
            --transform='s|/hysteria\.yaml$|/data/hysteria.yaml|' \
            -C /rootfs/app \
            marzneshin-marznode-*/marznode \
            marzneshin-marznode-*/marznode.py \
            marzneshin-marznode-*/requirements.txt \
            marzneshin-marznode-*/xray_config.json \
            marzneshin-marznode-*/hysteria.yaml \
        ) \
    && curl -fsSLRo /rootfs/app/data/geoip.dat \
        https://github.com/Loyalsoldier/v2ray-rules-dat/releases/latest/download/geoip.dat \
    && curl -fsSLRo /rootfs/app/data/geosite.dat \
        https://github.com/Loyalsoldier/v2ray-rules-dat/releases/latest/download/geosite.dat \
# Set nobody owner for data dir
    && chown -R 65532:65532 /rootfs/app/data \
    && sed -i \
        -e 's@match = re.match(r"Private key: (.+)\\nPublic key: (.+)", output)@match = re.match(r"Private\\s?[Kk]ey: (.+)\\n(?:Public key|Password): (.+)", output)@' \
        /rootfs/app/marznode/backends/xray/_utils.py

RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 --disable-pip-version-check install --prefix=/rootfs/usr/local --ignore-installed --root-user-action=ignore \
        -r /rootfs/app/requirements.txt

FROM base

# https://hub.docker.com/r/tobyxdd/hysteria
COPY --from=tobyxdd/hysteria:v2.7.1 /usr/local/bin/hysteria /usr/local/bin/

# https://github.com/SagerNet/sing-box/pkgs/container/sing-box
COPY --from=ghcr.io/sagernet/sing-box:v1.13.2 /usr/local/bin/sing-box /usr/local/bin/

# https://github.com/xtls/Xray-core/pkgs/container/xray-core
COPY --from=ghcr.io/xtls/xray-core:26.2.6 /usr/local/bin/xray /usr/local/bin/


ENV PATH=/usr/local/bin:/usr/bin:/bin
ENV PYTHONPYCACHEPREFIX=/app/data/.pycache
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONNOUSERSITE=1
ENV PYTHONUNBUFFERED=1

COPY --from=build /rootfs /

USER nobody:nogroup

# Use JSON syntax for ENTRYPOINT to avoid starting a shell
ENTRYPOINT ["python3"]
CMD ["marznode.py"]
