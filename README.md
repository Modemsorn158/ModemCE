# Modem Chess Engine

ModemCE4 is a UCI chess engine for CuteChess. It chooses a random legal move
from its opening book when the current position is present. Outside the book,
it uses iterative deepening and alpha-beta minimax until its time budget is
exhausted. The last fully searched depth determines the move; simpler positions
can reach greater depths. The evaluation counts material and recognizes
checkmate and automatic draws; equally scored moves are chosen randomly. Book
choices are uniform among distinct moves and are not evaluated for strength.

The engine uses UCI clocks, increments, moves-to-go, and movetime to set a
per-move budget with time in reserve. It also accepts `go depth N`,
`go infinite`, and `stop`; without a limit it searches for half a second.
During search it reports completed depths with UCI `info` messages. Clock-based
searches are capped at 10% of the remaining time for a move.

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
python -m PyInstaller --onefile --name ModemCE4 --add-data "data/opening_book.json;data" main.py
```

Select `dist/ModemCE4.exe` as a UCI engine in CuteChess. The book is embedded,
so the executable can be copied on its own. Earlier executables remain separate.
