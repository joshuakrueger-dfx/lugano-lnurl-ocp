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

Save this as a file called `pay.py`:

```python
import urllib.request, json

def pay(address, sats):
    user, host = address.split("@")
    pr  = json.load(urllib.request.urlopen(f"https://{host}/.well-known/lnurlp/{user}"))
    inv = json.load(urllib.request.urlopen(pr["callback"] + f"?amount={sats*1000}"))  # sats -> msat
    return inv["pr"]

print(pay("test@walletofsatoshi.com", 21))
```

Then run it from the terminal:

```sh
python3 pay.py
```

A real bolt11 invoice comes back (`lnbc...`). That is LNURL-pay end to end: resolve the address, ask
the callback for an amount, get the invoice you would pay. You just built it.

> **The number-one mistake:** do not paste the Python lines straight into the terminal. The terminal
> is the shell (zsh), not Python, so it reports `command not found: import`. Put the code in `pay.py`
> and run `python3 pay.py`, or, if you want a single line to paste, wrap it:
>
> ```sh
> python3 -c 'import urllib.request,json
> def pay(a,s):
>  u,h=a.split("@");pr=json.load(urllib.request.urlopen(f"https://{h}/.well-known/lnurlp/{u}"))
>  return json.load(urllib.request.urlopen(pr["callback"]+f"?amount={s*1000}"))["pr"]
> print(pay("test@walletofsatoshi.com",21))'
> ```

> Amounts are in millisatoshi. 1 sat = 1000 msat, which is why the code sends `sats * 1000`.

## Try it

- Point it at your **own** Lightning Address (make one in seconds in Wallet of Satoshi (free app)).
- Change the amount and watch the invoice change.
- Want to go further, run a real merchant, attack it, and see how it is defended? That is the bonus
  section, [Security, trust, privacy](./07-security.md) and [the break-it lab](./08-lab.md).
