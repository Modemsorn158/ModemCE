# Modem Chess Engine

ModemCE5 is a UCI chess engine for CuteChess. It chooses a random legal move
from its opening book when the current position is present. Outside the book,
it uses iterative deepening and alpha-beta minimax until its time budget is
exhausted. The last fully searched depth determines the move; simpler positions
can reach greater depths. The evaluation counts material and recognizes
checkmate and automatic draws; equally scored moves are chosen randomly. Book
choices are uniform among distinct moves and are not evaluated for strength.
ModemCE5 orders captures by the value of the victim and attacker, and also
prioritizes promotions, to help alpha-beta pruning find cutoffs earlier.

The engine uses UCI clocks, increments, moves-to-go, and movetime to set a
per-move budget with time in reserve. It also accepts `go depth N`,
`go infinite`, and `stop`; without a limit it searches for half a second.
During search it reports completed depths with UCI `info` messages. Clock-based
searches are capped at 10% of the remaining time for a move.

## Versions

| Version | Feature introduced |
| --- | --- |
| ModemCE1 | Random legal moves. |
| ModemCE2 | Lichess opening book; random legal moves outside the book. |
| ModemCE3 | Material evaluation and two-ply minimax outside the book. |
| ModemCE4 | Time-aware iterative deepening and alpha-beta pruning. |
| ModemCE5 | Improved capture and promotion ordering for the existing alpha-beta search. |

ModemCE4 already introduced alpha-beta pruning. ModemCE5 improves its move
ordering; it does not introduce pruning for the first time.

## Preliminary match results

Score is from the newer engine's perspective: one point for a win, half for a
draw. Each row is a separate head-to-head match, not an overall rating.

| Match | Wins–losses–draws | Score | Score chart |
| --- | ---: | ---: | --- |
| CE2 vs CE1 | 0–4–4 | 25% | █████░░░░░░░░░░░░░░░ |
| CE3 vs CE2 | 8–0–0 | 100% | ████████████████████ |
| CE4 vs CE3 | 4–2–2 | 62.5% | ████████████▌░░░░░░░ |
| CE5 vs CE4 | 4–3–1 | 56.25% | ███████████▎░░░░░░░░ |

These are only eight games per matchup, so the results are highly uncertain
and should not be treated as proof of a strength improvement. CE2's opening
book includes dubious lines, and the small sample scored worse than CE1.
Games used Cute Chess CLI 1.5.1, 3 seconds plus 0.03 seconds per move, four
games per color, one game at a time, a 1-second time margin, and a 200-full-move
draw limit. Games start from the normal position with each engine's own random
choices; the two colors do not replay identical opening lines.

[Game records, logs, settings, binary hashes, and a fixed-depth search comparison](benchmarks/2026-11-22-3s/README.md)
are available for inspection. The fixed-depth comparison found identical
evaluations in three test positions; in one tactical position CE5 evaluated
1,513 leaves versus CE4's 2,714. That small position sample does not guarantee
an efficiency improvement in every position.

### Run the matches again

Download the [official Cute Chess 1.5.1 Windows zip](https://github.com/cutechess/cutechess/releases/tag/v1.5.1)
and extract it under `tools/cutechess-1.5.1`, or specify the CLI path with
`--cli`. Put the five versioned executables in `dist/` (they are not tracked in
Git), install `requirements.txt`, then run:

```powershell
python benchmarks/run_matches.py --output benchmarks/my-run
```

Use `--rounds 50` for 100 games per matchup, for example. Match outcomes and
timing vary because the engines choose randomly and time-limited search depends
on the machine. `python benchmarks/compare_ordering.py` compares search leaf
counts against the ModemCE4 source at a fixed depth.

## Opening book

The bundled book is generated from the [Lichess chess-openings dataset](https://github.com/lichess-org/chess-openings),
commit `48a8c0e733facfdc9a3723fe882e51ec28014074`, released under CC0.
The source TSVs and license are in `data/openings`. Each position in each
listed opening line contributes its next move; transpositions are supported.
The dataset includes unusual and dubious named openings as well as mainstream
ones, so a book move is not necessarily a strong move.

Install dependencies with `python -m pip install -r requirements.txt`, then
regenerate the book with `python build_book.py` if the TSVs change.

## Build and run

Install PyInstaller (`python -m pip install pyinstaller`), then run:

```powershell
python -m PyInstaller --onefile --name ModemCE5 --add-data "data/opening_book.json;data" main.py
```

Select `dist/ModemCE5.exe` as a UCI engine in CuteChess. The book is embedded,
so the executable can be copied on its own. Earlier executables remain separate.
