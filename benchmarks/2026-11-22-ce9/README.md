# ModemCE9 vs ModemCE8 — 22 November 2026

CE9 scored 37 wins, 2 losses and 1 draw (93.75%) across 40 games. As in the
[other extended matches](../2026-11-22-extended/README.md), the time control
was 3 seconds plus 0.03 seconds per move, with 20 games per color, one game at a
time, a 1,000 ms time margin, and a 200-full-move draw limit. The engines chose
their own random opening moves, so openings were not paired.

[PGN games](ModemCE9-vs-ModemCE8.pgn) · [Match log](ModemCE9-vs-ModemCE8.log) ·
[Settings and binary hashes](metadata.json) · [Depth-annotation counts](depth-annotations.json)

In these games, 262 of CE8's 1,189 out-of-book moves had no depth annotation,
versus 38 of CE9's 1,202. Book positions were identified by the bundled book
and depth annotations by Cute Chess's PGN comments. Missing annotations can
indicate that no full iteration was reported before the engine moved, but the
counts do not by themselves establish why the match score changed. At fixed
depth two, the two versions returned identical completed search scores for
eight sampled positions from these games.

Recount the annotations with `python benchmarks/analyze_depth.py benchmarks/2026-11-22-ce9/ModemCE9-vs-ModemCE8.pgn`.
