# Try it yourself

You understand LNURL best once you have touched it. Three ways, from easiest to most revealing.

## Use a wallet

Wallets with LNURL support include Phoenix, Breez, Wallet of Satoshi, Zeus, Blixt, BlueWallet, Alby
(a browser extension), and coinos. Which feature each wallet supports varies, which is the whole
point of the optional LUDs.

Get a Lightning Address from one of them, then pay it a few sats from another. Notice you never
copied a one-time invoice.

## Run your own service

[LNbits](https://lnbits.com) is the classic choice here. It has ready-made extensions for
LNURL-pay links, withdraw and voucher codes, and Lightning Addresses. You can produce a scannable QR
in minutes.

## Do it by hand (the "aha" moment)

This is the most convincing one, and it is exactly what the [lab](./08-lab.md) does without any
dependencies.

Take an LNURL-pay link, decode the bech32 (online decoders exist, or use the `bech32` library or our
`lnurl_client.py`), and make the `GET` request yourself with `curl`. When you see the raw JSON
with the `tag` field, the core principle clicks immediately.

```sh
curl -s https://walletofsatoshi.com/.well-known/lnurlp/test | python3 -m json.tool
```

> Use testnet to avoid needing real money, or work with tiny amounts (a few sats) on mainnet, which
> is often more memorable.
