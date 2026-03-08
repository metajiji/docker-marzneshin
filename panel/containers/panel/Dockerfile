# syntax=docker/dockerfile:1.7-labs
ARG DEBIAN_VERSION=13
ARG MARZNESHIN_VERSION=0.7.4

FROM gcr.io/distroless/python3-debian$DEBIAN_VERSION:nonroot AS distroless

FROM debian:$DEBIAN_VERSION-slim AS prepare
SHELL ["/bin/bash", "-eo", "pipefail", "-c"]
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update \
    && apt-get install -y --no-install-suggests --no-install-recommends -o Binary::apt::APT::Keep-Downloaded-Packages=true \
        ca-certificates \
        curl \
        gcc \
        python3-pip \
        python3-dev

ARG MARZNESHIN_VERSION
RUN mkdir -p /rootfs/app/data \
    && curl -fsSL https://github.com/marzneshin/marzneshin/tarball/v${MARZNESHIN_VERSION:?err} | (\
        tar -xz --strip-components=1 --wildcards --anchored \
            -C /rootfs/app \
            marzneshin-marzneshin-*/app \
            marzneshin-marzneshin-*/cli \
            marzneshin-marzneshin-*/dashboard \
            marzneshin-marzneshin-*/alembic.ini \
            marzneshin-marzneshin-*/main.py \
            marzneshin-marzneshin-*/marzneshin-cli.py \
            marzneshin-marzneshin-*/requirements.txt \
        ) \
# TODO: Upgrade psycopg for compat with debian13
    && sed -i \
        -e 's|^psycopg\(.*\)==.*|psycopg\1==3.3.3|g' \
# TIP: Keep same version at original, but not specified in requirements.txt
        -e '1i click==8.2.1' \
        /rootfs/app/requirements.txt \
# Set nonroot owner for data dir
    && chown -R 65532:65532 /rootfs/app/data

RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 --disable-pip-version-check install --prefix=/rootfs/usr --ignore-installed --root-user-action=ignore \
        -r /rootfs/app/requirements.txt

COPY entrypoint.py /rootfs/

FROM node:20-alpine AS build

COPY --from=prepare /rootfs /rootfs

WORKDIR /rootfs/app/dashboard

ARG MARZNESHIN_VERSION
ARG VITE_BASE_API=/api/
ARG VITE_LATEST_APP_VERSION=$MARZNESHIN_VERSION-patched
RUN --mount=type=cache,target=/root/.cache \
    --mount=type=cache,target=/root/.local \
    --mount=type=cache,target=/.pnpm-store \
    corepack enable && corepack prepare pnpm@9 --activate \
    && pnpm config set store-dir /.pnpm-store \
    && pnpm install \
    && npm run build --if-present -- --outDir 'dist' --assetsDir 'static' \
    && rm -rf node_modules

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

WORKDIR /app

ENV PATH=/usr/local/bin:/usr/bin:/bin
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONNOUSERSITE=1
ENV PYTHONUNBUFFERED=1

COPY --from=build /rootfs /

USER nonroot

# Use JSON syntax for ENTRYPOINT to avoid starting a shell
ENTRYPOINT ["python3"]
CMD ["/entrypoint.py"]
