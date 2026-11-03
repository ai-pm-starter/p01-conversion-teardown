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
| Must-find recall | sum(must_find_hits) / 54 | ≥ 70% |
| Hallucination rate | hallucinated issues / all issues returned | ≤ 10% |
| Pass rate | rows with pass = Y / 18 | ≥ 70% |

## Results log
| Date | Prompt / model | Recall | Hallucination | Pass rate | Notes |
|---|---|---|---|---|---|
| | v1 / | | | | |
