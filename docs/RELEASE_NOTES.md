# TAP TSE 2026 — v1.0.0-rc.1

**Private repository / Public site deployment pending GitHub Pages plan eligibility**

The candidate contains the self-contained, bilingual electoral audit website (`index.html`), a premium README, unit and data integrity tests, per-state expected totals, and a QA-gated GitHub Pages deployment workflow.

## Verified
- PT-BR / EN-US switching, Brazil map, overseas world map (99 countries), minute slider and cross-filters.
- 499,205 BWEB records; national votes exactly reconcile with official TSE data.
- 270 per-UF total and cutoff verifications, 5 local automated tests.
- E2E browser smoke checks: totals, France country filter, 17:16 cutoff and responsive layout.
- Privacy: repository is **private**; no secrets in the deployed HTML.

## Publishing gate
The repository owner's current plan **does not support GitHub Pages for a private repository** (GitHub API HTTP 422 on 2026-10-29). The workflow deliberately skips deployment until `ENABLE_GITHUB_PAGES=true` and the account is eligible. No live site or public URL is claimed by this release candidate.

See [QA report](docs/QA_REPORT.md) and [README](README.md).

**Official TSE source:** https://dadosabertos.tse.jus.br/dataset/resultados-2026-boletim-de-urna
