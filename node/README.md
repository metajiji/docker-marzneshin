# Marzneshin Node

## Tips

### Generate self signed certificate

```bash
openssl req -x509 -nodes -newkey rsa:2048 -days 3650 -keyout test.key -out test.crt -addext subjectAltName="DNS:domain.tld" -subj /CN=domain.tld
```
