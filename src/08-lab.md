{{#include ../hands-on/lab.md}}

---

## The code

The two files live in
[`hands-on/`](https://github.com/joshuakrueger-dfx/lugano-lnurl-ocp/tree/main/hands-on):

- `lnurl_merchant.py`: the server side of LNURL-pay. Honest, plus `--spoof` (amount lie),
  `--spoof swap` (binding lie), `--ocp` (multi-asset), and a `/.well-known/lnurlp/*` route so it has
  a Lightning Address. About 70 lines, standard library only.
- `lnurl_client.py`: a correct wallet. It reads bolt11 with around 40 lines of bech32, no library, so
  you can see that "Lightning" is HTTP plus JSON plus one hash check. Signatures are out of scope and
  not verified, which is exactly the "signature gap" you discuss in Part 3.

Clone the repository and run them as the lab describes:

```sh
git clone https://github.com/joshuakrueger-dfx/lugano-lnurl-ocp.git
cd lugano-lnurl-ocp/hands-on
python3 lnurl_merchant.py
```
