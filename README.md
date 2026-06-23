# LNURL workshop: the most important Bitcoin protocol that isn't Bitcoin

A hands-on, 90-minute workshop for a technical audience. Build a Lightning payment server in 70
lines, use it to lie to a wallet, see why the one check that stops the lie lives in the wallet and
not the blockchain, then look honestly at OpenCryptoPay: what it solves, what it asks you to trust,
and the open frontier worth building on.

**Live site:** https://joshuakrueger-dfx.github.io/lugano-lnurl-ocp/

## What is in here

| Path | What it is |
|------|------------|
| `src/` | The course, as an mdBook (theory, lab, facilitator guide). Published to the live site. |
| `hands-on/` | The lab. Pure standard-library Python 3, no pip, no Node, no Bitcoin node. Includes `demo.py` (one-command narrated fallback) and `FALLBACK.md` (Plan B if the room cannot code). |
| `slides/` | Self-contained offline deck (`index.html`) and speaker script (`presenter.html`, EN and DE). Open by double-click. |

## Run the lab

```sh
git clone https://github.com/joshuakrueger-dfx/lugano-lnurl-ocp.git
cd lugano-lnurl-ocp/hands-on
python3 lnurl_merchant.py        # terminal 1
python3 lnurl_client.py http://127.0.0.1:8088/lnurl/pay   # terminal 2
```

Then follow [the lab](https://joshuakrueger-dfx.github.io/lugano-lnurl-ocp/08-lab.html): become the
merchant, become the attacker (`--spoof` and `--spoof swap`), and extend to multi-asset (`--ocp`).

## Build the site locally

```sh
cargo install mdbook   # or: brew install mdbook
mdbook serve --open
```

## License

Content and code are free to reuse for teaching. Attribution welcome.
