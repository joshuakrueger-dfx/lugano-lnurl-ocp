# Moderator-Leitfaden — LNURL/OCP Hands-on (für dich)

> Diese Karte ist **nicht** für die Teilnehmer (die haben `lab.md` + `CHEATSHEET.md`).
> Sie ist für dich: damit du die Übung selbst verstehst und bei Nachfragen souverän hilfst,
> auch wenn du sie noch nie gemacht hast. Englische Begriffe/Befehle bewusst im Original.

---

## 1. Das Mental-Modell in drei Sätzen

1. **Ein Lightning-QR ist eine URL.** Scannen = ein ganz normaler HTTP-GET. Das eigentliche
   Bitcoin (die `bolt11`-Invoice) taucht erst in der **letzten Antwort** auf.
2. **Der Server entscheidet, was die Wallet anzeigt.** Zwischen dir und einem bösartigen Händler
   steht genau *ein* Check — und der läuft **in der Wallet**, nicht auf der Blockchain.
3. **OpenCryptoPay (OCP)** ist derselbe `payRequest`, nur mit einer Menü-Liste aus Assets/Chains —
   und **nichts bindet den Wechselkurs**. Mehr Komfort, größere Vertrauensfläche.

Wenn ein Teilnehmer am Ende nur diese drei Sätze mitnimmt, war die Übung erfolgreich.

---

## 2. Die Bausteine (kurz & korrekt)

| Begriff | Was es ist | Merksatz für dich |
|---|---|---|
| **bech32** | Eine Text-Kodierung mit Prüfsumme (Daten → tippbarer String). | `lnurl1…`, `lnbc…` (Invoice) und `bc1…` (Bitcoin-Adresse) sind **dieselbe Kodier-Familie**. Nichts „Kryptografisches", nur eine Verpackung. |
| **LNURL** | Ein `lnurl1…`-String, der eine **https-URL** verpackt. | Auspacken = du bekommst eine ganz normale URL. Mehr ist es nicht. |
| **LNURL-pay (LUD-06)** | Der Ablauf: Wallet holt einen `payRequest`, dann eine Invoice. | Siehe Flow unten. Das ist das Herz der ganzen Übung. |
| **payRequest** | Die JSON-Antwort des Servers: `callback`, `minSendable`/`maxSendable` (in **msat**), `metadata`. | Das ist „was die Wallet zeigt", bevor irgendwas bezahlt wird. |
| **metadata** | Der Beschreibungstext (JSON-String), z. B. *„Coffee at the Lugano Summer School"*. | Genau dieser String wird angezeigt **und** gehasht. |
| **Lightning Address (LUD-16)** | `name@host` — sieht aus wie eine E-Mail. | Reiner Alias: Wallet schreibt es um zu `https://host/.well-known/lnurlp/name` und macht denselben GET. |
| **bolt11** | Die eigentliche Lightning-Rechnung (`pr` im Callback). | Beginnt mit `lnbc…`. **Hier** und nur hier steckt das „Bitcoin". |
| **msat** | Millisatoshi. **1 sat = 1000 msat.** | `minSendable: 21000` (msat) = **21 sat**. Häufige Verwirrungsquelle. |
| **description_hash (LUD-06-Bindung)** | Ein Feld *in der signierten Invoice* = `sha256(metadata)`. | Bindet die Invoice kryptografisch an den Text, den du gesehen hast. **Der entscheidende Schutz.** |
| **OCP / transferAmounts** | Erweiterung des `payRequest` um eine Liste: BTC/Lightning, USDT/Ethereum, USDC/Polygon … | Eine QR, viele Bezahlwege. Alte Wallets ignorieren die Liste und nehmen Lightning. |

---

## 3. Was in jedem Schritt passiert (mit deiner Rolle)

### Part 0 — Warm-up: „scan your card, pay the shop QR"
- **Infrastruktur:** LNbits (Version 1.5.5) mit **FakeWallet**-Backend läuft auf dem Mac mini,
  öffentlich über einen cloudflared-Tunnel (`https://lnbits.<domain>`). `provision_wallets.py`
  hat vorab N **vorgefundete Browser-Wallets** (z. B. 2100 sats) erzeugt und daraus eine
  druckbare **Karten-Seite mit QR-Codes** gebaut. Jede „Karte" ist ein QR auf eine URL
  `…/wallet?usr=…&wal=…`. Der **Shop-QR** kommt aus der LNbits-**LNURLp**-Extension (ein
  wiederverwendbarer LNURL-pay-Link — eine feste Invoice wäre einmalig, falsch für einen Raum).
- **Was der Teilnehmer tut:** Karte scannen → eine bereits gefüllte Wallet öffnet im Browser →
  den Shop-QR auf der Leinwand bezahlen → „es hat funktioniert".
- **Wichtig (Ehrlichkeit):** Wegen **FakeWallet** bewegt sich **kein echtes Bitcoin**. LNbits
  bucht intern und „settled" sofort. Die *UX* ist echt, die Sats sind Spielgeld. Das ist Absicht
  (offline-/internetausfallsicher) — sag es ruhig, falls jemand fragt.
- **Deine Rolle:** Der Warm-up muss nur **einmal pro Paar** klappen. Hängt eine Wallet, nicht
  kämpfen — der Rest des Labs braucht **weder Wallet noch Internet**.

### Part 1 — „Wo ist das Bitcoin?" (Decode)
- `python3 lnurl_client.py lnurl1…` → der String wird per bech32 ausgepackt und ist eine
  **https-URL** (`…/.well-known/lnurlp/coffee`). Aha-Moment: Der „kryptische" QR ist nur eine URL.
- Dann starten sie ihren **eigenen** Server (`lnurl_merchant.py`) und lösen `coffee@127.0.0.1:8088`
  von Hand auf — Beweis: **Lightning Address = Label vor einer URL**, kein Register, kein Extra-Protokoll.

### Part 2 — „Become the merchant"
- Zwei echte Endpoints: `GET /lnurl/pay` (der payRequest) und `GET /lnurl/callback?amount=…`
  (gibt die `bolt11`-Invoice zurück). Sie editieren `METADATA`, starten neu — und **steuern damit,
  was auf dem Wallet-Screen steht**. Kernbotschaft: Ein 70-Zeilen-HTTP-Server „spricht Lightning".

### Part 3 — „Become the attacker" (der Höhepunkt)
- **Angriff 1 — die laute Lüge:** `--spoof` → Invoice ist **1000×** zu hoch. Der **Betrags-Check**
  (`msat == amount`) fängt es. Offensichtlich.
- **Angriff 2 — die subtile Lüge:** `--spoof swap` → **Betrag stimmt auf den Satoshi**, aber die
  Invoice ist an eine *andere* Beschreibung gebunden („Donation to the attacker"). Der Betrags-Check
  ist zufrieden — **nur** der `description_hash`-Check schlägt an. **Das ist der ganze Grund, warum
  LUD-06 existiert:** ehrlicher Preis, unehrliches *Was*.
- **Die beiden entscheidenden Zeilen** stehen im **Client** (`lnurl_client.py`):
  - `ok_amount = msat == amount` → fängt Angriff 1
  - `ok_binding = dh == want` mit `want = sha256(metadata)` → fängt Angriff 2 (LUD-06)
- Diskussionsfragen zielen auf: Die Regel ist im Protokoll, **der Check lebt in der Wallet** — was,
  wenn eine Wallet ihn überspringt? Und: Der Server sieht weiterhin wer/was/wann → was wurde aus
  „keine Mittelsmänner"?

### Part 4 — OpenCryptoPay: gleiches Muster, größere Vertrauensfläche
- `--ocp` hängt `transferAmounts` an: dieselbe Coffee, zahlbar in BTC/Lightning, USDT/Ethereum,
  USDC/Polygon. Alte Wallets **ignorieren** die Liste (rückwärtskompatibel, mit Absicht).
- **Die Builder-Frage:** In Part 3 band der `description_hash` die Invoice an den *Text*. Über
  Assets und Chains hinweg gibt es **keinen einzigen Hash**, der den **Kurs** bindet. Ändere
  `TRANSFER_AMOUNTS` (USDT auf 99.00), neu starten, neu curlen — der Client merkt **nichts**.
  Der Server „sagt es einfach so". → Übergang zum Red-Team-Teil.

---

## 4. FAQ — Teilnehmerfragen & deine Antworten

**„Wo ist denn jetzt das eigentliche Bitcoin?"**
Nur in der allerletzten Antwort — der `bolt11`-Invoice (`pr`). Alles davor (QR scannen, payRequest,
Lightning Address auflösen) ist HTTP + JSON. Die „Discovery"-Schicht enthält null Bitcoin.

**„Sind die Sats echt? Habe ich gerade echtes Geld bezahlt?"**
Nein. Warm-up läuft auf LNbits **FakeWallet** — interne Buchung, sofort „settled", keine Chain,
kein Lightning-Netz. Im Lab sind die Invoices **von Hand gebaut**, Signatur absichtlich ungültig,
nie verschickt. Es bewegt sich nichts Reales. Bewusst so — funktioniert auch ohne Internet.

**„1000 msat = 1 sat? Wieso 21000?"**
Lightning rechnet in **Millisatoshi**. 1 sat = 1000 msat, also `minSendable: 21000` = **21 sat**.

**„Ist `lnurl1…` so etwas wie eine Bitcoin-Adresse?"**
Gleiche Kodier-Familie (**bech32**): Daten + Prüfsumme, tippbar/scanbar. `bc1…` (Adresse),
`lnbc…` (Invoice) und `lnurl1…` (verpackte URL) nutzen alle bech32. Es ist *nur* eine Verpackung,
keine Verschlüsselung.

**„Was ist der Unterschied zwischen LNURL und einer Lightning Address?"**
Eine Lightning Address (`name@host`) ist nur ein **freundlicher Alias**. Die Wallet schreibt sie um
zu `https://host/.well-known/lnurlp/name` — und ab da ist es exakt derselbe LNURL-pay-Flow.

**„Was ist `metadata` und warum wird es gehasht?"**
Das ist der Beschreibungstext, den die Wallet anzeigt (z. B. „Coffee …"). Der Hash davon steckt
**in der signierten Invoice** (`description_hash`). So ist garantiert: Was du **siehst**, ist exakt
das, wofür die Invoice gilt — *sofern die Wallet den Hash prüft*.

**„Warum prüft der Client die Invoice-Signatur nicht?"**
Bewusst außen vor (bräuchte Krypto-Libs / den Node-Key). Das Lab isoliert den **LNURL-spezifischen**
Schutz (den Hash-Check). Eine echte Wallet prüft **zusätzlich** die bolt11-Signatur gegen den Node.
Genau diese Lücke heißt im Code ehrlich „the signature gap".

**„Und wenn eine Wallet den Check einfach weglässt?"**
Dann zahlt sie den Angreifer. Das Protokoll *definiert* den Schutz, aber **durchsetzen muss ihn die
Wallet** — die Blockchain tut es nicht. Manche Wallets haben den Check tatsächlich übersprungen.
Daraus die schöne Haftungsfrage: Wer ist schuld, wenn die Regel da ist, aber niemand sie ausführt?

**„Lightning hat doch keine Mittelsmänner — stimmt das hier noch?"**
Der LNURL-Server sieht **wer wann was** zahlt. Die Discovery-Schicht führt einen **vertrauten
Server** wieder ein. Das ist der unbequeme Teil, auf den die Folien „What Bitcoin removed, LNURL
quietly brought back" zielen.

**„Warum ignoriert eine normale Wallet die OCP-Liste (`transferAmounts`)?"**
Unbekannte JSON-Felder werden ignoriert; die Wallet nimmt die Standard-Lightning-Option. Das ist
**Rückwärtskompatibilität** — Absicht, kein Bug.

**„Was bindet bei OCP den Kurs / das Asset / die Chain?"**
**Nichts** Kryptografisches. Der `description_hash` bindet den *Text*, nicht den Wechselkurs.
„9.80 USDT = 0.00021 BTC" behauptet allein der Server. Das ist die offene Vertrauensfrage des
Bauteils — der perfekte Aufhänger fürs Red-Team.

**„Ist `coffee@pay.example.swiss` (auf der Warm-up-Folie) echt erreichbar?"**
Nein, Platzhalter aus dem Deck. Im Lab läuft alles lokal gegen `127.0.0.1:8088`.

---

## 5. Troubleshooting (was wahrscheinlich schiefgeht)

- **Warm-up-Wallet lädt nicht / Zahlung hängt:** Nicht kämpfen. Muss nur **einmal pro Paar**
  klappen; Rest braucht weder Wallet noch Internet. Bei WLAN-Ausfall geht LNbits auch über Mobilfunk.
- **`python3` nicht gefunden:** Auf manchen Macs heißt es nur `python`. Version ≥ 3.6 reicht.
- **`curl` fehlt (selten):** Jeder `curl` ist nur ein GET — `python3 -m urllib.request <url>` tut's auch.
- **Port 8088 belegt:** Alter Merchant läuft noch → `Ctrl-C` im richtigen Terminal, oder Prozess killen.
- **„ATTACK DETECTED" erscheint:** Das ist **kein Fehler**, sondern das erwartete Ergebnis in den
  `--spoof`-Modi. Der Client hat die Lüge korrekt erkannt.
- **Merchant-Moduswechsel:** Vor jedem `--spoof`/`--ocp` den laufenden Merchant mit `Ctrl-C` stoppen,
  sonst bleibt der alte Modus aktiv.

---

## 6. Drei Sätze, mit denen du Stärke zeigst

- „Scannen heißt einen GET machen — das Bitcoin kommt erst in der letzten Antwort."
- „Der Schutz steht im Protokoll, ausführen muss ihn deine Wallet — die Chain garantiert hier nichts."
- „Der Hash bindet, *was* du kaufst. Bei OCP bindet nichts den *Kurs* — das ist die eigentliche Frage."

**Specs zum Nachschlagen:** LUD-06 (payRequest/Bindung) · LUD-09 (successAction) · LUD-16
(Lightning Address) — github.com/lnurl/luds
