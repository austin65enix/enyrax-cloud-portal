#!/usr/bin/env bash
set -e

echo "== ENYRAX Portal Health Check =="
echo

echo "[1] Hostname"
hostname
echo

echo "[2] Nginx status"
systemctl is-active nginx
echo

echo "[3] HTTP / HTTPS"
curl -I -s http://portal.soc-monitoring.dev | head -n 1
curl -I -s https://portal.soc-monitoring.dev | head -n 1
echo

echo "[4] Routes"
for path in / /soc/ /serviceops/ /projectops/ /status/; do
  code=$(curl -o /dev/null -s -w "%{http_code}" "https://portal.soc-monitoring.dev${path}")
  echo "${path} -> ${code}"
done
echo

echo "[5] TLS certificate"
sudo certbot certificates | grep -E "Certificate Name|Expiry Date|Domains"
echo

echo
echo "[6] API"
curl -s https://portal.soc-monitoring.dev/api/health
echo

echo
echo "[7] Modules API"
curl -s https://portal.soc-monitoring.dev/api/modules | head -c 300
echo

echo
echo "[8] SOC Summary API"
curl -s https://portal.soc-monitoring.dev/api/soc/summary | head -c 300
echo

echo "== Done =="
