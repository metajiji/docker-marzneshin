#!/bin/sh

set -eu -o pipefail

# Issue certificates from Let's Encrypt
for SERVER_NAME in ${SERVER_NAMES:?err}; do
    [ -e "${LEGO_PATH:?err}/certificates/$SERVER_NAME.crt" ] || /lego --accept-tos \
        --http --http.port=0.0.0.0:80 --domains="$SERVER_NAME" run
done

# Cleanup: remove all files not matching .crt or .key for domains in SERVER_NAMES
for file in /tls/*; do
    [ -e "$file" ] || continue  # Skip if no files

    filename="${file##*/}"  # Extract filename without path
    domain="${filename%.*}"  # Extract name without extension (POSIX)
    ext="${filename##*.}"  # Extract extension

    is_required=false
    for SERVER_NAME in ${SERVER_NAMES:?err}; do
        if [ "$domain" = "$SERVER_NAME" ]; then
            is_required=true
            break
        fi
    done

    if [ "$is_required" = false ] || { [ "$ext" != "crt" ] && [ "$ext" != "key" ]; }; then
        rm -vf "$file"
    fi
done

# Copy certificates
for SERVER_NAME in ${SERVER_NAMES:?err}; do
    install -vm 0644 "${LEGO_PATH:?err}/certificates/$SERVER_NAME.crt" /tls/
    install -vm 0644 "${LEGO_PATH:?err}/certificates/$SERVER_NAME.key" /tls/
done

# Create and run cron task
crontab -u root - <<EOF
$(for SERVER_NAME in $SERVER_NAMES; do
    echo "$(shuf -i 0-59 -n 1) 0 * * * /lego --http --http.port=0.0.0.0:80 --domains=$SERVER_NAME renew --renew-hook='sh -x /lego-scripts/renew.sh' 2>&1 > /proc/$$/fd/1"
done)
EOF

exec crond -f -L /proc/$$/fd/1
