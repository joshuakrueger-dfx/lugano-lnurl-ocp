# Why LNURL exists

To understand LNURL you first have to understand what is impractical about "bare" Lightning.

A normal Lightning bill is a **BOLT11 invoice**: a long string (`lnbc...`) that encodes exactly one
fixed amount and one fixed recipient, and is payable only once. Signed by the receiver. That design
is great for the payment itself, but it means:

- You cannot have a static, reusable "address" to receive money. Every payment needs a freshly
  generated invoice.
- Pulling money is awkward. Whoever wants to pay you must first request an invoice from you. Painful
  at a vending machine or on a desktop when your wallet is on your phone.
- There is no standard for login or authentication over Lightning.
- There are no human-readable addresses (like an email) natively.

LNURL is the answer to all of that. It is **not a new network and not a change to Lightning**. It is
a layer of HTTP conventions on top: an agreed format for how a wallet and a server talk to each
other so these scenarios become comfortable.

> **Workshop one-liner.** Lightning moves the money. LNURL organises the conversation before it:
> who asks whom, how, for what amount.

## The hook

Put two QR codes next to each other:

- a plain BOLT11 invoice: one use, fixed amount,
- a Lightning Address or LNURL-pay code: reusable, amount up to the payer.

Ask the room: *why does the second one do something the first one cannot?* Hold that tension. The
rest of the course is the answer.
