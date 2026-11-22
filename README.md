# Modem Chess Engine

ModemCE2 is a UCI chess engine for CuteChess. It chooses a random legal move
from its opening book when the current position is present, and otherwise
chooses a random legal move. Book choices are uniform among distinct moves;
they are not weighted by popularity or evaluated for strength.

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
python -m PyInstaller --onefile --name ModemCE2 --add-data "data/opening_book.json;data" main.py
```

Select `dist/ModemCE2.exe` as a UCI engine in CuteChess. The book is embedded,
so the executable can be copied on its own. `ModemCE1.exe` remains separate.
