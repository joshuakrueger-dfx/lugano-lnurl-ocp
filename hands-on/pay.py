import urllib.request, json


def pay(address, sats):
    user, host = address.split("@")
    pr = json.load(urllib.request.urlopen(f"https://{host}/.well-known/lnurlp/{user}"))
    inv = json.load(urllib.request.urlopen(pr["callback"] + f"?amount={sats*1000}"))  # sats -> msat
    return inv["pr"]


# Change the address to your own (e.g. from Wallet of Satoshi) and the amount in sats.
print(pay("test@walletofsatoshi.com", 21))
