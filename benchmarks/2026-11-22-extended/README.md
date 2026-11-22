# Extended head-to-head matches — 22 November 2026

Each matchup ran 40 games (20 with each engine playing White). Games started
from the normal position, but random opening choices were independent rather
than replayed as paired lines. Cute Chess CLI 1.5.1 ran one game at a time with
3 seconds per player plus 0.03 seconds per move, a 1,000 ms time margin and a
200-full-move draw limit. [Metadata](metadata.json) records the machine and
the executable hashes; the individual logs contain the commands and results.

| Newer vs older | Wins–losses–draws | Score | Records |
| --- | ---: | ---: | --- |
| CE2 vs CE1 | 6–8–26 | 47.50% | [PGN](ModemCE2-vs-ModemCE1.pgn) · [log](ModemCE2-vs-ModemCE1.log) |
| CE3 vs CE2 | 39–0–1 | 98.75% | [PGN](ModemCE3-vs-ModemCE2.pgn) · [log](ModemCE3-vs-ModemCE2.log) |
| CE4 vs CE3 | 16–14–10 | 52.50% | [PGN](ModemCE4-vs-ModemCE3.pgn) · [log](ModemCE4-vs-ModemCE3.log) |
| CE5 vs CE4 | 8–16–16 | 40.00% | [PGN](ModemCE5-vs-ModemCE4.pgn) · [log](ModemCE5-vs-ModemCE4.log) |
| CE6 vs CE5 | 3–24–13 | 23.75% | [PGN](ModemCE6-vs-ModemCE5.pgn) · [log](ModemCE6-vs-ModemCE5.log) |
| CE7 vs CE6 | 20–12–8 | 60.00% | [PGN](ModemCE7-vs-ModemCE6.pgn) · [log](ModemCE7-vs-ModemCE6.log) |
| CE8 vs CE7 | 15–19–6 | 45.00% | [PGN](ModemCE8-vs-ModemCE7.pgn) · [log](ModemCE8-vs-ModemCE7.log) |

Score is wins plus half the draws, divided by 40. Results remain noisy and are
specific to these clocks and the book; neither a single match nor Elo estimates
in logs prove a feature's general strength. The CE6 result is a substantial
regression in this sample. Search-depth annotations in the CE6–CE5 PGN average
2.15 and 2.16 plies respectively across annotated moves; these values come from
different positions, so they cannot alone explain the result.

Regenerate the summary with `python benchmarks/summarize.py benchmarks/2026-11-22-extended`.
