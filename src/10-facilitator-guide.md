# Facilitator guide

How to actually run this as a 90-minute session. Adapt freely to length and prior knowledge. The
golden rule from every good workshop: **interaction beats slides.** Talk for short stretches, then
get hands on keyboards.

## A dramaturgy that works

1. **Hook (5 min).** Two QR codes side by side: a one-time BOLT11 invoice and a reusable
   LNURL-pay or Lightning Address. "Why does the second do what the first cannot?" Build the tension.
2. **The problem.** First the pain (section 1), then the solution.
3. **The core principle (section 2).** The one slide that must stick: bech32 link, GET, JSON with a
   `tag`, callback. If that lands, the rest is just variation.
4. **Live demo.** Decode a bech32 and `curl` a pay endpoint, read the JSON together. This is the
   "aha".
5. **The four sub-protocols (section 4)** with the comparison table as the anchor. Depth to taste:
   developers get the JSON, everyone gets the idea.
6. **Lightning Address (section 5)** as "and this is how it becomes human-friendly".
7. **Security and privacy (section 7)**, so nobody leaves with half-knowledge.
8. **Hands-on.** Everyone builds a pay server, then breaks it. See the [lab](./08-lab.md).

## Keep it interactive without adding slides

- **Predict, then verify.** Before any spoof runs, have pairs write down which check will catch which
  attack. The surprise is the teaching.
- **Show of hands.** "Who has paid with a Lightning QR?" gives you the room and a natural hook.
- **Pairs.** The attacker part and the red-team debate both run in pairs, not as a lecture.

## Common misconceptions to be ready for

- "LNURL is its own cryptocurrency or network." No. It is an HTTP convention on top of Lightning.
- "A Lightning Address is an email." No. Only the format resembles one; a `.well-known` HTTPS path is
  queried, not a mail server.
- **msat versus sat (a factor of 1000)** reliably causes arithmetic errors. Call it out early.
- "A static QR is insecure because it can be changed." Explain the `description_hash` binding.
- "LNURL is trustless like Bitcoin." No. You trust the server and the domain to a meaningful degree.

## Run it offline

This repository ships everything to run the session without internet:

- the slide deck in
  [`slides/`](https://github.com/joshuakrueger-dfx/lugano-lnurl-ocp/tree/main/slides): open
  `index.html` by double-click (self-contained, fonts inlined), and `presenter.html` for the speaker
  script in English and German,
- the lab and code in
  [`hands-on/`](https://github.com/joshuakrueger-dfx/lugano-lnurl-ocp/tree/main/hands-on),
  pure standard-library Python.

The only part that needs the network is the optional warm-up purchase on a real merchant. The rest
is fully local.
