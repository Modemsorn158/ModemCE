# Preliminary head-to-head matches — 22 November 2026

Each newer engine played its predecessor eight times, four games as each color.
All games began from the normal starting position, with each engine choosing its
own moves and opening lines. The openings were not paired or fixed in advance.
The engines use random choices, and time-limited search depends on the machine;
reruns will not reproduce the exact games.

Cute Chess CLI 1.5.1 ran one game at a time with 3 seconds per player plus a
0.03-second increment, a 1,000 ms Cute Chess time margin, and a draw after 200
full moves. See [metadata.json](metadata.json) for the machine and exact binary
hashes. Each log records the command, per-game result and Cute Chess statistics;
paths beginning `<PROJECT>` are relative to the project root.

| Newer vs older | Wins | Losses | Draws | Score | Games | Log |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| CE2 vs CE1 | 0 | 4 | 4 | 25% | [PGN](ModemCE2-vs-ModemCE1.pgn) | [Log](ModemCE2-vs-ModemCE1.log) |
| CE3 vs CE2 | 8 | 0 | 0 | 100% | [PGN](ModemCE3-vs-ModemCE2.pgn) | [Log](ModemCE3-vs-ModemCE2.log) |
| CE4 vs CE3 | 4 | 2 | 2 | 62.5% | [PGN](ModemCE4-vs-ModemCE3.pgn) | [Log](ModemCE4-vs-ModemCE3.log) |
| CE5 vs CE4 | 4 | 3 | 1 | 56.25% | [PGN](ModemCE5-vs-ModemCE4.pgn) | [Log](ModemCE5-vs-ModemCE4.log) |

The very small samples give a noisy picture; in particular, an 8–0 result is
not evidence of an infinite Elo difference. These are separate head-to-head
scores, not a common rating scale.

## Fixed-depth move-ordering comparison

[ordering-comparison.json](ordering-comparison.json) records a three-ply
alpha-beta search of three fixed positions using CE4 source from commit
`14f08fb` and CE5 source from commit `07bb2e1`. The scores are identical; the
respective CE4/CE5 leaf evaluation counts are 509/509, 2,714/1,513, and
565/565. Timings are single runs and fluctuate. This microbenchmark measures
the recursive search, not opening-book play or full games, and does not prove
the ordering is faster for all positions.
