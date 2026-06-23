#!/usr/bin/env python3
"""Provision N pre-funded LNbits browser wallets and a printable QR-card sheet.

Verified against LNbits 1.5.5 (FakeWallet backend):
  - POST /api/v1/account            {"name": ...}            -> {id, user, adminkey, inkey, ...}
  - PUT  /users/api/v1/balance      {"id":..,"amount":sats}  (auth via ?usr=<superuser>, needs password set)
  - GET  /api/v1/qrcode/{data}      -> SVG (used as <img> src; no extra deps)

Wallet open URL handed to students:  {base}/wallet?usr=<user>&wal=<wallet_id>

Stdlib only. Usage:
  python3 provision_wallets.py --base https://lnbits.example.com \
      --superuser <SUPERUSER_ID> --count 30 --sats 2100 --out wallet_cards.html
"""
import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request


def api(base, method, path, body=None, params=None):
    url = base.rstrip("/") + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url, data=data, method=method, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode()[:400]
        sys.exit(f"\n  HTTP {e.code} on {method} {path}\n  {detail}\n")
    except urllib.error.URLError as e:
        sys.exit(f"\n  Cannot reach {url}: {e.reason}\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", required=True, help="Public LNbits URL, e.g. https://lnbits.example.com")
    ap.add_argument("--superuser", required=True, help="Superuser user id (must have a password set)")
    ap.add_argument("--count", type=int, default=30, help="Number of student wallets")
    ap.add_argument("--sats", type=int, default=2100, help="Sats to credit each wallet")
    ap.add_argument("--out", default="wallet_cards.html", help="Printable card sheet output")
    a = ap.parse_args()

    base = a.base.rstrip("/")
    rows = []
    for i in range(1, a.count + 1):
        w = api(base, "POST", "/api/v1/account", body={"name": f"Student {i:02d}"})
        wid, uid = w["id"], w["user"]
        api(base, "PUT", "/users/api/v1/balance",
            body={"id": wid, "amount": a.sats}, params={"usr": a.superuser})
        url = f"{base}/wallet?usr={uid}&wal={wid}"
        rows.append((i, url))
        print(f"[{i:02d}/{a.count}] funded {a.sats} sats  {url}")

    cards = []
    for i, url in rows:
        qr = f"{base}/api/v1/qrcode/{urllib.parse.quote(url, safe='')}"
        cards.append(
            f'<div class="card"><div class="num">#{i:02d}</div>'
            f'<img src="{qr}" alt="QR {i}"/>'
            f'<div class="hint">Scan &rarr; your wallet opens</div></div>'
        )

    doc = (
        "<!doctype html><meta charset=utf-8><title>Workshop wallets</title><style>"
        "body{font-family:system-ui,sans-serif;margin:0}"
        ".grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8mm;padding:10mm}"
        ".card{border:1px dashed #999;border-radius:8px;padding:6mm;text-align:center;break-inside:avoid}"
        ".card img{width:48mm;height:48mm}"
        ".num{font-weight:700;font-size:14pt;margin-bottom:3mm}"
        ".hint{color:#555;font-size:9pt;margin-top:2mm}"
        "@media print{.card{page-break-inside:avoid}}"
        "</style><div class=\"grid\">" + "".join(cards) + "</div>"
    )
    with open(a.out, "w") as f:
        f.write(doc)
    print(f"\nWrote {len(rows)} cards -> {a.out}  (open in a browser, Print -> Save as PDF)")


if __name__ == "__main__":
    main()
