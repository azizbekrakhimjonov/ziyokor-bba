# Ziyokor BBA — ziyokortest.uz

Django + Gunicorn. BBA test platformasi (`public/bba-platform.html`) va `POST /api/public/bba`.

## Mahalliy

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8080
```

## Server

Batafsil: [deploy/DEPLOY.md](deploy/DEPLOY.md)

- `deploy/setup-server.sh install` — venv, paketlar, migrate
- `deploy/bba.service` — systemd
- `deploy/nginx-ziyokortest.uz*.conf` — nginx
