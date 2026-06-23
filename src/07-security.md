# Security, trust, privacy

This belongs in every serious workshop, otherwise people leave with a false picture of "magically
safe".

## Trust model

LNURL moves work onto a server, and you have to trust it to some degree. With LNURL-pay you only see
the final invoice after the server has created it. The `description_hash` trick (see
[The four sub-protocols](./04-subprotocols.md)) protects the description, but the **amount and the
payment target come from the server**. A malicious server could, for example, issue an invoice to
itself instead of to the supposed recipient. Rule of thumb: **LNURL is only as trustworthy as the
domain it comes from.**

Be precise about what the wallet can and cannot verify in LNURL-pay:

- It **can** check that the invoice amount equals what the user agreed to.
- It **can** check that `description_hash` equals `sha256(metadata)`, so the shown description is the
  bound one.
- It **cannot** verify who ultimately receives the sats. The destination is whatever the server put
  in the invoice.

## Transport

HTTPS is mandatory (a valid certificate, no self-signed) or a Tor onion link. No plaintext HTTP on
the clearnet.

## The withdraw risk

As noted, `k1` must be single-use, otherwise a voucher can be double-redeemed.

## Privacy in auth

The domain-specific `linkingKey` prevents cross-service tracking. That is a real plus over "log in
with Google" and a good discussion topic.

## Phishing

Because an LNURL hides a domain (bech32), and because people scan QR codes without thinking, the
question "who actually owns this domain?" matters. Good wallets show the domain before the action.
For auth it is even required.

## OpenCryptoPay: the same pattern, a bigger trust surface

OpenCryptoPay (OCP) is LNURL-pay's `payRequest` generalised. Instead of one Lightning invoice, the
server returns a menu of assets across chains:

```json
{
  "tag": "payRequest",
  "callback": "https://.../cb",
  "transferAmounts": [
    { "method": "Lightning", "assets": [{ "asset": "BTC",  "amount": 0.00021 }] },
    { "method": "Ethereum",  "assets": [{ "asset": "USDT", "amount": 9.80  }] },
    { "method": "Polygon",   "assets": [{ "asset": "USDC", "amount": 9.80  }] }
  ]
}
```

A plain Lightning wallet ignores the rest and takes the Lightning path (backward compatible on
purpose). But look at everything you are now trusting the server to assert: the exchange rate, which
assets are real, which chain settles, the fee. In Part 3 of the lab the hash bound the description.
**What binds the rate?** Across chains there is no single hash tying it together. That is the open
frontier, and a good thing to argue about.

## The honest verdict (and the debate to run)

LNURL is the biggest UX win Lightning ever had. It won for a reason. The hash binding is good
hygiene, when wallets actually do it. But "self-custodial Bitcoin at the till" is mostly custodial
and mostly not Bitcoin the asset, and trusting the OCP rate and settlement is unsolved.

Frame it as two honest readings and let people argue both:

- **A useful bridge.** It meets users where they are. Real checkout, real assets, works with old
  wallets. Trust is the price of usable money, and we always paid it: exchanges, custodians, banks.
- **Re-centralisation.** One operator sets the rate, picks the asset and settlement, holds the money
  mid-flight, and logs every payer. "Bitcoin payments" where Bitcoin is optional and trust is
  required.

Both are defensible. The point of the workshop is that you can now tell which is which.
