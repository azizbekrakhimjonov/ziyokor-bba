# ziyokortest.uz — server + nginx

Ubuntu 22.04/24.04 yoki Debian 12 uchun. VPS IP: DNS da `A` yozuvi `ziyokortest.uz` va ixtiyoriy `www` → shu IP.

## 1. Server tayyorgarligi

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y nginx certbot python3-certbot-nginx git curl build-essential python3
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs
node -v   # v22.x
```

(Bun ishlatsangiz: `curl -fsSL https://bun.sh/install | bash`)

## 2. Loyihani joylash

```bash
sudo mkdir -p /opt/ziyokor-bba
sudo chown "$USER:$USER" /opt/ziyokor-bba
cd /opt/ziyokor-bba

git clone <SIZNING_REPO_URL> .
# yoki: rsync/scp bilan kod yoki release/bba-server (build serverda qiling!)

npm install    # yoki bun install
npm run build

sudo mkdir -p /opt/ziyokor-bba/data
sudo cp deploy/env.production.example /opt/ziyokor-bba/.env
# .env ni tahrirlang
```

**Muhim:** build **shu Linux serverda** bo‘lishi kerak (SQLite native modul).

## 3. systemd

```bash
sudo cp deploy/bba-ziyokortest.service /etc/systemd/system/bba.service
sudo systemctl daemon-reload
sudo systemctl enable --now bba
sudo systemctl status bba
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8080/
```

Agar `www-data` yozish huquqi kerak bo‘lsa:

```bash
sudo chown -R www-data:www-data /opt/ziyokor-bba/data
```

## 4. nginx (birinchi marta SSL siz)

```bash
sudo mkdir -p /var/www/certbot
sudo cp deploy/nginx-ziyokortest.uz.initial.conf /etc/nginx/sites-available/ziyokortest.uz
sudo ln -sf /etc/nginx/sites-available/ziyokortest.uz /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

Brauzerda: `http://ziyokortest.uz` ochilishi kerak.

## 5. HTTPS (Let's Encrypt)

```bash
sudo certbot --nginx -d ziyokortest.uz -d www.ziyokortest.uz
```

Keyin to‘liq konfig (www → apex redirect) uchun:

```bash
sudo cp deploy/nginx-ziyokortest.uz.conf /etc/nginx/sites-available/ziyokortest.uz
sudo certbot install --cert-name ziyokortest.uz   # kerak bo‘lsa
sudo nginx -t && sudo systemctl reload nginx
```

Yangilanish: `sudo certbot renew --dry-run`

## 6. Yangilash (deploy)

```bash
cd /opt/ziyokor-bba
git pull
npm install
npm run build
sudo systemctl restart bba
```

`data/bba.sqlite` ni backup qiling: `cp data/bba.sqlite data/bba.sqlite.bak`
