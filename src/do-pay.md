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

This is the function. Read it, then run it with one of the methods below.

```python
import urllib.request, json

def pay(address, sats):
    user, host = address.split("@")
    pr  = json.load(urllib.request.urlopen(f"https://{host}/.well-known/lnurlp/{user}"))
    inv = json.load(urllib.request.urlopen(pr["callback"] + f"?amount={sats*1000}"))  # sats -> msat
    return inv["pr"]

print(pay("test@walletofsatoshi.com", 21))
```

**Easiest (just run it): download and run.** Two single-line commands, nothing to paste or type:

```sh
curl -O https://raw.githubusercontent.com/joshuakrueger-dfx/lugano-lnurl-ocp/main/hands-on/pay.py
python3 pay.py
```

**Method 1 (type it yourself): make the file from the terminal, no editor.** Paste this whole block
into the terminal. It writes a clean `pay.py` and runs it:

```sh
cat > pay.py <<'EOF'
import urllib.request, json
def pay(address, sats):
    user, host = address.split("@")
    pr  = json.load(urllib.request.urlopen(f"https://{host}/.well-known/lnurlp/{user}"))
    inv = json.load(urllib.request.urlopen(pr["callback"] + f"?amount={sats*1000}"))
    return inv["pr"]
print(pay("test@walletofsatoshi.com", 21))
EOF
python3 pay.py
```

**Method 2: one line, no file.** Paste this single command into the terminal:

```sh
python3 -c 'import urllib.request,json
def pay(a,s):
 u,h=a.split("@");pr=json.load(urllib.request.urlopen(f"https://{h}/.well-known/lnurlp/{u}"))
 return json.load(urllib.request.urlopen(pr["callback"]+f"?amount={s*1000}"))["pr"]
print(pay("test@walletofsatoshi.com",21))'
```

Either way, a real bolt11 invoice comes back (`lnbc...`). That is LNURL-pay end to end: resolve the
address, ask the callback for an amount, get the invoice you would pay. You just built it.

> **Two traps to avoid.** (1) Do not paste the Python lines straight into the terminal: the terminal
> is the shell (zsh), not Python, so it says `command not found: import`. (2) Do not save the file
> with **TextEdit**: it saves Rich Text (`.rtf`), and Python chokes on `\rtf1`. Use Method 1 above,
> or in TextEdit choose **Format → Make Plain Text** first.

> Amounts are in millisatoshi. 1 sat = 1000 msat, which is why the code sends `sats * 1000`.

## Try it

- Point it at your **own** Lightning Address (make one in seconds in Wallet of Satoshi (free app)).
- Change the amount and watch the invoice change.
- Want to go further, run a real merchant, attack it, and see how it is defended? That is the bonus
  section, [Security, trust, privacy](./07-security.md) and [the break-it lab](./08-lab.md).
