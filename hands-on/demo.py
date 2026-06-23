#!/usr/bin/env python3
"""Fallback: the whole LNURL lab in one command.

For when the room is not comfortable in a terminal, or you are short on time. Nobody has to
assemble commands. This plays the entire story and narrates it:

    honest -> PASS
    --spoof       (loud lie: invoices 1000x)        -> the amount check catches it
    --spoof swap  (subtle lie: right amount, wrong thing) -> only the hash binding catches it
    --ocp         (OpenCryptoPay: one payRequest, many assets)

Run:
    python3 demo.py          # paced: press Enter between steps (good for projecting live)
    python3 demo.py --auto   # run straight through, no pauses

Same files as the lab (lnurl_merchant.py, lnurl_client.py). Pure standard library, no pip.
"""
import argparse
import json
import os
import socket
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable or "python3"
HOST, PORT = "127.0.0.1", 8088
PAY = f"http://{HOST}:{PORT}/lnurl/pay"


def port_open():
    with socket.socket() as s:
        s.settimeout(0.3)
        return s.connect_ex((HOST, PORT)) == 0


def wait_port(timeout=8):
    end = time.time() + timeout
    while time.time() < end:
        if port_open():
            return True
        time.sleep(0.15)
    return False


def start_merchant(*args):
    p = subprocess.Popen([PY, os.path.join(HERE, "lnurl_merchant.py"), *args],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not wait_port():
        p.terminate()
        sys.exit(f"\nThe merchant did not come up on {HOST}:{PORT}. "
                 "Is another merchant still running? Stop it (Ctrl-C) and try again.")
    return p


def run_client():
    out = subprocess.run([PY, os.path.join(HERE, "lnurl_client.py"), PAY],
                         capture_output=True, text=True)
    print(out.stdout.rstrip())
    if out.stderr.strip():
        print(out.stderr.rstrip())


def rule(title=""):
    print("\n" + "=" * 66)
    if title:
        print(title)
        print("=" * 66)


def pause(auto):
    if auto:
        return
    try:
        input("\n[Enter] to continue ...")
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)


def step(title, predict, merchant_args, auto, ocp=False):
    rule(title)
    if predict:
        print(predict)
    pause(auto)
    p = start_merchant(*merchant_args)
    try:
        if ocp:
            data = json.load(urllib.request.urlopen(PAY, timeout=5))
            print("GET /lnurl/pay  ->  same payRequest, now with a transferAmounts menu:\n")
            print(json.dumps(data.get("transferAmounts", data), indent=2))
            print("\nChange a number in TRANSFER_AMOUNTS, restart, and the quote just changes.")
            print("Nothing binds the rate. That is the open frontier worth building on.")
        else:
            run_client()
    finally:
        p.terminate()
        p.wait()
        time.sleep(0.3)  # let the port free before the next bind


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--auto", action="store_true", help="run straight through without pauses")
    args = ap.parse_args()

    if port_open():
        sys.exit(f"Something is already listening on {HOST}:{PORT}. "
                 "Stop any running merchant (Ctrl-C in its terminal) and run this again.")

    rule("LNURL lab: the whole story in one command")
    print("You will see an honest payment pass, then two attacks, then OpenCryptoPay.\n"
          "No commands to type. Read along, and guess what happens before each run.\n"
          "(Ctrl-C to quit at any time.)")
    pause(args.auto)

    step("1/4  HONEST merchant  ->  expect PASS",
         "Predict: will the wallet accept or reject this one?",
         [], args.auto)

    step("2/4  --spoof  (loud lie: invoices 1000x the shown amount)",
         "Predict: which check catches it, the amount or the description_hash?",
         ["--spoof"], args.auto)

    step("3/4  --spoof swap  (subtle lie: right amount, wrong thing)",
         "Predict: the amount is correct this time. So what catches it?",
         ["--spoof", "swap"], args.auto)

    step("4/4  --ocp  (OpenCryptoPay: one payRequest, many assets across chains)",
         "Same pattern you just built, stretched to a menu of assets.",
         ["--ocp"], args.auto, ocp=True)

    rule("Done.")
    print("That was the whole lab: build it, break it two ways, then scale it to OpenCryptoPay.\n"
          "Now open lab.md to do any part yourself, or jump to the Finale and get paid for real.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
