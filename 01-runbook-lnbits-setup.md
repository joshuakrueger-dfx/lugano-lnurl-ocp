# Runbook: LNbits + FakeWallet setup (on the Mac mini)

All steps verified against **LNbits 1.5.5** source (funding-source class, env vars, API routes,
auth model). The fragile parts are flagged. **Do a full dry-run before the workshop.**

---

## 0. Prereqs
- `ssh mini` (Tailscale; user `josh-agends`), Docker installed.
- A cloudflared tunnel on the mini (you already run these) to expose port 5000 publicly over HTTPS.

## 1. Start LNbits with the FakeWallet backend

```sh
mkdir -p ~/lnbits-workshop/data && cd ~/lnbits-workshop
wget https://raw.githubusercontent.com/lnbits/lnbits/main/.env.example -O .env
```

Edit `.env` — set exactly these (names verified against `.env.example` + `settings.py`):

```ini
LNBITS_BACKEND_WALLET_CLASS=FakeWallet
FAKE_WALLET_SECRET="ToTheMoon1"
LNBITS_DENOMINATION=sats

LNBITS_ADMIN_UI=true          # enables the superuser + balance API
LNBITS_SITE_TITLE="Lugano LNURL Workshop"

# extensions must live on the mounted volume or they vanish on container recreate
LNBITS_EXTENSIONS_PATH="/app/data/extensions"

HOST=0.0.0.0
PORT=5000
```

Run it:

```sh
docker pull lnbits/lnbits
docker run --detach --publish 5000:5000 --name lnbits-workshop \
  --volume ${PWD}/.env:/app/.env \
  --volume ${PWD}/data/:/app/data \
  lnbits/lnbits
```

## 2. Get the superuser + set a password  ⚠️ critical gotcha

The balance/funding API requires a **superuser that has a password configured**
(`check_super_user` rejects with *"Super user must have credentials configured"* otherwise — verified
in `lnbits/decorators.py`).

1. Find the superuser id:
   ```sh
   docker logs lnbits-workshop 2>&1 | grep -i "super" | head
   # or read it from the data dir:
   cat ~/lnbits-workshop/data/.super_user 2>/dev/null
   ```
2. Open `http://<mini-ip>:5000/wallet?usr=<SUPERUSER_ID>` in a browser.
3. In the account menu → **set a username + password**. Without this, funding 403s.

Keep `<SUPERUSER_ID>` — the provisioning script needs it.

## 3. Expose publicly via cloudflared

Point a tunnel hostname at `http://localhost:5000`. Result: `https://lnbits.<yourdomain>`.
Students' phones reach this over Wi-Fi **or cellular** (matters when venue Wi-Fi dies).

> ⚠️ Your mini already runs tunnels (stockbots/cloister). Add a **new ingress entry**, don't
> overwrite the existing config, then restart the connector.

Verify: open `https://lnbits.<yourdomain>` on your phone over cellular.

## 4. Install the LNURLp extension (for the "shop" pay QR)

Admin UI → **Extensions** → install **"LNURLp"** (Pay Links). This gives a reusable LNURL-pay
link/QR everyone can pay (a fixed bolt11 invoice would be single-use, wrong for a room).

Create the shop:
- Make a wallet named `Shop` (or reuse the superuser wallet).
- LNURLp → **+ New Pay Link** → fixed or open amount → note its **LNURL / QR**. This is the
  "pay the shop" target for the 0:16 beat. Project it big.

*(Optional, for the LNURL-withdraw hands-on beat: also install the "Withdraw" extension and make a
multi-use voucher. Not required — wallets are already funded.)*

## 5. Provision the student wallets

See `provision_wallets.py`. It creates N wallets, funds each, and writes a printable card sheet.

```sh
python3 provision_wallets.py \
  --base https://lnbits.<yourdomain> \
  --superuser <SUPERUSER_ID> \
  --count 30 --sats 2100 \
  --out wallet_cards.html
```

What it does (all routes verified in source):
- `POST /api/v1/account {"name": "..."}` → new user+wallet (`id`, `user`, `adminkey`, `inkey`)
- `PUT /users/api/v1/balance?usr=<superuser> {"id": <wallet_id>, "amount": <sats>}` → credits it
- builds `https://…/wallet?usr=<user>&wal=<id>` per student and renders QR cards
  (QR via LNbits' own `/api/v1/qrcode/{data}` endpoint — no extra deps)

Open `wallet_cards.html` in a browser → **Print → Save as PDF** → print + cut. One card per student.

## 6. Dry-run (do not skip)
- [ ] Scan one card with your phone over the **public URL** → wallet opens showing the funded balance.
- [ ] From that wallet, pay the **shop LNURL** → balance drops, shop balance rises (instant, internal).
- [ ] Decode + `curl` the shop LNURL on a laptop → JSON with `tag:"payRequest"`, `callback`, `minSendable`.
- [ ] Repeat on a second phone (iOS + Android) — browser camera/permission quirks differ.

## Failure modes & fixes
| Symptom | Cause | Fix |
|---|---|---|
| Funding call 403 "super user must have credentials" | superuser has no password | Step 2 |
| Funding call 403 "not authorized" | `usr` query auth disabled | keep default `auth_allowed_methods` (includes `user-id-only`) |
| `POST /api/v1/account` 403/forbidden | new accounts disabled or `LNBITS_ALLOWED_USERS` set | ensure `LNBITS_ALLOW_NEW_ACCOUNTS=true` (default) and no allowed-users restriction |
| Extensions gone after restart | not on volume | `LNBITS_EXTENSIONS_PATH` on mounted `data/` (step 1) |
| Phone can't open wallet | Wi-Fi blocked | public cloudflared URL works on cellular too |
