#!/bin/sh

set -eu

install -vm 0644 "$LEGO_CERT_PATH" "$LEGO_CERT_KEY_PATH" /tls/
docker-compose --project-directory="${HOST_COMPOSE_DIR:?err}" restart nginx
