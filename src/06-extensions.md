# Extensions worth knowing

These build on LNURL-pay and explain why LNURL is so widespread today.

- **successAction (LUD-09).** After a successful payment the service can return an action: show a
  message, open a URL, or deliver a secret that is AES-encrypted with the payment preimage. The last
  one is clever: only someone who actually paid knows the preimage and can decrypt, for example, a
  voucher code or a download.

- **Comments (LUD-12).** The first response contains `commentAllowed: <n>`. The wallet may then send
  a comment of up to `n` characters with the callback. Handy for a "thanks!" note on a donation.

- **payerData (LUD-18).** The payer can identify itself: with a name, a pubkey, or an auth signature.
  This is the technical basis for the next item.

- **Nostr zaps.** The "zaps" in the Nostr network are LNURL-pay plus a Nostr extension. A `nostr`
  field carries a signed Nostr event request, and after payment a public "zap receipt" is posted. If
  your audience knows Nostr, this is a motivating "what is it all for" example.

- **verify (LUD-21).** Lets the wallet ask the service for the payment status (paid or open) without
  having to watch the Lightning layer itself.
