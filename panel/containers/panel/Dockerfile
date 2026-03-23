ARG MARZNESHIN_VERSION=0.7.4
FROM python:3.12-slim AS base
WORKDIR /app

FROM base AS prepare
SHELL ["/bin/bash", "-eo", "pipefail", "-c"]

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update \
    && apt-get install -y --no-install-suggests --no-install-recommends -o Binary::apt::APT::Keep-Downloaded-Packages=true \
        curl

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
    && sed -i \
        -e 's/^typer==.*/typer==0.24.1/' \
        -e 's/^rich==.*/rich==14.3.3/' \
        /rootfs/app/requirements.txt \
# Set nobody owner for data dir
    && chown -R 65534:65534 /rootfs/app/data

RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 --disable-pip-version-check install --prefix=/rootfs/usr/local --ignore-installed --root-user-action=ignore \
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

FROM base

ENV PATH=/usr/local/bin:/usr/bin:/bin
ENV PYTHONPYCACHEPREFIX=/app/data/.pycache
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONNOUSERSITE=1
ENV PYTHONUNBUFFERED=1

COPY --from=build /rootfs /

USER nobody:nogroup

# Use JSON syntax for ENTRYPOINT to avoid starting a shell
ENTRYPOINT ["python3"]
CMD ["/entrypoint.py"]
