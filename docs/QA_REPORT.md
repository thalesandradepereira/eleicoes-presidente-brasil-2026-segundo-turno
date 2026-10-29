# QA Report · TAP TSE 2026 · Release candidate 1

**Date:** 2026-10-29 (America/Sao_Paulo)  
**Version:** `v1.0.0-rc.1`  
**Release status:** **Candidate validated locally; PUBLIC SITE NOT DEPLOYED**  
**Reason:** the GitHub API returned `HTTP 422: Your current plan does not support GitHub Pages for this repository.` The repository must remain **private**.

## Acceptance matrix

| Check | Evidence | Result |
|---|---|---|
| Repository access | Owner `thalesandradepereira`; `visibility=PRIVATE`; main branch | PASS |
| Data integrity | SHA-256 of packaged HTML and embedded compressed payload | PASS |
| 499,205 ballot records | Automated `unittest`, exact row count | PASS |
| National results | Lula 64,256,232; Flávio 59,826,041; blank 1,430,496; null 2,723,305 | PASS |
| Overseas, 99 countries | 1,308 records and four vote-category totals checked | PASS |
| Brazilian ballot closing cutoff | 17:15:00 Brasília inclusive; 488,813 records with expected totals | PASS |
| Per-UF data reconciliation | 27 states × 5 categories × 2 views = **270 assertions** | PASS |
| Maps / filters / language | Real Chromium browser on user-authorized Mac; PT-BR, EN-US, countries, 17:16 | PASS |
| Mobile rendering | Chromium viewport 390 px, no horizontal overflow | PASS |
| Official source | Official TSE data URL shown at top of HTML and in README | PASS |
| Pages enablement | Explicit GitHub Pages creation API returned 422 due plan | **BLOCKED** |
| Public URL & HTTPS | Cannot test until Pages is enabled | **NOT VERIFIED** |
| Public site smoke test | No deployed Pages website | **NOT VERIFIED** |

## Reconciliation details

```
National totals (Brazil + Overseas ZZ)
  Lula          64,256,232
  Flávio        59,826,041
  Blank          1,430,496
  Null           2,723,305

Brazilian ballot boxes closed by 17:15:00 Brasília
  Boxes            488,813
  Lula          62,657,589
  Flávio        58,545,934
  Blank          1,396,695
  Null           2,654,428

Overseas, final
  Records            1,308
  Lula             200,154
  Flávio           171,497
  Blank              4,675
  Null               5,117
```

## Methodological notes

- The timeline uses ballot-box **closing time** (`DT_ENCERRAMENTO`), not ballot arrival, counting, publication or results availability.
- The 99-country view uses an auxiliary place-to-country mapping; electoral vote numbers remain those of TSE.
- Official results report 499,248 **counted polling sections**, while the BWEB rows aggregated here number 499,205. Difference = 43 sections. **No causal attribution is asserted.**
- Public GitHub Pages publishing from private repositories requires an eligible GitHub plan. This condition cannot be bypassed without violating the requested privacy.

## Verification workflow

```sh
python3 -m unittest discover -s tests -v
git status --porcelain
gh repo view thalesandradepereira/tap-tse-2026-auditoria --json isPrivate
gh run list --repo thalesandradepereira/tap-tse-2026-auditoria
```

Before a production release, enable eligible private-repo Pages, set `ENABLE_GITHUB_PAGES=true`, confirm GitHub Actions succeeds, verify the HTTPS endpoint independently and test the deployed controls.

**No public URL may be claimed until a live HTTP response and browser-level smoke test have been observed.**
