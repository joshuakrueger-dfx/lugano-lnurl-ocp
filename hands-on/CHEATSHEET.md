# LNURL on one page — what you built today

> A Lightning QR is a URL. Scanning it is an HTTP GET. The Bitcoin shows up only in the last reply.
> Everything else is the web — and a server you trust.

## The flow (LNURL-pay, LUD-06)
```
wallet  ──GET /lnurl/pay──────────────▶  server
        ◀── payRequest {callback, min/max, metadata} ──
wallet  ──GET /callback?amount=<msat>─▶  server
        ◀── { pr: bolt11 invoice } ────  ← the only Bitcoin in the whole exchange
```
- `lnurl1…` = **bech32(an https URL)**. Nothing cryptographic, just an encoding.
- **Lightning Address** `name@host` → `https://host/.well-known/lnurlp/name`. Same URL, friendly label.

## The one check that matters
A safe wallet verifies **both**, before paying:
```
invoice.amount         == agreed amount          # stops the obvious overcharge
invoice.description_hash == sha256(metadata)     # LUD-06: binds the invoice to what you were shown
```
The rule is in the protocol; the **check runs in the wallet**. The blockchain enforces neither.

## The two attacks you ran
| | what the merchant did | which check caught it |
|---|---|---|
| `--spoof` | invoiced 1000× the shown price | the **amount** check |
| `--spoof swap` | kept the price, swapped the bound description | **only** the `description_hash` |
The swap is the whole reason LUD-06 exists: honest price, dishonest *what*.

## OpenCryptoPay — same trick, bigger surface
Same `payRequest` + a `transferAmounts` array → pay one purchase in BTC, USDT or USDC across chains.
Old wallets ignore the rest and take Lightning (backward compatible).
**Open question:** the hash binds the *description* — **nothing binds the rate, asset, or chain.**
Edit `TRANSFER_AMOUNTS`, restart, re-curl: the client never notices. The server just *says so*.

## Commands
```sh
python3 lnurl_client.py lnurl1…                        # decode a QR → it's a URL
python3 lnurl_merchant.py                               # honest 70-line LNURL-pay server
python3 lnurl_merchant.py --spoof | --spoof swap       # the loud / the subtle lie
python3 lnurl_merchant.py --ocp                         # multi-asset payRequest
curl -s http://127.0.0.1:8088/.well-known/lnurlp/coffee # your server's Lightning Address
```

## Take it home
1. Point your **own** wallet at `--spoof`. Does it catch the lie, or would it have paid?
2. Add a `successAction` (LUD-09) with a link → now it's phishing. Whose job is it to sanitise that?
3. Design a binding that protects the OCP **price** the way the hash protects the description.

## Specs
LUD-06 (payRequest) · LUD-09 (successAction) · LUD-16 (Lightning Address) — github.com/lnurl/luds
