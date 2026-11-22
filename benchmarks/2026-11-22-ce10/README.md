# ModemCE10 vs ModemCE9 — 22 November 2026

CE10 scored 17 wins, 14 losses and 9 draws (53.75%) in 40 games. The match used
the same settings as the [extended matches](../2026-11-22-extended/README.md):
3 seconds plus 0.03 seconds per move, 20 games per color, one game at a time,
a 1,000 ms time margin, and a 200-full-move draw limit. The engines picked their
own random opening moves, so the openings were not paired.

[PGN games](ModemCE10-vs-ModemCE9.pgn) · [Match log](ModemCE10-vs-ModemCE9.log) ·
[Settings and binary hashes](metadata.json) · [Evaluation speed sample](evaluation-speed.json)

For a separate single-run microbenchmark, CE9 and CE10 evaluated three fixed
positions 3,000 times each. They returned the same scores; CE9 took 0.289 s and
CE10 took 0.185 s on this machine, about 36% less time for this sample. The
microbenchmark is small, and its timing does not establish a general playing
strength improvement. Run `python benchmarks/compare_evaluation.py` to repeat it.
