# Scotland Tree Service — Handover

Site for **Scotland Tree Service**, Scotland, Ontario. Phone (226) 546-3840. Domain `www.scotlandtreetrimming.com`.

## What was built

15 pages generated from one markdown file: home, a services index, seven
service pages, about, contact, FAQ, privacy, terms and a 404.

| Service page | Slug |
|---|---|
| Tree Trimming and Pruning | `/tree-trimming-and-pruning` |
| Dead Branch Removal | `/dead-branch-removal` |
| Emergency Storm Damage Cleanup | `/emergency-storm-damage-cleanup` |
| Tree Removal | `/tree-removal` |
| Crown Thinning and Canopy Reduction | `/crown-thinning-and-canopy-reduction` |
| Tree Cabling and Bracing | `/tree-cabling-and-bracing` |
| Stump Grinding and Removal | `/stump-grinding-and-removal` |

## Measured, not asserted

| Check | Result |
|---|---|
| Words of body copy | 16,168 |
| Head-term density, site-wide | 4.03% (target 4.0%) |
| Verbatim overlap with the five sibling city sites | 1.50%–2.89% (6-word runs, paragraph text) |
| Certification / accreditation claims | 0 |
| Colour-contrast failures | 0 of 27 computed ratios |
| Dead internal links | 0 |
| Missing images | 0 |
| Duplicate meta descriptions | 0 |
| Initial page weight (home) | 272 KB |

Re-run any of it with `python tools/verify.py` in this repo, or the auditor in
the build folder.

## Credentials language — deliberate

The copy uses **arborist** as an occupational word and **fully insured** as a
factual statement. It does not claim certification, accreditation, ISA or TCIA
membership, WSIB standing, or any standards number, because none was
substantiated. The auditor greps for all of those and must report zero before
anything ships. If real credentials are obtained later, add them to the copy
and relax the corresponding grep — not the other way round.

## Go-live sequence

1. **Push the repo private.** `build.py` and `google-apps-script.gs` carry the
   owner's email address.
2. **Set up the Apps Script.** Follow the header comment in
   `google-apps-script.gs`. Deploy as a web app, execute as *Me*, access
   *Anyone*. Copy the `/exec` URL.
3. **Paste that URL** into `SHEET_ENDPOINT` at the top of `site/script.js`.
   Confirm it is this city's own URL and not another city's — each site needs
   its own endpoint or the leads land in the wrong sheet.
4. **Run `python build.py`** so the cache fingerprints pick up the changed
   `script.js`.
5. **Deploy to Cloudflare** and test the form on the temporary
   `*.workers.dev` URL. Submit a real test lead and confirm the row appears.
6. **Only then attach `www.scotlandtreetrimming.com`.**

## Things worth knowing

- `html_handling = "auto-trailing-slash"` is set in `wrangler.toml`, and all
  internal links are extensionless. Do not change one without the other.
- The sitemap lists 12 URLs. Privacy, terms and 404 are excluded on purpose and
  carry `noindex`.
- Privacy and terms sit below the head-term density target. They are boilerplate
  legal pages carrying `noindex`, so their density does not matter.
- Every page URL carries an MD5 fingerprint of `style.css` and `script.js`. If
  you edit either file without rebuilding, returning visitors keep the old one.
