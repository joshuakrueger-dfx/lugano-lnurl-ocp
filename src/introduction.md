# LNURL: the most important Bitcoin protocol that isn't Bitcoin

You have used it a hundred times without knowing its name. Today you build it, break it, and decide
if it should exist.

This is a self-study course and a ready-to-run workshop. Work through it section by section, then
decide what goes into your own session. By the end you can explain LNURL from first principles,
run the whole thing yourself, and answer the hard questions without hand-waving.

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

- decode an LNURL by hand and explain that it is just a URL,
- run a complete LNURL-pay server in 70 lines of standard-library Python,
- explain the `description_hash` binding, and say precisely what it protects and what it does not,
- map the four sub-protocols and tell them apart by a single question,
- name the open trust problem that multi-asset payments leave unsolved.

## How to use this site

- **The course** (sections 1 to 7) is the theory, built from the problem upward. Read it in order.
- **Do it** is the hands-on lab and a guide to trying LNURL with real wallets and tools.
- **Teach it** is the facilitator guide: dramaturgy, timings, and the misconceptions to expect.

Everything in the lab is pure Python 3, no pip, no Node, no Bitcoin node. The repository also ships
the slide deck and the lab code, so you can run the entire workshop offline.
