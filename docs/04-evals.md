# Evals: Conversion Teardown

## Eval set
18 real pages, German versions, captured Nov 2, 2026: 5 sites (Zalando, dm, Kleinanzeigen, Lieferando, MediaMarkt) × homepage and product page × desktop and mobile. Zalando mobile (E02, E04) was not captured, so 9 homepages and 9 product pages; 10 desktop and 8 mobile. For Lieferando the "product page" is a restaurant menu.
File: `evals/eval-set.csv`. Screenshots in `evals/screenshots/` named `E01.png` etc. (kept local: third-party content, not committed).

## How to label (before running the model)
1. Write down the issues you see (`human_issues`, separated by `;`).
2. Pick the 3 most important ones → `must_find_top3`.
This is the "ground truth". Labeller: Prashant (PM). If a second person joins, they label independently first, then you agree the top 3: that's how real eval teams reduce bias.

## How to score each model output
- `must_find_hits`: how many of the top 3 the model found (0–3). Judge by meaning, not exact words.
- `hallucinated_count`: issues that are not visible in the screenshot.
- `pass` = Y if must_find_hits ≥ 2 AND hallucinated_count = 0.

## Metrics and pass bar
| Metric | Definition | Pass bar |
|---|---|---|
| Must-find recall | sum(must_find_hits) / 54 (total must-finds) | ≥ 70% |
| Hallucination rate | hallucinated issues / all issues returned | ≤ 10% |
| Pass rate | rows with pass = Y / 18 | ≥ 70% |

## Results log
| Date | Prompt / model | Recall | Hallucination | Pass rate | Notes |
|---|---|---|---|---|---|
| Nov 15, 2026 | v1 / gemini-3.6-flash, viewport tiles | 35% (19/54) | 2.4% (2/83) | 33% (6/18) | Below the recall and pass bars. Fast: 12–18 s per page, 4–38 tiles. Hits PM-written must-finds 19% (7/36) vs Claude-suggested 67% (12/18). Model leans to CTA styling and trust/payment badges; PM leans to space use above the fold. Details: `evals/results/v1/scoring-v1.md` (scores reviewed by PM, Nov 15). |
| Nov 15, 2026 | v2 / gemini-3.6-flash, viewport tiles | not scored | – | – | Partial run: 4 of 18 pages (E01, E03, E05, E18) before the free-tier daily request quota ran out. Prompt: `prompts/v2-teardown.md`. Finish with `run_teardown.py all --prompt v2 --skip-existing`. |

## Status
**Paused Nov 24, 2026.** PM moved to P2 JobPilot. Next step when resumed: finish the v2 run, score it like v1, then P1-05 (ADR) onward. P1 issues stay open.
