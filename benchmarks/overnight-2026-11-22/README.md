# Overnight paired-opening matches

Status: **running**. Last updated (UTC): 2026-11-22T16:56:41+00:00.

Each row is a separate head-to-head comparison; score is from the first engine's perspective.
Each batch uses five fixed six-ply openings, played twice with colors swapped. The 25-opening
set is traversed twice for a target of 100 games per matchup. Results are stochastic.

Time control: **30 seconds plus 0.2 seconds per move**, 1,000 ms Cute Chess time margin,
one game at a time, 200-full-move draw limit. The engine's own opening books remain enabled.
The matches use the same 25 openings; they do not sample all possible openings or opponents.

| Match | Wins–losses–draws | Games | Score | Records |
| --- | ---: | ---: | ---: | --- |
| CE6 vs CE5 | 20–10–10 | 40 | 62.50% | [ModemCE6-vs-ModemCE5/](ModemCE6-vs-ModemCE5/) |
| CE9 vs CE8 | 18–6–16 | 40 | 65.00% | [ModemCE9-vs-ModemCE8/](ModemCE9-vs-ModemCE8/) |
| CE12 vs CE5 | 37–0–3 | 40 | 96.25% | [ModemCE12-vs-ModemCE5/](ModemCE12-vs-ModemCE5/) |
| CE12 vs CE9 | 12–10–18 | 40 | 52.50% | [ModemCE12-vs-ModemCE9/](ModemCE12-vs-ModemCE9/) |
| CE12 vs CE11 | 11–16–13 | 40 | 43.75% | [ModemCE12-vs-ModemCE11/](ModemCE12-vs-ModemCE11/) |

Individual batch PGNs and logs are in the linked folders. [settings.json](settings.json)
records binary and opening hashes; [status.json](status.json) records progress and errors.
The earlier 3+0.03-second results are in [the extended report](../2026-11-22-extended/README.md).
