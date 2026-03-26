#!/bin/sh
set -eu

for SERVER_NAME in $SERVER_NAMES; do
    if [ ! -f "$LEGO_PATH/certificates/$SERVER_NAME.crt" ]; then
        echo "HEALTHCHECK ERROR: Missing certificate for $SERVER_NAME" >&2
        exit 1
    fi
done

exit 0
