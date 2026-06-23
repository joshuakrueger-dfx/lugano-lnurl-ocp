# The four sub-protocols

This is the main content. For each one: what it is for, the flow, and the single most important
detail.

The tell that separates them is one question: **who creates the invoice?** Keep it in mind.

## LNURL-pay (LUD-06), the important one

**What for:** a static, reusable payment code. A QR at the till, a donation button, a tip link.
Created once, used any number of times, optionally with a free-choice amount.

**Flow:**

1. Wallet decodes the LNURL, makes a `GET`. The server answers:

   ```json
   {
     "tag": "payRequest",
     "callback": "https://service.com/pay/callback",
     "minSendable": 1000,
     "maxSendable": 100000000,
     "metadata": "[[\"text/plain\",\"Donation to Alice\"]]"
   }
   ```

   `minSendable` and `maxSendable` are in msat (so 1000 means 1 sat).

2. The wallet shows the allowed range; the user picks an amount.
3. The wallet calls the callback with the amount:
   `GET https://service.com/pay/callback?amount=50000` (50 sat in msat).
4. The server answers with the actual, freshly created BOLT11 invoice:

   ```json
   { "pr": "lnbc500n1...", "routes": [] }
   ```

5. The wallet pays `pr`.

**The most important detail (security).** The invoice carries a `description_hash` (the `h` tag): the
hash of the `metadata` from step 1. The wallet checks that this hash matches. So the server cannot
quietly change the description in step 4. Step 1 and step 4 are cryptographically bound. That is the
elegant trick that makes a static code trustworthy.

> `metadata` is a JSON array of `[mimetype, content]` pairs. `text/plain` is required. Optional ones
> include `text/long-desc` and `image/png;base64` (a thumbnail up to 512 by 512), so a wallet can
> show more before paying than a bare invoice ever could.

## LNURL-withdraw (LUD-03), the "pull" payment

**What for:** collect money without typing an invoice first. This is the model behind Bitcoin ATMs,
faucets, and vouchers: the service shows a QR, your wallet pulls the amount.

**Flow:**

1. Wallet decodes, makes a `GET`. The server answers:

   ```json
   {
     "tag": "withdrawRequest",
     "callback": "https://service.com/withdraw/callback",
     "k1": "a random identifier for this session",
     "defaultDescription": "ATM withdrawal #7",
     "minWithdrawable": 1000,
     "maxWithdrawable": 50000000
   }
   ```

2. The user picks an amount; the wallet creates a BOLT11 invoice for it itself.
3. The wallet calls the callback: `GET .../withdraw/callback?k1=<k1>&pr=<own_invoice>`.
4. The server pays that invoice and returns `{"status": "OK"}`.

**The most important detail.** The direction is reversed. With pay, the **server** creates the
invoice; with withdraw, the **wallet** does. The `k1` is the glue that ties the two requests of one
session together, and it must be treated as single-use on the server. If a `k1` is accepted more
than once, a withdraw QR can be redeemed repeatedly and a till can be drained. That is the classic
implementation bug.

## LNURL-auth (LUD-04, plus 05 and 13), login without a password

**What for:** sign in to a service or authorise an action with no username or password, using only
cryptographic keys from the wallet.

**Flow (simplified):**

1. The service shows an LNURL with `tag=login` and a random challenge `k1` (32 bytes, hex).
2. The wallet derives a service-specific `linkingKey`: a key computed deterministically from the
   wallet seed and the service's **domain name**.
3. The wallet signs the `k1` with the private `linkingKey` (ECDSA on secp256k1, DER-encoded).
4. The wallet calls: `GET <url>?sig=<signature>&key=<public_linkingKey>&k1=<k1>`.
5. The server verifies the signature against the supplied public key. If it matches, the user is
   "the owner of exactly this key", so they are logged in.

**The most important detail (privacy).** Because the `linkingKey` differs per domain, every service
sees a different public key. Different services cannot link you by your key. At the same time the key
is reproducible for the same service, so you are recognised next time. This is a genuine advantage
over "log in with Google".

> The exact derivation (LUD-05, BIP32-based) is optional depth: a `hashingKey` from the master key
> via `m/138'/0`, then `HMAC-SHA256(hashingKey, domain)`; the first 16 bytes give four 32-bit numbers
> used to derive the service key under `m/138'/<long1>/<long2>/...`. For a workshop, "one reproducible
> key per domain" is usually enough.

## LNURL-channel (LUD-02), ask for a channel

**What for:** ask someone to open an inbound Lightning channel to you (useful for new users with no
inbound liquidity).

**Flow:** the server returns `tag=channelRequest`, a `k1`, and the `uri` (connection details of its
node). The wallet connects to that node, then calls the callback with `k1`, its own `remoteid` (node
ID), and `private` (0 or 1). The service then opens the channel.

In practice this is the least used of the four. For a workshop, a short mention that it exists is
often enough.

## Comparison (good for one slide)

| | Who creates the invoice? | Money flow | Typical use |
|---|---|---|---|
| pay | Server | to the service | donation, till, tip |
| withdraw | Wallet | from the service | ATM, faucet, voucher |
| auth | nobody (no payment) | none | login, authorisation |
| channel | nobody | none | inbound liquidity |

## The modern encoding alternative (LUD-17)

Instead of bech32, LUD-17 allows writing LNURLs directly as URLs with their own scheme: `lnurlp://`,
`lnurlw://`, `lnurlc://`, `keyauth://`. A wallet simply translates `lnurlw://domain.com/path` into a
`GET` to `https://domain.com/path`. Advantages: the domain is not obscured, no bech32 library is
needed, and each sub-protocol has its own scheme. It is formally a breaking change, so both forms
still coexist.
