# Relay Server Implementations

The relay server sits between your cloud GPU container and the mining pool. It accepts HTTPS/WebSocket connections from the cloud (which looks legitimate) and forwards them as standard stratum protocol to the pool.

## Option A: Nginx Stream Proxy (Recommended)

**Best for:** Production use, high reliability, minimal CPU overhead

### Prerequisites
```bash
# Ubuntu/Debian
apt-get update
apt-get install nginx-full certbot
```

### SSL Certificate Setup
```bash
# Let's Encrypt (free, auto-renew)
certbot certonly --standalone -d relay.yourdomain.com

# Certificate files will be at:
# /etc/letsencrypt/live/relay.yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/relay.yourdomain.com/privkey.pem
```

### Nginx Configuration
```nginx
# /etc/nginx/nginx.conf
# Add this OUTSIDE the http block (at root level)

stream {
    # Define upstream (the mining pool)
    upstream pearl_pool {
        server sg1.alphapool.tech:5566;
        # Can add backup servers:
        # server eu1.alphapool.tech:5566 backup;
    }
    
    # SSL termination + proxy
    server {
        listen 443 ssl;
        proxy_pass pearl_pool;
        proxy_connect_timeout 10s;
        proxy_timeout 24h;  # Keep connection alive for mining
        
        ssl_certificate /etc/letsencrypt/live/relay.yourdomain.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/relay.yourdomain.com/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
    }
    
    # Optional: non-SSL port for testing
    server {
        listen 8080;
        proxy_pass pearl_pool;
        proxy_timeout 24h;
    }
}
```

### Start/Test
```bash
# Test config
nginx -t

# Restart
systemctl restart nginx

# Test connection (from another machine)
telnet relay.yourdomain.com 443
# Should connect (will show binary garbage - that's OK)

# Check logs
tail -f /var/log/nginx/error.log
```

### Systemd Service (Auto-Start)
Nginx already installs as systemd service, just enable:
```bash
systemctl enable nginx
systemctl status nginx
```

---

## Option B: Python Relay (More Control)

**Best for:** Custom logging, authentication, multiple pool support, easier debugging

### Implementation
```python
#!/usr/bin/env python3
# stratum_relay.py
import socket
import ssl
import threading
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StratumRelay:
    def __init__(self, 
                 listen_host: str = "0.0.0.0",
                 listen_port: int = 443,
                 pool_host: str = "sg1.alphapool.tech",
                 pool_port: int = 5566,
                 ssl_cert: Optional[str] = None,
                 ssl_key: Optional[str] = None):
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.pool_host = pool_host
        self.pool_port = pool_port
        self.ssl_cert = ssl_cert
        self.ssl_key = ssl_key
        
    def handle_client(self, client_sock: socket.socket, addr: tuple):
        """Handle a single client connection"""
        logger.info(f"New connection from {addr}")
        
        try:
            # Connect to mining pool
            pool_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            pool_sock.connect((self.pool_host, self.pool_port))
            logger.info(f"Connected to pool {self.pool_host}:{self.pool_port}")
            
            # Bidirectional relay
            def forward(src, dst, direction):
                try:
                    while True:
                        data = src.recv(4096)
                        if not data:
                            break
                        dst.sendall(data)
                        logger.debug(f"{direction}: {len(data)} bytes")
                except Exception as e:
                    logger.error(f"{direction} error: {e}")
                finally:
                    src.close()
                    dst.close()
            
            # Start bidirectional forwarding
            t1 = threading.Thread(target=forward, args=(client_sock, pool_sock, "client→pool"))
            t2 = threading.Thread(target=forward, args=(pool_sock, client_sock, "pool→client"))
            t1.start()
            t2.start()
            t1.join()
            t2.join()
            
        except Exception as e:
            logger.error(f"Relay error: {e}")
        finally:
            client_sock.close()
            logger.info(f"Connection from {addr} closed")
    
    def start(self):
        """Start the relay server"""
        # Create listen socket
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.listen_host, self.listen_port))
        server.listen(100)
        
        # Wrap with SSL if cert provided
        if self.ssl_cert and self.ssl_key:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(self.ssl_cert, self.ssl_key)
            server = context.wrap_socket(server, server_side=True)
            logger.info(f"SSL enabled (cert: {self.ssl_cert})")
        
        logger.info(f"Relay listening on {self.listen_host}:{self.listen_port}")
        logger.info(f"Forwarding to {self.pool_host}:{self.pool_port}")
        
        try:
            while True:
                client, addr = server.accept()
                threading.Thread(target=self.handle_client, args=(client, addr)).start()
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        finally:
            server.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Stratum relay server")
    parser.add_argument("--listen-host", default="0.0.0.0", help="Listen address")
    parser.add_argument("--listen-port", type=int, default=443, help="Listen port")
    parser.add_argument("--pool-host", default="sg1.alphapool.tech", help="Pool hostname")
    parser.add_argument("--pool-port", type=int, default=5566, help="Pool port")
    parser.add_argument("--ssl-cert", help="SSL certificate file")
    parser.add_argument("--ssl-key", help="SSL key file")
    
    args = parser.parse_args()
    
    relay = StratumRelay(
        listen_host=args.listen_host,
        listen_port=args.listen_port,
        pool_host=args.pool_host,
        pool_port=args.pool_port,
        ssl_cert=args.ssl_cert,
        ssl_key=args.ssl_key
    )
    
    relay.start()
```

### Run as Systemd Service
```ini
# /etc/systemd/system/stratum-relay.service
[Unit]
Description=Stratum Mining Relay
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/relay
ExecStart=/usr/bin/python3 /opt/relay/stratum_relay.py \
    --listen-port 443 \
    --pool-host sg1.alphapool.tech \
    --pool-port 5566 \
    --ssl-cert /etc/letsencrypt/live/relay.yourdomain.com/fullchain.pem \
    --ssl-key /etc/letsencrypt/live/relay.yourdomain.com/privkey.pem
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Install
mkdir -p /opt/relay
cp stratum_relay.py /opt/relay/
chmod +x /opt/relay/stratum_relay.py

# Enable and start
systemctl daemon-reload
systemctl enable stratum-relay
systemctl start stratum-relay

# Check status
systemctl status stratum-relay
journalctl -u stratum-relay -f
```

---

## Testing Your Relay

### From Local Machine
```bash
# Test connection (should connect without error)
telnet relay.yourdomain.com 443

# Test with actual miner
./alpha-miner \
  --pool stratum+tcp://relay.yourdomain.com:443 \
  --address prl1pYOUR_WALLET \
  --worker test-local

# Watch relay logs to see traffic
```

### Monitoring
```bash
# Nginx: watch active connections
watch -n 1 'ss -tan | grep :443 | wc -l'

# Python: check systemd logs
journalctl -u stratum-relay -f --since "5 min ago"
```

---

## Security Considerations

### Firewall Rules
```bash
# Only allow connections from known IPs (optional)
ufw allow from <modal-ip-range> to any port 443

# Or allow all (if using dynamic IPs)
ufw allow 443/tcp
```

### Rate Limiting (Nginx)
```nginx
# Add to stream context
limit_conn_zone $binary_remote_addr zone=conn_limit:10m;

server {
    listen 443 ssl;
    limit_conn conn_limit 5;  # Max 5 connections per IP
    proxy_pass pearl_pool;
    # ... rest of config
}
```

### Authentication (Python Only)
```python
# Add to StratumRelay.handle_client()
# Before connecting to pool:
def authenticate(self, client_sock):
    """Simple token-based auth"""
    client_sock.sendall(b"AUTH_TOKEN: ")
    token = client_sock.recv(64).decode().strip()
    
    if token != "your-secret-token":
        client_sock.sendall(b"UNAUTHORIZED\n")
        client_sock.close()
        return False
    
    client_sock.sendall(b"OK\n")
    return True

# Call it first in handle_client:
if not self.authenticate(client_sock):
    return
```

---

## Multi-Pool Support

### Nginx (Multiple Upstreams)
```nginx
stream {
    # Pearl pool
    upstream pearl {
        server sg1.alphapool.tech:5566;
    }
    
    # Another coin pool
    upstream othercoin {
        server pool.othercoin.com:3333;
    }
    
    # Pearl relay on :443
    server {
        listen 443 ssl;
        proxy_pass pearl;
        # ... ssl config
    }
    
    # Othercoin relay on :8443
    server {
        listen 8443 ssl;
        proxy_pass othercoin;
        # ... ssl config
    }
}
```

### Python (Port-Based Routing)
```python
# Start multiple relay instances
relay1 = StratumRelay(listen_port=443, pool_host="sg1.alphapool.tech", pool_port=5566)
relay2 = StratumRelay(listen_port=8443, pool_host="pool.othercoin.com", pool_port=3333)

threading.Thread(target=relay1.start).start()
threading.Thread(target=relay2.start).start()
```

---

## Troubleshooting

**"Connection refused"**
- Check firewall: `ufw status`
- Check service running: `systemctl status nginx` or `systemctl status stratum-relay`
- Check port binding: `ss -tlnp | grep 443`

**"SSL handshake failed"**
- Verify cert files exist and readable
- Check cert expiry: `openssl x509 -in cert.pem -noout -dates`
- Test cert: `openssl s_client -connect relay.yourdomain.com:443`

**"Pool connection refused"**
- Check pool is reachable: `telnet sg1.alphapool.tech 5566`
- Verify DNS: `nslookup sg1.alphapool.tech`
- Check relay logs for pool connection errors

**"High CPU usage" (Python only)**
- Use Nginx instead for production
- Or optimize Python: use `asyncio` instead of threads
- Limit concurrent connections

**"Shares not accepted"**
- Relay is transparent, shouldn't affect share acceptance
- Test miner directly to pool first (verify wallet/worker config correct)
- Check relay logs for protocol errors
