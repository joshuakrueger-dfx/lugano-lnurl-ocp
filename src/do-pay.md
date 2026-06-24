# Build a pay function

The whole of LNURL-pay fits in about eight lines, and you can type it yourself. No files to
download, no libraries, just Python 3.

## First, see that it is just a URL

A Lightning Address is a URL. `curl` one:

```sh
curl -s https://walletofsatoshi.com/.well-known/lnurlp/test
```

You get a `payRequest` back: a `tag`, a `callback`, `min`/`maxSendable`, and `metadata`. No app, no
Bitcoin yet, just HTTP and JSON. Swap `test` for any name and it still answers.

## Now build pay()

Type this into a file `pay.py`, or straight into `python3`:

```python
import urllib.request, json

def pay(address, sats):
    user, host = address.split("@")
    pr  = json.load(urllib.request.urlopen(f"https://{host}/.well-known/lnurlp/{user}"))
    inv = json.load(urllib.request.urlopen(pr["callback"] + f"?amount={sats*1000}"))  # sats -> msat
    return inv["pr"]

print(pay("test@walletofsatoshi.com", 21))
```

Run it. A real bolt11 invoice comes back (`lnbc...`). That is LNURL-pay end to end: resolve the
address, ask the callback for an amount, get the invoice you would pay. You just built it.

> Amounts are in millisatoshi. 1 sat = 1000 msat, which is why the code sends `sats * 1000`.

## Try it

- Point it at your **own** Lightning Address (make one in seconds in Wallet of Satoshi (free app)).
- Change the amount and watch the invoice change.
- Want to go further, run a real merchant, attack it, and see how it is defended? That is the bonus
  section, [Security, trust, privacy](./07-security.md) and [the break-it lab](./08-lab.md).
