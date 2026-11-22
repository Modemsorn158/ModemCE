# Modem Chess Engine

ModemCE10 is a UCI chess engine for CuteChess. It chooses a random legal move
from its opening book when the current position is present. Outside the book,
it uses iterative deepening and alpha-beta minimax until its time budget is
exhausted. The last fully searched depth determines the move; simpler positions
can reach greater depths. The evaluation counts material and recognizes
checkmate and automatic draws, with modest positional bonuses; equally scored
moves are chosen randomly. Book
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
| ModemCE6 | Positional evaluation rewards pawn advancement and piece centralization. |
| ModemCE7 | Quiescence search extends forcing moves at the search horizon. |
| ModemCE8 | King evaluation encourages safety early and activity in the endgame. |
| ModemCE9 | Carries alpha-beta bounds across root moves, rechecking potential ties. |
| ModemCE10 | Precomputes positional scores to reduce evaluation overhead without changing the formula. |

ModemCE4 already introduced alpha-beta pruning. ModemCE5 improves its move
ordering; it does not introduce pruning for the first time.
ModemCE7 extends captures, promotions and check evasions at the search horizon
up to six extra plies, to reduce premature evaluations during tactics.

## Preliminary match results

Score is from the newer engine's perspective: one point for a win, half for a
draw. Each row is a separate head-to-head match, not an overall rating.

| Match | Wins–losses–draws | Score | Score chart |
| --- | ---: | ---: | --- |
| CE2 vs CE1 | 6–8–26 | 47.50% | ██████████░░░░░░░░░░ |
| CE3 vs CE2 | 39–0–1 | 98.75% | ████████████████████ |
| CE4 vs CE3 | 16–14–10 | 52.50% | ███████████░░░░░░░░░ |
| CE5 vs CE4 | 8–16–16 | 40.00% | ████████░░░░░░░░░░░░ |
| CE6 vs CE5 | 3–24–13 | 23.75% | █████░░░░░░░░░░░░░░░ |
| CE7 vs CE6 | 20–12–8 | 60.00% | ████████████░░░░░░░░ |
| CE8 vs CE7 | 15–19–6 | 45.00% | █████████░░░░░░░░░░░ |

Bars round to the nearest 5%. These are only 40 games per matchup, so the
results remain uncertain and are not proof of a general strength improvement.
CE6 in particular scored poorly against CE5 at this time control.
Games used Cute Chess CLI 1.5.1, 3 seconds plus 0.03 seconds per move, 20
games per color, one game at a time, a 1-second time margin, and a 200-full-move
draw limit. Games start from the normal position with each engine's own random
choices; the two colors do not replay identical opening lines.

[Game records, logs, settings and binary hashes](benchmarks/2026-11-22-extended/README.md)
are available for inspection, as are the [earlier eight-game pilot and fixed-depth search comparison](benchmarks/2026-11-22-3s/README.md).
The fixed-depth comparison found identical
evaluations in three test positions; in one tactical position CE5 evaluated
1,513 leaves versus CE4's 2,714. That small position sample does not guarantee
an efficiency improvement in every position.

### Run the matches again

Download the [official Cute Chess 1.5.1 Windows zip](https://github.com/cutechess/cutechess/releases/tag/v1.5.1)
and extract it under `tools/cutechess-1.5.1`, or specify the CLI path with
`--cli`. Put the versioned executables in `dist/` (they are not tracked in
Git), install `requirements.txt`, then run:

```powershell
python benchmarks/run_matches.py --output benchmarks/my-run
```

Use `--rounds 50` for 100 games per matchup, for example. Use `--first-version`
and `--last-version` to select a subset of consecutive matchups. Match outcomes and
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
python -m PyInstaller --onefile --name ModemCE10 --add-data "data/opening_book.json;data" main.py
```

Select `dist/ModemCE10.exe` as a UCI engine in CuteChess. The book is embedded,
so the executable can be copied on its own. Earlier executables remain separate.
