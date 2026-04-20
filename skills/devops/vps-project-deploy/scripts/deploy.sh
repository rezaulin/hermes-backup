#!/bin/bash
set -e

PROJECT=$1
PORT=$2
SUBDOMAIN=$3
DOMAIN=${4:-reviewtechno.me}
VPS_IP=$(curl -s ifconfig.me)
TOKEN=$(cat ~/.cloudflare-token | tr -d '\n')
FQDN="${SUBDOMAIN}.${DOMAIN}"

if [ -z "$PROJECT" ] || [ -z "$PORT" ] || [ -z "$SUBDOMAIN" ]; then
  echo "Usage: bash deploy.sh <project> <port> <subdomain> [domain]"
  echo "Example: bash deploy.sh chatbot 3001 bot reviewtechno.me"
  exit 1
fi

echo "🚀 Deploying ${FQDN} → port ${PORT}"

# --- Step 1: Get Zone ID ---
echo "📡 Getting Zone ID for ${DOMAIN}..."
ZONE_ID=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones?name=${DOMAIN}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" | jq -r '.result[0].id')

if [ "$ZONE_ID" = "null" ] || [ -z "$ZONE_ID" ]; then
  echo "❌ Zone not found for ${DOMAIN}. Check domain or token."
  exit 1
fi
echo "   Zone ID: ${ZONE_ID}"

# --- Step 2: Create DNS Record ---
echo "🌐 Creating DNS A record: ${SUBDOMAIN} → ${VPS_IP}..."
DNS_RESULT=$(curl -s -X POST "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  --data "{\"type\":\"A\",\"name\":\"${SUBDOMAIN}\",\"content\":\"${VPS_IP}\",\"proxied\":true}")

DNS_SUCCESS=$(echo "$DNS_RESULT" | jq -r '.success')
if [ "$DNS_SUCCESS" != "true" ]; then
  EXISTING=$(echo "$DNS_RESULT" | jq -r '.errors[0].message // empty')
  if echo "$EXISTING" | grep -qi "already exist"; then
    echo "   ⚠️  DNS record already exists, continuing..."
  else
    echo "❌ DNS creation failed: $EXISTING"
    exit 1
  fi
else
  echo "   ✅ DNS record created"
fi

# --- Step 3: Generate Origin SSL Certificate ---
echo "🔐 Generating SSL Origin Certificate..."
SSL_RESULT=$(curl -s -X POST "https://api.cloudflare.com/client/v4/certificates" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  --data "{\"hostnames\":[\"${FQDN}\",\"*.${DOMAIN}\"],\"requested_validity\":3650,\"request_type\":\"origin-rsa\"}")

CERT=$(echo "$SSL_RESULT" | jq -r '.result.certificate // empty')
KEY=$(echo "$SSL_RESULT" | jq -r '.result.private_key // empty')

if [ -z "$CERT" ] || [ -z "$KEY" ]; then
  echo "❌ SSL generation failed"
  echo "$SSL_RESULT" | jq '.errors'
  exit 1
fi

sudo mkdir -p /etc/nginx/ssl
echo "$CERT" | sudo tee /etc/nginx/ssl/${PROJECT}.crt > /dev/null
echo "$KEY" | sudo tee /etc/nginx/ssl/${PROJECT}.key > /dev/null
sudo chmod 600 /etc/nginx/ssl/${PROJECT}.key
echo "   ✅ SSL certificate saved"

# --- Step 4: Create Nginx Config ---
echo "⚙️  Creating nginx config..."
sudo tee /etc/nginx/sites-available/${PROJECT} > /dev/null <<NGINX
server {
    listen 80;
    listen 443 ssl;
    server_name ${FQDN};

    ssl_certificate /etc/nginx/ssl/${PROJECT}.crt;
    ssl_certificate_key /etc/nginx/ssl/${PROJECT}.key;

    location / {
        proxy_pass http://127.0.0.1:${PORT};
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_cache_bypass \$http_upgrade;
    }
}
NGINX

sudo ln -sf /etc/nginx/sites-available/${PROJECT} /etc/nginx/sites-enabled/${PROJECT}
sudo nginx -t && sudo systemctl reload nginx
echo "   ✅ Nginx configured and reloaded"

# --- Step 5: Start with PM2 ---
echo "🎯 Starting app with PM2 on port ${PORT}..."
cd /root/${PROJECT} 2>/dev/null || { echo "❌ /root/${PROJECT} not found. Clone/create your app first."; exit 1; }

if pm2 describe ${PROJECT} > /dev/null 2>&1; then
  echo "   ⚠️  PM2 process '${PROJECT}' exists, restarting..."
  PORT=${PORT} pm2 restart ${PROJECT} --update-env
else
  PORT=${PORT} pm2 start app.js --name ${PROJECT} --env production
fi
pm2 save

echo ""
echo "✅ DEPLOYED SUCCESSFULLY!"
echo "   🌐 https://${FQDN}"
echo "   📂 App: /root/${PROJECT}"
echo "   🔌 Port: ${PORT}"
echo "   📋 PM2: pm2 logs ${PROJECT}"
