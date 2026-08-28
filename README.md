# Scotland Tree Service — Website

Static site for **Scotland Tree Service**, Scotland, Ontario. No framework, no build server, no
monthly hosting bill.

```
Scotland-Tree-Trimming-Website-Content.md   <- every word on the site (source of truth)
build.py                                <- turns that markdown into site/
wrangler.toml                           <- Cloudflare Pages / Workers config
google-apps-script.gs                   <- lead handler for the contact form
site/                                   <- generated output; THIS is what deploys
site/style.css, site/script.js          <- hand-written, NOT generated
tools/                                  <- logo pipeline and verification
*.png                                   <- master photos (on disk, NOT tracked)
```

Read `HANDOVER.md` first — it has the go-live sequence and the measured numbers.

---

## Layout variant

This town runs `HEADER_VARIANT = "compact"` and `HERO_VARIANT = "band-above"`, set near the
top of `build.py`. Six towns in one county is a tight cluster, so the markup
differs between them as well as the palette, the photographs and the words -
the header structure and the home-page hero are different layouts, not the same
layout recoloured. `site/style.css` ends with the rules for these two variants
and carries no rules for the other ten.

## The one rule

`build.py` regenerates every HTML file in `site/`. **Never hand-edit anything in
`site/` except `style.css` and `script.js`** — everything else is overwritten on
the next build.

---

## Making changes

**Copy** — edit `Scotland-Tree-Trimming-Website-Content.md`, then `python build.py`.

**CSS or JS** — edit `site/style.css` or `site/script.js`, then run
`python build.py` anyway. Every page carries a content hash of both files for
cache-busting, and without a rebuild your change never reaches a returning
visitor.

**Photos** — drop the new file in the project root, update `PAGE_PHOTOS` or
`GALLERY_PHOTOS` near the top of `build.py`, then `python build.py --images`.
That re-derives every crop and every size. It takes a minute or two.

**Logo** — `python tools/make-logo.py`, then `python build.py` to refresh the
cache fingerprints.

---

## Deploying

The repo is set up for Cloudflare. The worker name is `scotlandtreetrimming` and the
canonical host is `www.scotlandtreetrimming.com`.

Only `site/` is served. The master photos, the markdown and `build.py` stay in
the repo but never reach a visitor.

---

## The contact form

`site/script.js` has a `SHEET_ENDPOINT` constant at the top. Until you paste a
real Google Apps Script `/exec` URL into it, the form validates and shows its
success message but delivers nothing. `google-apps-script.gs` in this repo is
the receiving end — its header comment has the six-step setup.

**Do not attach the domain until the form has been tested end to end.**

---

## Verifying a build

```
python tools/verify.py
```

Checks internal links, image references, heading structure, duplicate ids, alt
text, and meta description length and uniqueness.
