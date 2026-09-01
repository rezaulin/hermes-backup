# Stratum Wrapper Script (Cloud-Side Component)

This script runs **inside** the cloud GPU container. It acts as a local stratum server that the miner connects to, while forwarding traffic to your relay via HTTPS.

## Simple Python Wrapper (Recommended)

Save as `stratum_wrapper.py` (deploy with container):

```python
#!/usr/bin/env python3
"""
Stratum-over-HTTPS wrapper for cloud GPU mining stealth.
Miner connects to localhost:5566, wrapper forwards via HTTPS to relay.
"""
import socket
import requests
import json
import threading
import time
import sys
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

class StratumHTTPSWrapper:
    """Wraps stratum protocol in HTTPS for stealth mining"""
    
    def __init__(self, relay_url: str, listen_port: int = 5566):
        self.relay_url = relay_url.rstrip('/')
        self.listen_port = listen_port
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'pytorch/2.0.1 (compute-client)',
            'Content-Type': 'application/json'
        })
        self.session_id = None
        self.running = True
        
    def handle_miner(self, miner_sock: socket.socket):
        """Handle single miner connection"""
        logger.info("Miner connected")
        
        try:
            # Establish session with relay
            resp = self.session.post(
                f"{self.relay_url}/session/create",
                json={"protocol": "stratum", "version": "1.0"},
                timeout=10
            )
            resp.raise_for_status()
            self.session_id = resp.json()["session_id"]
            logger.info(f"Relay session established: {self.session_id[:8]}...")
            
            # Start background receiver (pool → miner)
            receiver = threading.Thread(
                target=self._receive_from_pool,
                args=(miner_sock,),
                daemon=True
            )
            receiver.start()
            
            # Forward miner → pool (main thread)
            buffer = b""
            while self.running:
                try:
                    chunk = miner_sock.recv(4096)
                    if not chunk:
                        logger.info("Miner disconnected")
                        break
                    
                    buffer += chunk
                    
                    # Process complete JSON-RPC messages
                    while b'\n' in buffer:
                        line, buffer = buffer.split(b'\n', 1)
                        if line.strip():
                            self._forward_to_pool(line)
                            
                except socket.timeout:
                    continue
                except Exception as e:
                    logger.error(f"Forward error: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"Connection error: {e}")
        finally:
            miner_sock.close()
            self._cleanup_session()
            
    def _forward_to_pool(self, data: bytes):
        """Send miner message to pool via HTTPS"""
        try:
            resp = self.session.post(
                f"{self.relay_url}/session/{self.session_id}/send",
                json={"data": data.decode('utf-8', errors='ignore')},
                timeout=5
            )
            resp.raise_for_status()
        except Exception as e:
            logger.error(f"Send error: {e}")
            
    def _receive_from_pool(self, miner_sock: socket.socket):
        """Poll relay for pool responses, forward to miner"""
        while self.running:
            try:
                resp = self.session.get(
                    f"{self.relay_url}/session/{self.session_id}/recv",
                    timeout=30
                )
                
                if resp.status_code == 200:
                    data = resp.json().get("data")
                    if data:
                        miner_sock.sendall(data.encode('utf-8'))
                        
                elif resp.status_code == 204:
                    # No data, continue polling
                    pass
                else:
                    logger.warning(f"Recv unexpected status: {resp.status_code}")
                    
            except requests.Timeout:
                # Normal for long-poll, continue
                continue
            except Exception as e:
                logger.error(f"Receive error: {e}")
                break
                
    def _cleanup_session(self):
        """Close relay session"""
        if self.session_id:
            try:
                self.session.delete(
                    f"{self.relay_url}/session/{self.session_id}",
                    timeout=5
                )
                logger.info("Session closed")
            except:
                pass
                
    def start(self):
        """Start wrapper server"""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("127.0.0.1", self.listen_port))
        server.listen(5)
        
        logger.info(f"Wrapper listening on 127.0.0.1:{self.listen_port}")
        logger.info(f"Relay endpoint: {self.relay_url}")
        
        try:
            while self.running:
                server.settimeout(1.0)
                try:
                    miner_sock, _ = server.accept()
                    threading.Thread(
                        target=self.handle_miner,
                        args=(miner_sock,),
                        daemon=True
                    ).start()
                except socket.timeout:
                    continue
                    
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            self.running = False
        finally:
            server.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Stratum-over-HTTPS wrapper for stealth mining"
    )
    parser.add_argument(
        "--relay",
        default="https://relay.yourdomain.com",
        help="Relay server URL"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5566,
        help="Local stratum port (default: 5566)"
    )
    
    args = parser.parse_args()
    
    wrapper = StratumHTTPSWrapper(
        relay_url=args.relay,
        listen_port=args.port
    )
    
    wrapper.start()
```

## Usage in Container

### Standalone Test
```bash
# Start wrapper
python3 stratum_wrapper.py --relay https://relay.yourdomain.com

# In another terminal, start miner
./alpha-miner \
  --pool stratum+tcp://127.0.0.1:5566 \
  --address prl1pYOUR_ADDRESS \
  --worker test
```

### Modal Integration
```python
# In Modal function:
import subprocess
import time

# Start wrapper (background)
wrapper = subprocess.Popen([
    "python3", "/root/stratum_wrapper.py",
    "--relay", "https://relay.yourdomain.com",
    "--port", "5566"
])

time.sleep(3)  # Let wrapper start

# Start miner (connects to wrapper)
miner = subprocess.Popen([
    "/usr/local/bin/alpha-miner",
    "--pool", "stratum+tcp://127.0.0.1:5566",
    # ... other args
])
```

## Relay API Endpoints (What Wrapper Expects)

Your relay must implement these endpoints:

**POST /session/create**
- Request: `{"protocol": "stratum", "version": "1.0"}`
- Response: `{"session_id": "abc123..."}`

**POST /session/{session_id}/send**
- Request: `{"data": "stratum json-rpc line"}`
- Response: `{"status": "ok"}`

**GET /session/{session_id}/recv**
- Response: `{"data": "stratum response"}` or 204 No Content

**DELETE /session/{session_id}**
- Response: `{"status": "closed"}`

See `references/relay_implementations.md` for relay server code.

## Troubleshooting

**"Connection refused to relay"**
- Check relay is running: `curl https://relay.yourdomain.com/health`
- Check firewall allows outbound HTTPS
- Verify relay URL correct (https://, no trailing slash)

**"Miner can't connect to wrapper"**
- Wrapper must start before miner
- Add `time.sleep(3)` between wrapper and miner launch
- Check wrapper logs: is it listening?

**"No shares accepted"**
- Wrapper is transparent, shouldn't affect shares
- Test miner directly to pool first (verify config)
- Check wrapper/relay logs for protocol errors

**"Wrapper crashes with JSON decode error"**
- Some miners send binary data before stratum
- Add error handling: `decode('utf-8', errors='ignore')`

**"High latency / stale shares"**
- Relay too far from pool geographically
- Deploy relay closer to pool (same region)
- Check network path: wrapper → relay → pool

## Performance Notes

**Overhead:**
- HTTP wrapping adds ~5-20ms latency per message
- Negligible impact on mining (shares every 10-30s)
- GPU compute unaffected (bottleneck is submission, not compute)

**Memory:**
- Wrapper uses ~10-20MB RAM
- Scales with buffer sizes (default: 4KB recv buffer)

**CPU:**
- <1% CPU on modern cores
- Wrapper is I/O bound, not CPU bound
