#!/bin/sh

URL=http://172.25.0.2
HOST_PORT=${URL#*//}  # Strip http:// or https://
HOST=${HOST_PORT%%[:/]*}  # Strip :port and /path
OUTPUT=nextcloud

rm -rf "$OUTPUT"

save_page() {
     wget \
          --mirror \
          --page-requisites \
          --adjust-extension \
          --no-parent \
          --span-hosts \
          --restrict-file-names=unix,nocontrol \
          -e robots=off \
          --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
          --no-host-directories \
          --directory-prefix="$OUTPUT" \
          --domains="$HOST" \
          --content-on-error \
          "$1"
}

save_page "$URL/login"
save_page "$URL/status.php"
save_page "$URL/index.php/error/404"
save_page "$URL/index.php/error/403"
save_page "$URL/core/img/favicon-touch.png"

find nextcloud -type f \( -name '*\?*' -o -name '*@*' \) -print0 | while IFS= read -r -d '' file; do
     new="${file%%[?@]*}"
     [ "$file" != "$new" ] && mv -vf "$file" "$new"
done

find nextcloud -type f -exec sed -i "s|$URL||g" {} +
