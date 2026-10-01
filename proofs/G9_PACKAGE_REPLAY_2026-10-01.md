# G9 Package Replay — Corrective on V5, target V5.1 — 2026-10-01

Materialized per `authority/METHODOLOGIE_DEV_YGO_V1.md` §8 ("les packages
doivent être testés comme produits livrés") and
`governance/PRE_GO_CORRECTIVE_ON_V5_V2.md` §3 G9 items 9-12.

## Package

Flat Sources zip of exactly the 6 product modules under `worktree/source/`:
`api.py card_data.py compiler.py contracts.py runtime.py validator.py`.

- Package: `YGO_V5_1_CORRECTIVE_SOURCES.zip`
- SHA-256: `8aeaff09e826ccf84b5a722c777b95d5bb00c819d9fa0b7735042c92dfaf1fe6`
- Built with `zip -q -X` from inside `worktree/source` (no absolute paths,
  no extra metadata).

## Clean extraction

Extracted into a directory with no prior relationship to `worktree/source`.
Per-file SHA-256 compared against `worktree/source`: all 6 files matched
byte-for-byte.

## Replay on packaged bytes

The full `tests/test_g1_*.py` .. `tests/test_g8_*.py` suite (62 tests) was
re-run with `YGO_SOURCE_OVERRIDE` pointed at the extracted directory
instead of `worktree/source` (see `tests/_bootstrap.py`), so every `import
contracts/card_data/compiler/validator/runtime/api` statement actually
resolved against the packaged-and-extracted bytes, not the working tree.

Result: **62/62 PASS**, identical to the non-packaged run.

## Live external card-resolution route

`card_data.YGOPRODeckProvider.fetch_exact("Dark Magician")` against the
real `db.ygoprodeck.com` endpoint succeeded from this environment:
canonical_name=`Dark Magician`, card_type=`Normal Monster`, level=`7`,
provider=`YGOPRODeck-v7`.

A `CardDataService` configured with `routes=[<simulated-down>,
YGOPRODeckProvider()]` also succeeded, falling back from the simulated
outage to the real live route — direct material evidence for REQ-CR-025 /
RED-PROVIDER-FALLBACK beyond the mocked unit tests in
`tests/test_g2_card_facts_resolver.py`.

## Scope note

This proof covers package/replay/live-route items of the G9 checklist
only. It does not by itself constitute a full G9 PASS — see
`governance/TEST_PROOF_MATRIX_CORRECTIVE_ON_V5_V2.md` "G9 — EXECUTED" for
the complete, honest checklist (mutation coverage, V4 differential,
coverage %, V5 parent guard replay, and Black-Box remain partial or
explicitly deferred).
