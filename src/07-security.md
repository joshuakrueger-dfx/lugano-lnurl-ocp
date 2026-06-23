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

## OpenCryptoPay: the same pattern at scale

OpenCryptoPay (OCP) is LNURL-pay's `payRequest` generalised. Instead of one Lightning invoice, the
server offers a menu of assets across chains:

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
purpose). This is what makes a real till checkout work: the buyer pays in the wallet they already
have, and the hard parts (rate, chain, settlement) are handled server-side so they never see them.

The honest open question is the same one Part 3 raised. The `description_hash` binds the description.
**What binds the rate?** Today the operator quotes it, the way every exchange quote works, and across
chains there is no single hash tying it together yet. Binding it trustlessly is the open frontier,
and exactly the kind of thing this audience could go and build.

## The honest verdict (and the debate to run)

LNURL is the biggest UX win Lightning ever had. It won for a reason, and the hash binding is good
hygiene when wallets actually do it. OpenCryptoPay carries that win to real checkout: SPAR in
Switzerland is a live rollout, not a slide.

Be precise rather than breathless. At the till, settlement is custodial and the asset that moves may
not be BTC. That is a deliberate UX trade, and a good standard names it openly instead of hiding it.
Binding the rate and settlement trustlessly across chains is still open. That is the frontier, not a
flaw to apologise for.

Frame it as two honest readings and let people argue both:

- **A useful bridge.** It meets users where they are. Real checkout, real assets, works with old
  wallets. Trust is the price of usable money, and we always paid it: exchanges, custodians, banks.
- **The honest cost.** You depend on the operator for the rate, the settlement, and the privacy of
  who paid. A real dependency, the same one every payment rail carries. The bet is that good
  engineering and the right operator make it worth it.

Both are defensible. The point of the workshop is that you can argue either side on the merits.
