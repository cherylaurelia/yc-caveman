# A Caveman's Guide to YC Startups

A single-file website that explains every YC startup in simple caveman words —
for people who don't speak tech/business jargon.

**To use it: just open `index.html` in any browser.** No server, no install. Works offline
(company logos and founder photos need internet the first time; founder photos live in `avatars/`).

## What's inside

- **All 6,020 launched YC companies** (from the public [yc-oss API](https://github.com/yc-oss/api),
  a daily-updated mirror of the official YC directory — snapshot July 2026).
- **Filters**: category (B2B, Fintech, Healthcare, Government, …), batch (all 50 seasons,
  with quick links to the newest ones), search, sort. In caveman mode batches become
  seasons (Winter 2012 → cold season 2012).
- **Caveman / Original toggle** — auto-translates all one-liner descriptions using
  ~230 jargon-to-simple-words rules (`src/jargon.json`).
- **55 hand-written "full story" profiles** for famous companies — Airbnb, Stripe,
  DoorDash, Zepto, GovDash, VotingWorks… — each with founders + X/Twitter links and four
  smoke signals: product, founder, competition, market opportunity.
- **Dictionary tab** — 84 startup/tech terms, each with a caveman meaning and the real one.

## Files

```
index.html             <- the whole website (open this)
avatars/               <- founder photos (downloaded locally)
build.py               <- assembles index.html from src/
fetch_data.py          <- re-downloads fresh YC company data
fetch_all_founders.py  <- re-scrapes founders + photos for all companies (resumable)
fetch_founders.py      <- founders for the 55 hand-written profiles only
src/                   <- template, datasets, stories, dictionary, jargon rules
```

## Updating

```sh
python3 fetch_data.py          # grab latest YC directory
python3 fetch_all_founders.py  # refresh founders + photos (takes a while)
python3 build.py               # rebuild index.html
```

To edit stories/dictionary/translations, change the files in `src/` and re-run `build.py`.
