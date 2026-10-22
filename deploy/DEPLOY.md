# ziyokortest.uz — clone va ishga tushirish

`.env` yo‘q. Sozlamalar: `config/settings.py`.

## 1. Dasturlar (bir marta)

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nginx git
```

## 2. Kod

```bash
sudo mkdir -p /opt/ziyokor-bba
sudo chown "$USER:$USER" /opt/ziyokor-bba
git clone <REPO_URL> /opt/ziyokor-bba
cd /opt/ziyokor-bba
bash deploy/setup-server.sh install
python manage.py test bba.tests.test_api
```

## 3. Huquqlar (Gunicorn www-data ostida)

```bash
sudo chown -R www-data:www-data /opt/ziyokor-bba/data /opt/ziyokor-bba/staticfiles
sudo chown -R www-data:www-data /opt/ziyokor-bba/.venv
# Kod o‘qish uchun (venv www-data ga tegishli bo‘lsa yetarli)
sudo chown -R www-data:www-data /opt/ziyokor-bba
```

## 4. systemd

```bash
sudo cp deploy/bba.service /etc/systemd/system/bba.service
sudo systemctl daemon-reload
sudo systemctl enable --now bba
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:7583/
```

## 5. nginx

SSL dan oldin:

```bash
sudo cp deploy/nginx-ziyokortest.uz.initial.conf /etc/nginx/sites-available/ziyokortest.uz
sudo ln -sf /etc/nginx/sites-available/ziyokortest.uz /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

Certbot:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d ziyokortest.uz -d www.ziyokortest.uz
sudo cp deploy/nginx-ziyokortest.uz.conf /etc/nginx/sites-available/ziyokortest.uz
sudo nginx -t && sudo systemctl reload nginx
```

## 6. Yangilash

```bash
cd /opt/ziyokor-bba
git pull
bash deploy/setup-server.sh install
sudo systemctl restart bba
```

Backup: `cp data/bba.sqlite3 data/bba.sqlite3.bak`

**Kirish:** admin / `admin123` · demo / `demo123`
