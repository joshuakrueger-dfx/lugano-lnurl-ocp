#!/usr/bin/env python3
"""A correct LNURL-pay client, in pure stdlib — what your wallet silently does for you,
plus the one check that stops a malicious merchant.

Usage:
    python3 lnurl_client.py http://127.0.0.1:8088/lnurl/pay
    python3 lnurl_client.py lnurl1...        # decodes a bech32 LNURL first, then runs

It deliberately reads bolt11 with ~40 lines of bech32 — no library, no magic — so you can
see that "Lightning" UX is HTTP + JSON + a hash check. Signatures are NOT verified here
(out of scope); we only read amount + description_hash.
"""
import hashlib
import json
import sys
import urllib.request

CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"


def bech32_decode(s):
    s = s.lower()
    pos = s.rfind("1")
    hrp = s[:pos]
    data = [CHARSET.index(c) for c in s[pos + 1:]]
    return hrp, data[:-6]            # strip the 6-char checksum


def convertbits(data, frm, to):
    acc = bits = 0
    maxv = (1 << to) - 1
    out = []
    for v in data:
        acc = (acc << frm) | v
        bits += frm
        while bits >= to:
            bits -= to
            out.append((acc >> bits) & maxv)
    return out


def lnurl_to_url(lnurl):
    _hrp, data = bech32_decode(lnurl)
    return bytes(convertbits(data, 5, 8)).decode()


# --- minimal bolt11 reader: amount (from hrp) + description_hash (tag 'h' = 23) ---
MULT = {"m": 10 ** -3, "u": 10 ** -6, "n": 10 ** -9, "p": 10 ** -12}


def bolt11_fields(inv):
    hrp, data = bech32_decode(inv)
    amt = ""
    for pfx in ("lnbcrt", "lntb", "lnbc"):
        if hrp.startswith(pfx):
            amt = hrp[len(pfx):]
            break
    msat = None
    if amt:
        if amt[-1] in MULT:
            msat = int(int(amt[:-1]) * MULT[amt[-1]] * 10 ** 11)
        else:
            msat = int(int(amt) * 10 ** 11)
    body = data[7:-104]              # drop 7-group timestamp and 104-group signature
    i, dh = 0, None
    while i < len(body):
        tag = body[i]
        ln = body[i + 1] * 32 + body[i + 2]
        i += 3
        field = body[i:i + ln]
        i += ln
        if tag == 23:                # description_hash
            dh = bytes(convertbits(field, 5, 8))[:32].hex()
    return msat, dh


def get(url):
    with urllib.request.urlopen(url, timeout=10) as r:
        return json.loads(r.read().decode())


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: lnurl_client.py <url|lnurl1...>")
    arg = sys.argv[1]
    if arg.lower().startswith("lnurl1"):
        url = lnurl_to_url(arg)
        print(f"decoded LNURL -> {url}")
        print("   (notice: it's just an HTTPS URL. there is no Bitcoin in this step.)\n")
    else:
        url = arg

    req = get(url)
    assert req.get("tag") == "payRequest", req
    meta = req["metadata"]
    amount = req["minSendable"]
    print(f"1. payRequest: merchant wants {amount} msat for metadata {meta!r}")

    inv = get(req["callback"] + f"?amount={amount}")["pr"]
    msat, dh = bolt11_fields(inv)
    want = hashlib.sha256(meta.encode()).hexdigest()
    print(f"2. callback returned an invoice:")
    print(f"     invoice amount    : {msat} msat   (you agreed to {amount})")
    print(f"     invoice descr.hash: {dh}")
    print(f"     sha256(metadata)  : {want}\n")

    ok_amount = msat == amount
    ok_binding = dh == want
    if ok_amount and ok_binding:
        print("PASS. The invoice is bound to exactly what you were shown. Safe to pay.")
    else:
        print("ATTACK DETECTED. The merchant lied:")
        if not ok_amount:
            print(f"  - amount mismatch: invoice is for {msat} msat, you agreed to {amount}")
        if not ok_binding:
            print("  - description_hash != sha256(metadata): the invoice commits to a")
            print("    description you were never shown. LUD-06 binding is broken")
        if ok_amount and not ok_binding:
            print("    NOTE: the amount looked perfect. ONLY the hash binding caught this swap.")
        print("  A naive wallet that skips these checks pays the attacker.")
        sys.exit(1)


if __name__ == "__main__":
    main()
