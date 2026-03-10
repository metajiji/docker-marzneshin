# syntax=docker/dockerfile:1.7-labs
ARG DEBIAN_VERSION=13

FROM gcr.io/distroless/python3-debian$DEBIAN_VERSION:nonroot AS distroless

FROM debian:$DEBIAN_VERSION-slim AS build
SHELL ["/bin/bash", "-eo", "pipefail", "-c"]
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update \
    && apt-get install -y --no-install-suggests --no-install-recommends -o Binary::apt::APT::Keep-Downloaded-Packages=true \
        ca-certificates \
        python3 \
        curl

COPY --from=ghcr.io/astral-sh/uv:0.10-python3.13-trixie-slim /usr/local/bin/uv /usr/local/bin/uvx /usr/local/bin/

WORKDIR /rootfs/app
ARG MIGRATOR_VERSION=e0af91056f0cf644eefb0c6a5719766496f9a325
RUN mkdir -p /rootfs/app/data /rootfs/app/log \
    && curl -fsSL https://github.com/erfjab/migration/archive/$MIGRATOR_VERSION.tar.gz | (\
        tar -xz --strip-components=1 --wildcards --anchored \
            -C /rootfs/app \
            migration-*/app \
            migration-*/.python-version \
            migration-*/alembic.ini \
            migration-*/import.py \
            migration-*/main.py \
            migration-*/pyproject.toml \
            migration-*/uv.lock \
        ) \
# Set nonroot owner for data dir
    && chown -R 65532:65532 /rootfs/app/data /rootfs/app/log \
    && sed -i \
# TIP: Move state data to external volume
        -e 's|"{bot_name}\.log"|"log/{bot_name}.log"|' \
        /rootfs/app/app/handler/utils/log.py \
        /rootfs/app/app/importer/utils/system_config.py \
    && sed -i \
# TIP: Move state data to external volume
        -e 's|marzban\.json|data/marzban.json|' \
        /rootfs/app/app/export/export.py \
        /rootfs/app/app/importer/utils/system_config.py \
        /rootfs/app/import.py \
    && sed -i \
# TIP: Move state data to external volume
        -e 's|exceptions\.json|data/exceptions.json|' \
        /rootfs/app/app/handler/utils/panel.py \
        /rootfs/app/app/importer/utils/helpers.py \
        /rootfs/app/main.py

RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system --no-break-system-packages \
        --target="/rootfs/usr/lib/python$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")" \
        -r pyproject.toml

COPY node_usages.py /rootfs/app
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

ENV PATH=/usr/local/bin:/usr/bin:/bin \
    PYTHONPYCACHEPREFIX=/app/data/.pycache \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONNOUSERSITE=1 \
    PYTHONUNBUFFERED=1

COPY --from=build /rootfs /

USER nonroot

ENTRYPOINT ["python"]
CMD ["main.py"]
