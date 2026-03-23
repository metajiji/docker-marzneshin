# Marzneshin Panel

## Tips

### Create admin user

```bash
docker compose exec -ti panel python marzneshin-cli.py admin create -u admin --sudo
```

### Update user

```bash
docker compose exec -ti -e CLI_PROG_NAME="marzneshin cli" panel python marzneshin-cli.py admin update --username=marzban
```
