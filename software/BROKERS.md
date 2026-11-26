# Message services for boards in different places

Notes from 2026-11-26. The facts below were gathered by a research pass over each provider's own pages
on that day; I have not re-checked them, and free plans change. Nothing is chosen or built yet.

## What is needed

A few boards to a few dozen, in different homes, each sending a few tiny messages a minute at most
(`{"from": "abc", "what": "wave", "value": 0.7}`), grouped by a shared "herd" name. A web page should be
able to join the same herd. Messages are data only: a board never runs anything it receives.

Two facts shape the choice:

- The CircuitPython MQTT library (`adafruit_minimqtt`) speaks plain MQTT, with or without encryption,
  but not MQTT over WebSockets. A web page can only use WebSockets. So the service must offer both.
- Encryption (TLS) on the board costs memory. With 2 MB of PSRAM it should fit; it is not yet tried.

## The candidates

| Service | Account | Free limits | For the board | For a web page | Private? |
|---|---|---|---|---|---|
| flespi | Yes; a token per herd is possible (100 tokens) | 50 connections, 20,000 messages a minute; account deleted after 60 idle days; "testing and development" | MQTT 1883, 8883 | WebSockets 443 | Yes |
| EMQX Serverless | Yes | 1 million connection-minutes a month (about 23 always-on clients), 10 messages a second each; stopped after 30 idle days | MQTT 8883 only (encrypted) | WebSockets 8084 | Yes |
| Adafruit IO | Yes; one key for the whole account | 30 messages a minute for the whole account, 10 feeds | MQTT 1883, 8883; HTTP | WebSockets 443 | Yes |
| shiftr.io | Yes | Free instance runs only 6 hours a day; $7 a month otherwise | MQTT 1883, 8883 | WebSockets 443 | Yes |
| ntfy.sh | No: the topic name is the secret | 250 messages a day | HTTPS | HTTPS, server-sent events | By obscurity |
| Public test brokers (HiveMQ, Mosquitto, EMQX) | No | "Must not be used" for anything depended on | MQTT 1883 | WebSockets | No |
| Ably | Yes | 6 million messages a month, 500 connections | MQTT 8883 (limited) | Its own library, SSE | Yes |
| Cloudflare Workers + Durable Objects | Yes; the relay must be written | 100,000 requests a day | HTTPS (polling) | WebSockets | Yes |
| Own Mosquitto on a small server | Yours | About 2 to 6 euros a month | Anything | Anything | Yes |

## Recommendation

- **To try first: flespi.** Private, enough connections, plain MQTT on 1883 for the board (no
  encryption cost while experimenting) and WebSockets on 443 for a page, and one token per herd. The
  risk: the free plan is labelled for testing and development, its terms can change at 25 days'
  notice, and an idle account is deleted after 60 days.
- **To last: an own Mosquitto broker** on a small server behind a hostname the owner controls, so the
  boards never need re-pointing. Free plans come and go: HiveMQ's free serverless plan and
  Cloudflare's Pub/Sub have both left their providers' current pages. The cost is being the maintainer.
- Whichever is used, the boards should reach it through one setting (`settings.toml`), and the
  behaviour-facing calls (`dino.herd.send`, `dino.herd.messages`) should not show which it is.

## Not verified

- Whether HiveMQ still has a free serverless plan (a blog post from February 2026 describes one; the
  pricing page does not).
- Age rules in the terms of flespi, EMQX, shiftr, HiveMQ, Ably and PubNub: not read. ntfy requires
  users to be adults. This matters if children's boards connect under an adult's account: the account
  holder is the adult; check before relying on any of them.
- Adafruit IO's paid tier and terms (the pages did not load).
- Whether the board can hold an encrypted connection alongside its web page: needs the real board.

## Sources read

flespi: flespi.com/mqtt-broker, flespi.com/pricing, flespi.com/en/docs/restrictions.
EMQX: emqx.com/en/pricing, docs.emqx.com/en/cloud/latest/create/serverless.html and .../restriction.html.
Adafruit IO: io.adafruit.com/api/docs/mqtt.html, .../http.html. shiftr: shiftr.io/cloud,
shiftr.io/docs/broker/mqtt-interface. ntfy: docs.ntfy.sh/publish, .../subscribe/api, .../terms.
HiveMQ: hivemq.com/pricing, mqtt-dashboard.com. Mosquitto: test.mosquitto.org. Ably:
ably.com/docs/platform/pricing/free, ably.com/docs/protocols/mqtt. Cloudflare:
developers.cloudflare.com/durable-objects/platform/pricing, .../workers/platform/pricing.
MiniMQTT: docs.circuitpython.org/projects/minimqtt/en/latest/api.html.
