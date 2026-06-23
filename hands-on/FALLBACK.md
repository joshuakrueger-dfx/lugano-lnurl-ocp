# Plan B: if the room cannot code (facilitator only)

You planned a hands-on lab, but the group turns out to be less terminal-comfortable than expected.
That is fine. The workshop still works. Switch into one of these modes, no slides change needed.

## The fastest rescue: one command

There is a single script that plays the entire lab and narrates it. Nobody assembles commands.

```sh
python3 demo.py          # paced: press Enter between steps (project this live)
python3 demo.py --auto   # run straight through
```

It shows, in order: honest payment passes, `--spoof` (loud lie) caught by the amount check,
`--spoof swap` (subtle lie) caught **only** by the hash binding, then `--ocp` (the multi-asset
payRequest). Same files as the lab, pure standard library. Before each run it prints a one-line
**predict** prompt, so the room still thinks, even if only you are typing.

## Three levels of fallback

1. **Follow-along.** You run every step on the projector, the students watch and **predict out loud**
   which check will catch which attack. Hands-on becomes a guided live demo. Zero coding from them,
   the "aha" is intact. Use `python3 demo.py` so you do not fumble commands either.

2. **Mixed room.** Tell them: "If the terminal is your thing, run it yourself from `lab.md`. If not,
   watch the screen and call out your prediction." People self-select. The keen ones go deep, the
   rest still engage with the idea.

3. **Talk + finale only.** Drop the typing entirely. Present the concept from the slides (or the
   course site), run `demo.py` once on screen as the proof, then go straight to the **Finale**: every
   student makes a Lightning Address at coinos.io in the browser (no code, no app) and you pay a few
   of them real sats with OpenCryptoPay. That live moment needs no coding at all and is the part
   people remember.

## Keep the learning even without typing

The teaching is in the **prediction and the discussion**, not the keystrokes:

- Before each attack, ask the room to commit to an answer (amount check, hash check, or both).
- After the swap, ask why the amount check was happy yet the payment was still rejected.
- Run the Part 3 pair questions as an open room discussion instead.

## What still works no matter what

- **The warm-up** is your live dfx.shop purchase. No student input needed.
- **The finale** (coinos Lightning Address, you pay them) is pure browser clicking. No code.
- **The course site and handout** carry every concept, so anyone can follow and review later.

If the network also fails, you lose only the warm-up and the finale. `demo.py` and the whole lab run
fully offline on localhost.
