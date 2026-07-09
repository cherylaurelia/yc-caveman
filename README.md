# A Caveman's Guide to YC Startups

A single-file website that explains every YC startup in simple caveman words —
for people who don't speak tech/business jargon.

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
