# Marzneshin Node

## Export

```bash
cp docker-compose.override.example.yml docker-compose.override.yml
cp migrator.env.example migrator.env
```

Edit you `docker-compose.override.yml`, in my case configured volume for `marzban/db.sqlite3`:

```yaml
---
services:
  migrator:
    volumes:
      - type: bind
        source: /var/lib/docker/volumes/marzban-dashboard_marzban-var/_data/db.sqlite3
        target: /var/lib/marzban/db.sqlite3
        read_only: true
        bind:
          create_host_path: false
      - type: bind
        source: /var/lib/docker/volumes/marzneshin_panel_data/_data
        target: /var/lib/marzneshin
        read_only: false  # Yes required write access
        bind:
          create_host_path: false
```

Run export script

```bash
docker compose run --rm -ti migrator app/export/export.py
```

Run import command

```bash
docker compose run --rm -ti migrator import.py
```

Get owner and group for sqlite file

```bash
# ls -n /var/lib/docker/volumes/marzneshin_panel_data/_data/db.sqlite3
-rw-r--r--. 1 65534 65534 4218880 Mar 10 12:39 /var/lib/docker/volumes/marzneshin_panel_data/_data/db.sqlite3
```

Run import node usages command

```bash
docker compose run --rm --user 65534:65534 -ti migrator node_usages.py
```

Go to web panel and delete [injected user](https://github.com/erfjab/migration/blob/e0af91056f0cf644eefb0c6a5719766496f9a325/app/importer/utils/helpers.py#L100-L92) `bear`.
