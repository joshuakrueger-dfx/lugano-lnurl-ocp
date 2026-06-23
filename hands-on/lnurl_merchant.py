#!/usr/bin/env python3
"""Minimal LNURL-pay 'merchant' — pure stdlib. One file. No pip, no Node, no Bitcoin node.

Run:
    python3 lnurl_merchant.py                 # honest merchant
    python3 lnurl_merchant.py --spoof         # the LOUD lie: invoices 1000x the shown amount
    python3 lnurl_merchant.py --spoof swap    # the SUBTLE lie: right amount, wrong thing bought
    python3 lnurl_merchant.py --ocp           # OpenCryptoPay: one payRequest, many assets/chains

Endpoints — this is the ENTIRE server side of LNURL-pay:
    GET /lnurl/pay                       -> the payRequest JSON a wallet fetches first
    GET /lnurl/callback?amount=<msat>    -> {"pr": "<bolt11 invoice>"}
    GET /.well-known/lnurlp/<name>       -> the SAME payRequest (LUD-16 Lightning Address)

A Lightning Address `name@host` is nothing but a friendly alias: the wallet rewrites it to
https://host/.well-known/lnurlp/name and gets the payRequest above. Same URL, nicer label.

The workshop point: there is NO Bitcoin here. It's HTTP + JSON. The server (you) decides what
the wallet sees. In every mode the wallet is shown the same "Coffee, 21 sats" — the lie, when
there is one, lives only in the invoice. The single thing standing between you and a malicious
merchant is a check the WALLET must run (LUD-06: invoice.description_hash == sha256(metadata)).
"""
import argparse
import hashlib
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

HOST, PORT = "127.0.0.1", 8088

# What we ADVERTISE to the wallet (LUD-06 metadata, a JSON-encoded string). The wallet shows and
# hashes exactly this, in every mode.
METADATA = '[["text/plain","Coffee at the Lugano Summer School"]]'

# Pre-minted sample invoices. Signature validity is irrelevant for this lab; the client only ever
# READS their fields (amount from the hrp, description_hash from tag 23). Generated offline so the
# runtime stays stdlib-only.
#   GOOD: 21 sat,    description_hash == sha256(METADATA)        -> honest, client prints PASS
#   EVIL: 21000 sat, description_hash of a DIFFERENT description -> the LOUD attack (amount is off)
GOOD = "lnbc210n1p4r989cpp5s9wp934kayru6qf8dkwdxjhm080pt20smyna6s6p0pd5p740czpqsp5d6zz6laf6zej575vq66rac5zlyqzzpa6rg3yq4swf6w0ewpxpsmqhp5ya8tzwrjsx3rnaed60lheccrhzc6y85ugeh2dvfnyy7fdydjd2uq6s9tgsw9auctedqwxx0tz40tpngua8ccrmpwaphw8wnlrtemjxaxnst8wsr8e8t9uwp68rh9dlg85ghyp0lj8dww8enluml004pyrasqkundhl"
EVIL = "lnbc210u1p4r989cpp5npc58xv4gnz9sztd2d22s3e5jevfkp3wewlrt4j5lag2u4u6sttqsp5z0lljh6e4un2z3y0khm3gcf3vzj4xqd95um6mkn7h6enr6e5ahjqhp54e6wc5ytz7wdmmlmhuzuxq2xxapej2pu5qlwpy4ag5rpt8n6tkhsmz8lpyd6jwzjtg5elcp2cexy4zprl4c06dfc0wtn070cfkenf9l42y5lfrwluvxeu007k54eee4j7zg5x23stx630ck2590js9am7tgpseqmsx"


def _craft_invoice(hrp, description_hash_hex):
    """Hand-build a bolt11 string our reader will parse: the amount comes from `hrp`, and tag 23
    (description_hash) is pinned to a value we choose. The signature and bech32 checksum are
    deliberately bogus — the lab never verifies either, which is exactly the 'signature gap'.
    Pure stdlib, so the runtime stays dependency-free.

    Layout after the '1' separator, in 5-bit groups, matching what lnurl_client.py reads:
        7 (timestamp) + [tag 23 | len | 32-byte hash] + 104 (signature) + 6 (checksum)
    """
    cs = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
    acc = bits = 0
    field = []
    for b in bytes.fromhex(description_hash_hex):          # 32 bytes -> 52 five-bit groups
        acc = (acc << 8) | b
        bits += 8
        while bits >= 5:
            bits -= 5
            field.append((acc >> bits) & 31)
    if bits:
        field.append((acc << (5 - bits)) & 31)
    tag = [23, len(field) // 32, len(field) % 32] + field   # tag header + hash payload
    groups = [0] * 7 + tag + [0] * 104 + [0] * 6           # timestamp + tag + signature + checksum
    return hrp + "1" + "".join(cs[g] for g in groups)


# The SUBTLE attack: a perfectly valid 21-sat invoice (the amount matches to the satoshi!) whose
# description_hash is bound to something you never agreed to. ONLY the LUD-06 hash check catches it.
SWAP_BOUND_TO = '[["text/plain","Donation to the attacker — you never saw this"]]'
SWAP = _craft_invoice("lnbc210n", hashlib.sha256(SWAP_BOUND_TO.encode()).hexdigest())

# OpenCryptoPay: the same payRequest, stretched from one Lightning invoice to a menu of assets
# across chains. Notice what is NOT here — nothing binds the rate, the asset, or the chain.
TRANSFER_AMOUNTS = [
    {"method": "Lightning", "minFee": 0,   "assets": [{"asset": "BTC",  "amount": 0.00021}]},
    {"method": "Ethereum",  "minFee": 120, "assets": [{"asset": "USDT", "amount": 9.80}]},
    {"method": "Polygon",   "minFee": 1,   "assets": [{"asset": "USDC", "amount": 9.80}]},
]


class Handler(BaseHTTPRequestHandler):
    mode = None     # None (honest) | "amount" | "swap"
    ocp = False

    def _json(self, obj):
        body = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _pay_request(self):
        base = f"http://{self.headers.get('Host', f'{HOST}:{PORT}')}"
        pr = {
            "tag": "payRequest",
            "callback": f"{base}/lnurl/callback",
            "minSendable": 21000,   # msat (= 21 sat)
            "maxSendable": 21000,
            "metadata": METADATA,
        }
        if self.ocp:
            pr["transferAmounts"] = TRANSFER_AMOUNTS   # one QR, many ways to pay
        self._json(pr)

    def do_GET(self):
        path = urlparse(self.path).path
        # A Lightning Address `name@host` resolves here. The name is ignored on purpose:
        # it's just a label in front of the very same payRequest /lnurl/pay returns.
        if path == "/lnurl/pay" or path.startswith("/.well-known/lnurlp/"):
            self._pay_request()
        elif path == "/lnurl/callback":
            inv = {"amount": EVIL, "swap": SWAP}.get(self.mode, GOOD)
            self._json({"pr": inv})
        else:
            self.send_error(404)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--spoof", nargs="?", const="amount", choices=["amount", "swap"], default=None,
                    help="amount = invoice 1000x too big (loud); swap = right amount, wrong description (subtle)")
    ap.add_argument("--ocp", action="store_true", help="serve an OpenCryptoPay multi-asset payRequest")
    args = ap.parse_args()
    Handler.mode = args.spoof
    Handler.ocp = args.ocp
    label = "OpenCryptoPay · multi-asset" if args.ocp else {
        "amount": "SPOOF · amount (the loud lie)",
        "swap":   "SPOOF · swap (the subtle lie)",
    }.get(args.spoof, "honest")
    print(f"LNURL-pay merchant [{label}]  ->  http://{HOST}:{PORT}/lnurl/pay")
    HTTPServer((HOST, PORT), Handler).serve_forever()
