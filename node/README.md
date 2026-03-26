# Marzneshin Node

## Install

Go to admin UI and copy *certificate* from *Settings* and save as `client.pem`

```bash
cp node.env.example node.env
docker compose up -d
```

## Tips

### Generate self signed certificate

```bash
openssl req -x509 -nodes -newkey rsa:2048 -days 3650 -keyout test.key -out test.crt -addext subjectAltName="DNS:domain.tld" -subj /CN=domain.tld
```

### Generate private key

```bash
docker compose exec -ti node xray x25519
```

### Generate shortIds

```bash
for i in {1..4}; do openssl rand -hex 8; done | jq -R . | jq -s .
```
