# The specs: LUDs

There is no single LNURL specification. There are many small, numbered documents: LUD-01, LUD-02,
and so on (LUD means Lightning URL Document), maintained on GitHub under
[lnurl/luds](https://github.com/lnurl/luds). Each wallet and each service implements only the parts
it needs. They are deliberately optional and modular, with a loose dependency hierarchy (for
example, "comments in payRequest" builds on the base payRequest).

This modularity is useful: you can say cleanly "this feature is LUD-XX", and you never have to treat
LNURL as one monolithic thing.

The ones worth knowing:

| LUD | What it is |
|-----|------------|
| LUD-01 | Base: bech32 encoding and decoding of the URL |
| LUD-02 | `channelRequest`, ask for a channel |
| LUD-03 | `withdrawRequest`, withdrawal (a "pull" payment) |
| LUD-04 | `auth`, passwordless login |
| LUD-05 | Key derivation for auth (BIP32-based) |
| LUD-06 | `payRequest`, paying |
| LUD-09 | `successAction`, a message, link, or secret after payment |
| LUD-12 | Comments in payRequest |
| LUD-13 | Key derivation for auth (signMessage-based) |
| LUD-16 | Lightning Address (`name@domain.com`) |
| LUD-17 | New URI schemes (`lnurlp://` instead of bech32) |
| LUD-18 | `payerData`, the sender identifies itself (basis for Nostr zaps) |
| LUD-21 | `verify`, query the payment status |
