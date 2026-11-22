# Overnight paired-opening matches

Status: **running**. Last updated (UTC): 2026-11-22T14:24:02+00:00.

Each row is a separate head-to-head comparison; score is from the first engine's perspective.
Each batch uses five fixed six-ply openings, played twice with colors swapped. The 25-opening
set is traversed twice for a target of 100 games per matchup. Results are stochastic.

Time control: **30 seconds plus 0.2 seconds per move**, 1,000 ms Cute Chess time margin,
one game at a time, 200-full-move draw limit. The engine's own opening books remain enabled.
The matches use the same 25 openings; they do not sample all possible openings or opponents.

| Match | Wins–losses–draws | Games | Score | Records |
| --- | ---: | ---: | ---: | --- |
| CE6 vs CE5 | 3–2–5 | 10 | 55.00% | [ModemCE6-vs-ModemCE5/](ModemCE6-vs-ModemCE5/) |
| CE9 vs CE8 | 4–2–4 | 10 | 60.00% | [ModemCE9-vs-ModemCE8/](ModemCE9-vs-ModemCE8/) |
| CE12 vs CE5 | 10–0–0 | 10 | 100.00% | [ModemCE12-vs-ModemCE5/](ModemCE12-vs-ModemCE5/) |
| CE12 vs CE9 | 3–2–5 | 10 | 55.00% | [ModemCE12-vs-ModemCE9/](ModemCE12-vs-ModemCE9/) |
| CE12 vs CE11 | 0–5–5 | 10 | 25.00% | [ModemCE12-vs-ModemCE11/](ModemCE12-vs-ModemCE11/) |

Individual batch PGNs and logs are in the linked folders. [settings.json](settings.json)
records binary and opening hashes; [status.json](status.json) records progress and errors.
The earlier 3+0.03-second results are in [the extended report](../2026-11-22-extended/README.md).
