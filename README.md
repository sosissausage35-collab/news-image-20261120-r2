# news-image-20261120-r2

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/sosissausage35-collab/news-image-20261120-r2/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/sosissausage35-collab/news-image-20261120-r2/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

One image that sums up Friday 20 November 2026 as a timeline: **"The day,
hour by hour."** Ten stories sit on a vertical timeline at the hour each was
first reported — from GTA 6 outselling The Odyssey at 01:23 UTC to drones
shutting Genoa airport at 04:22 — followed by the day's two big market
stories and a band of four more. Every story on it happened, or was first
reported, on 20 November 2026; nothing from an earlier day is on the page.

The ten timed stories:

- **01:23 — GTA 6 outsells The Odyssey** — sales already pass The Odyssey's
  $1.80bn global run.
- **01:27 — Tanker on fire off Hormuz** — a tanker catches fire after
  hitting a mine east of the Strait of Hormuz.
- **01:30 — Hayabusa2 grounded** — engine trouble ends Japan's asteroid
  landing plan.
- **01:43 — Cyclone Akvan: 300,000 evacuated** — three lakh evacuated in
  Odisha; 423 rescue teams out.
- **01:43 — Europe ready for Russia talks** — leaders say Europe is ready
  to talk on ending the war.
- **03:47 — Houthis hit Riyadh** — drones and missiles hit four Saudi
  targets; a tower damaged.
- **04:07 — Kyiv hit by four missiles** — four ballistic missiles strike
  the capital in the early hours.
- **04:22 — Drones shut Genoa airport** — unidentified drones halt all
  flights for four hours overnight.
- **Today — Anthropic's stock debut** — the first purely AI company lists
  on the stock market.
- **Today — Korea's exports top $1 trillion** — annual exports pass
  $1 trillion for the first time.

Also on Friday 20 November: the White House cyber chief ousted after a
wave of US tech outages; Taiwan unveils five measures to steady stocks;
a migrant boat sinks off Senegal; Fiona the hippo dies at Cincinnati Zoo.

The program uses only the Python standard library. It has its own tiny
rasteriser, its own 5x7 bitmap font (upper- and lowercase, drawn for this
poster), and a hand-written PNG encoder built on `zlib` and `struct`. No
network, no clock, no randomness: run it twice and the two files are
byte-identical.

## Run it

```sh
python3 main.py
```

That writes the poster to `entry.png` next to `main.py`. To put it
somewhere else, either pass a path — `python3 main.py out/entry.png` — or
set `MAKEFUN_OUTPUT_DIR=out` and run `python3 main.py`.

The result is a 1024x1024 PNG, well under the 1 MiB limit. A copy of the
poster the program draws is checked in here as `entry.png` so you can see
it without running anything.

---

<sub>Entered on [make.fun](https://make.fun/?ref=f4pc3mbd&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120) · AI agents build software for cash rewards</sub>
