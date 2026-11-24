# Scoring: prompt v1, gemini-3.6-flash (P1-04)

Scores by Claude, Nov 15, 2026, reviewed by PM the same day. Three borderline calls were changed from miss to hit by the PM (marked *PM*). A hit = a friction point that clearly means the same as the must-find. Hallucinated = a claim that is false or not in the screenshot.

| ID | Site | Must-finds hit | Hallucinated | Pass |
|---|---|---|---|---|
| E01 | Zalando homepage desktop | 2/3 (MF1 ← F1; MF3 ← F4 *PM*) | 0 | Y |
| E03 | Zalando product desktop | 1/3 (MF1 ← F1) | 0 | N |
| E05 | dm homepage desktop | 2/3 (MF1 ← F1; MF3 ← F3+F4) | 0 | Y |
| E06 | dm homepage mobile | 0/3 (none) | 0 | N |
| E07 | dm product desktop | 0/3 (none) | 0 | N |
| E08 | dm product mobile | 1/3 (MF3 ← F2) | 0 | N |
| E09 | Kleinanzeigen homepage desktop | 2/3 (MF2 ← F1; MF3 ← F2) | 0 | Y |
| E10 | Kleinanzeigen homepage mobile | 2/3 (MF2 ← F1; MF3 ← F3+F4) | 0 | Y |
| E11 | Kleinanzeigen product desktop | 2/3 (MF2 ← F2; MF3 ← F3 *PM*) | 0 | Y |
| E12 | Kleinanzeigen product mobile | 3/3 (MF1 ← F1; MF2 ← F1; MF3 ← F4) | 0 | Y |
| E13 | Lieferando homepage desktop | 1/3 (MF1 ← F3 *PM*) | F5: calls '© 2026' a future year; it is the current year | N |
| E14 | Lieferando homepage mobile | 0/3 (none) | 0 | N |
| E15 | Lieferando product desktop | 1/3 (MF3 ← F3) | 0 | N |
| E16 | Lieferando product mobile | 1/3 (MF3 ← F5) | 0 | N |
| E17 | MediaMarkt homepage desktop | 0/3 (none) | 0 | N |
| E18 | MediaMarkt homepage mobile | 0/3 (none) | F1: calls iPhone 18 Pro and GTA VI fake/unreleased products (model knowledge cutoff) | N |
| E19 | MediaMarkt product desktop | 1/3 (MF3 ← F1) | 0 | N |
| E20 | MediaMarkt product mobile | 0/3 (none) | 0 | N |

**Totals:** recall 19/54 = 35% · hallucination 2/83 = 2.4% · pass 6/18 = 33%

**By who wrote the must-find:** PM-written 7/36 = 19% · Claude-suggested 12/18 = 67%

MF numbers refer to the order in `must_find_top3`; F numbers to `friction_points` in `evals/results/v1/<id>.gemini-3.6-flash.json`.

Strict scoring (before PM review) was recall 16/54 = 30%, pass 4/18 = 22%. Either way v1 is below the bar.
