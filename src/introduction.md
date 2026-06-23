# LNURL: the most important Bitcoin protocol that isn't Bitcoin

You have used it a hundred times without knowing its name. Today you build a real Lightning payment
yourself, and use it for real.

This is a self-study course and a ready-to-run workshop. Work through it section by section. By the
end you can explain LNURL from first principles, build a working payment in a few lines, and (if you
want) go to the bonus and attack it to see exactly how it stays honest.

## The one idea to hold on to

> Lightning moves the money. LNURL organises the conversation before it: who asks whom, how, and
> for what amount. That conversation is plain HTTP. The Bitcoin shows up only at the very end.

Almost every "magical" Lightning experience you have seen (a reusable QR at a till, a tip link, a
`name@domain` address, login with one tap) is this HTTP layer doing the work. Once you see that,
the magic stops being magic, and you can reason about what you are actually trusting.

## Who this is for

A technical audience that already knows the basics of Bitcoin and a little Lightning. We skip
Bitcoin fundamentals, touch Lightning briefly, then go deep on LNURL and on OpenCryptoPay, the
open standard that generalises the same trick to any asset on any chain.

## What you will be able to do

- explain that a Lightning QR or address is just a URL, and prove it with one `curl`,
- build a working LNURL-pay function in about eight lines of standard-library Python,
- map the four sub-protocols and tell them apart by a single question,
- and, in the bonus, run a real merchant, attack it, and see the one check that keeps it honest.

## How to use this site

- **The course** is the theory, built from the problem upward. Read it in order.
- **Do it** is the hands-on: build a pay function yourself, then try LNURL with real wallets.
- **Bonus: break it (at home)** is the deeper, optional part: the trust model and a lab where you
  run a server, make it lie, and watch the defence catch it.

Everything is pure Python 3, no pip, no Node, no Bitcoin node. The repository also ships the slide
deck and the lab code, so you can run the entire workshop offline.
