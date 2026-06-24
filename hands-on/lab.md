# Hands-on lab: LNURL is just HTTP. Prove it, then break it

Tech track. No pip, no Node, no Bitcoin node. Python 3 only. Two files:
`lnurl_merchant.py`, `lnurl_client.py`. Work on your own. Team up with a neighbour if you want, but
everyone should get their own hands on the keys and solve it themselves.

> Thesis you are about to verify with your own hands: **the discovery layer of every Lightning
> payment you have ever made contains no Bitcoin at all. It is an HTTP request to a server you trust.**

**Pick your pace.** Each part has a clear goal and a checkpoint that tells you when it worked.
If a part clicks fast, jump ahead. The Stretch goals at the bottom are real, not filler.

**30-second pre-flight, run this now.** If both print a version, you are ready:

```sh
python3 --version        # need >= 3.6   (on some machines it is just `python`)
curl --version           # any version   (Windows 10+, macOS, Linux all ship it)
```

No `curl`? Every `curl` below is just "GET this URL", so any HTTP client works. Stuck on anything?
Grab your neighbour or raise a hand.

---

## Part 0: warm-up (2 min). One real payment, on screen
**Goal:** see a real OpenCryptoPay payment happen end to end, before we take it apart.

Watch the facilitator buy the **0.01 EUR test product on dfx.shop** live: scan the QR, the
OpenCryptoPay checkout opens, confirm, paid in seconds. Real merchant on mainnet, real
OpenCryptoPay. No wallet or funds needed from you.

> Want to follow along on your own phone? Scan the same QR. It just opens the dfx.shop checkout.
> You do not have to pay; the point is to *see* it is a normal web checkout.

**Checkpoint:** the checkout shows the product and settles within seconds. Everything from Part 1
on is fully local, so no wallet and no internet are needed past this point.

## Part 1: where is the Bitcoin? (8 min)
**Goal:** prove that a "scary" Lightning QR is just a URL, and that a Lightning Address resolves to
that very same URL.

A `lnurl1…` string looks cryptographic. Decode one:

```sh
python3 lnurl_client.py lnurl1dp68gurn8ghj7urp0yhx27rpd4cxcefwwdmkjumn9uh8wetvdskkkmn0wahz7mrww4excup0vdhkven9v5w5wzts
```

It is `https://…/.well-known/lnurlp/coffee`. **That is the whole secret of LNURL: a bech32-wrapped
URL.** The QR is a URL. Scanning it means your wallet does an HTTP GET. No signatures, no chain yet.

**And that exact path is a Lightning Address.** When you type `coffee@pay.example.swiss` into a
wallet, it just rewrites it to `https://pay.example.swiss/.well-known/lnurlp/coffee` and does the
same GET. `name@host` is an alias for that URL, nothing more. Prove it on your own machine:

```sh
python3 lnurl_merchant.py          # terminal 1: leave running for the rest of the lab
# resolve "coffee@127.0.0.1:8088" by hand. The name is just a label:
curl -s http://127.0.0.1:8088/.well-known/lnurlp/coffee | python3 -m json.tool   # terminal 2
```

**Checkpoint:** the decode prints a normal `https://` URL, and the curl returns a JSON object whose
`tag` is `payRequest`. Your 70-line server now has a Lightning Address. No registry, no extra
protocol, just a path and a JSON reply.

## Part 2: become the merchant (8 min)
**Goal:** run the entire server side of LNURL-pay yourself and read the wire format.

That same server is the thing that tells wallets what to do. Hit its two real endpoints:

```sh
curl -s http://127.0.0.1:8088/lnurl/pay | python3 -m json.tool      # the payRequest, again
curl -s "http://127.0.0.1:8088/lnurl/callback?amount=21000"         # -> the bolt11 invoice
```

Read it: `tag:"payRequest"`, a `callback` URL, `min/maxSendable`, and `metadata`. The callback
hands back a bolt11 invoice (`pr`). You, a 70-line HTTP server, just spoke fluent Lightning. Edit
`METADATA` in the file, restart, curl again. You control the wallet's screen.

> **Watch the units.** Amounts are in **millisatoshi (msat)**. 1 sat = 1000 msat, so `21000` is
> 21 sat, not 21000 sat. This trips up almost everyone once.

**Checkpoint:** `/lnurl/pay` returns the `payRequest`, and the callback returns a `pr` field
starting with `lnbc`. You changed the metadata and saw the output change.

## Part 3: become the attacker (12 min)
**Goal:** break the payment two ways and see exactly which check catches which lie.

You decide what the screen says. So what stops you from showing "Coffee, 21 sats" and taking more?
You will run two attacks, one obvious and one not.

> **Predict first (do this before running anything).** On your own (compare with a neighbour if you
> like), write down your guess: for
> each attack below, *which* of the two checks will catch it, amount or `description_hash`? Then run
> it and see if you were right. The surprise is the point.

**Attack 1, the loud lie (wrong amount).**

```sh
# stop the honest merchant (Ctrl-C), then:
python3 lnurl_merchant.py --spoof          # shows coffee, invoices 1000x the amount
python3 lnurl_client.py http://127.0.0.1:8088/lnurl/pay
```

`ATTACK DETECTED`. The invoice is for 21000000 msat, you agreed to 21000. The **amount check**
caught it. Easy. But amount is the obvious lever; a careful attacker keeps the price *identical*.

**Attack 2, the subtle lie (right amount, wrong thing).**

```sh
python3 lnurl_merchant.py --spoof swap     # shows coffee 21 sat, binds the invoice elsewhere
python3 lnurl_client.py http://127.0.0.1:8088/lnurl/pay
```

Now the amount matches to the satoshi, so the amount check passes. Yet the client *still* prints
`ATTACK DETECTED`, and this time **only** the `description_hash` line fails. That is the entire
reason LUD-06 exists: the invoice is cryptographically bound to the exact text you were shown, so a
merchant cannot quietly swap *what* you are paying for while keeping the price honest.

Open `lnurl_client.py` and find the two lines that catch the two attacks:
- `msat == amount` catches Attack 1.
- `description_hash == sha256(metadata)`, the **LUD-06 binding**, is the *only* thing that catches Attack 2.

**Checkpoint:** honest run prints `PASS`; `--spoof` fails on the amount; `--spoof swap` passes the
amount and fails *only* on `description_hash`.

**Think it through (compare with a neighbour if you like):**
1. The protocol *defines* the defence, but it lives in the **client**. What happens if a wallet
   skips the check? (Some have.) Who is liable?
2. The server still wrote the invoice, so it chose who actually gets paid, and it sees who paid
   what, when. What did Lightning's "no intermediaries" promise just quietly lose?

## Part 4: OpenCryptoPay, the same pattern at scale (8 min)
**Goal:** extend your own server to multi-asset, then meet the open frontier worth building on.

OCP is your `payRequest`, generalised: instead of one Lightning invoice, the server offers a *menu*
of assets across chains. Your merchant already knows how. Flip one flag and look:

```sh
# stop the merchant (Ctrl-C), then:
python3 lnurl_merchant.py --ocp
curl -s http://127.0.0.1:8088/lnurl/pay | python3 -m json.tool
```

Same `tag:"payRequest"`, but now there is a `transferAmounts` array: pay in BTC over Lightning,
USDT over Ethereum, or USDC over Polygon, for the same coffee. A plain Lightning wallet just
ignores the rest and takes the first option (backward compatible, on purpose).

Now the builder's question. In Part 3 the `description_hash` bound the invoice to what you were
shown. Scan this JSON and ask: **what binds the rate?** Who asserts that 9.80 USDT really equals
0.00021 BTC? Which `asset` is real, which `chain` actually settles, who sets the `minFee`?

```sh
# proof there is no such binding: change the numbers, restart, and the client never notices.
# edit TRANSFER_AMOUNTS in lnurl_merchant.py (make USDT 99.00), then:
python3 lnurl_merchant.py --ocp
curl -s http://127.0.0.1:8088/lnurl/pay | python3 -m json.tool   # the server just says so.
```

**Checkpoint:** the `payRequest` now carries `transferAmounts`, and after you edit a number the
output changes with no complaint from anything. Part 3's hash protected the *description*. Across
assets and chains there is **no single hash** tying the rate together yet. Today the operator quotes
it, like any exchange. Binding it trustlessly is the open frontier, and a great thing to build.
Bring it to the Red Team.

---

## Finale: get paid, for real (live)
**Goal:** receive a real Lightning payment to a wallet you set up in a minute, and watch the exact
flow you just built move actual money.

1. Install **Wallet of Satoshi** on your phone (free, about a minute; scan the QR on the slide).
2. Open it. You now have a **Lightning Address**: `your-name@walletofsatoshi.com`. That is an
   LNURL-pay endpoint, the same thing your `pay()` function talks to. Put it on your screen.
3. The facilitator walks around and pays a few of you, **real satoshis**, with OpenCryptoPay.
4. Watch the balance jump. Under the hood, that wallet just ran the same `payRequest` flow you built.

**Checkpoint:** real sats land in your wallet. The thing you built today just moved real money. That
is the point.

> Wallet of Satoshi is **custodial**: it holds the sats for you. That is the trade you read about in
> the trust section. For a few sats in a workshop, it is the right tool. Needs internet.

## Stuck? (quick fixes)
- **Rather just watch it run?** `python3 demo.py` plays the whole lab (honest, both attacks, OCP)
  and narrates it, press Enter between steps. No commands to assemble.
- **`python3: command not found`**: try `python`. You need version 3.6 or newer.
- **`Address already in use` on start**: a merchant is already running. Find the old terminal and
  press Ctrl-C, or change `PORT` at the top of `lnurl_merchant.py`.
- **`curl` hangs or "connection refused"**: the merchant is not running. Start it in terminal 1
  first (Part 1), and keep that terminal open.
- **Windows quoting**: if the `?amount=...` URL misbehaves, wrap the whole URL in double quotes.
- **Nothing prints**: pipe through `python3 -m json.tool` to pretty-print, or drop it to see raw output.

## You can now
- decode an LNURL by hand and explain that it is just a URL,
- run the whole server side of LNURL-pay and a Lightning Address,
- explain the `description_hash` binding, and say precisely what it does and does not protect,
- name the open trust question that OpenCryptoPay leaves on the table.

## Stretch (if you finish early)
- Point a real wallet at your own spoof merchant (paste the URL). Does *it* catch the mismatch, or
  would it have paid? Report what you find.
- Add a `successAction` to your payRequest (LUD-09) that shows a message after payment. Now imagine
  it is a phishing link. Whose job is it to sanitise that?
