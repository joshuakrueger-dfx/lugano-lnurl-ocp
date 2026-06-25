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

This is the function. Type it into a file and run it.

```python
import urllib.request, json

def pay(address, sats):
    user, host = address.split("@")
    pr  = json.load(urllib.request.urlopen(f"https://{host}/.well-known/lnurlp/{user}"))
    inv = json.load(urllib.request.urlopen(pr["callback"] + f"?amount={sats*1000}"))  # sats -> msat
    return inv["pr"]

print(pay("test@walletofsatoshi.com", 21))
```

**Type it into a file with `nano`.** `nano` runs inside the terminal and saves plain text, so none of
the traps below can bite you:

```sh
nano pay.py
```

Type the function, then **save and exit**: `Ctrl-O`, `Enter`, `Ctrl-X`. (`^O` means hold the Control
key and press the letter `O`, not `⌘` and not the `^` character.) Then run it:

```sh
python3 pay.py
```

A real bolt11 invoice comes back (`lnbc...`). That is LNURL-pay end to end: resolve the address, ask
the callback for an amount, get the invoice you would pay. You just built it.

**Prefer to stay in the terminal?** Two shortcuts that need no editor. Write the file in one paste:

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

Or run it in one line, no file at all:

```sh
python3 -c 'import urllib.request,json
def pay(a,s):
 u,h=a.split("@");pr=json.load(urllib.request.urlopen(f"https://{h}/.well-known/lnurlp/{u}"))
 return json.load(urllib.request.urlopen(pr["callback"]+f"?amount={s*1000}"))["pr"]
print(pay("test@walletofsatoshi.com",21))'
```

> **Traps to avoid, all four are about how the text lands in the file, not about LNURL.**
> 1. Do not paste the Python straight into the terminal: the terminal is the shell (zsh), not Python,
>    so it says `command not found: import`.
> 2. Do not save with **TextEdit**: it saves Rich Text (`.rtf`) and Python chokes on `\rtf1`. `nano`
>    avoids this; if you must use TextEdit, choose **Format → Make Plain Text** first.
> 3. In `nano`, `^O` is **Control + O**, not `⌘` and not the `^` key. If you get stuck, press
>    `Ctrl-X`, then `Y`, then `Enter`, which saves and quits in one go.
> 4. Indent with **only spaces, never mix tabs and spaces**, or Python throws `TabError`. If you
>    already mixed them, normalise the file:
>    `python3 -c "open('pay.py','w').write(open('pay.py').read().expandtabs(4))"`.

> Amounts are in millisatoshi. 1 sat = 1000 msat, which is why the code sends `sats * 1000`.

> **No terminal at all?** As a last resort, grab the finished file with
> `curl -O https://raw.githubusercontent.com/joshuakrueger-dfx/lugano-lnurl-ocp/main/hands-on/pay.py`
> then `python3 pay.py`. But typing it yourself is the point.

## Try it

- Point it at your **own** Lightning Address (make one in seconds in Wallet of Satoshi (free app)).
- Change the amount and watch the invoice change.
- **Finale challenge:** turn the `lnbc...` it prints into a **QR that pays you**, then show it. First
  working code the facilitator can scan gets paid real sats. Shortcut: Wallet of Satoshi's *Receive*
  screen. Boss level: make `pay.py` render the QR itself.
- Want to go further, run a real merchant, attack it, and see how it is defended? That is the bonus
  section, [Security, trust, privacy](./07-security.md) and [the break-it lab](./08-lab.md).
