"""Run rotating, paired-opening batches with a hard overnight cutoff."""

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import chess.pgn

ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "tools/cutechess-1.5.1/cutechess-1.5.1-win64/cutechess-cli.exe"
OPENINGS = ROOT / "benchmarks/openings/overnight.pgn"
PAIRS = [(6, 5), (9, 8), (12, 5), (12, 9), (12, 11)]
GAMES_PER_BATCH = 10
OPENINGS_PER_BATCH = 5
MAX_BATCHES_PER_PAIR = 10
OPENING_COUNT = 25


def utc_now():
    return datetime.now(timezone.utc)


def iso_now():
    return utc_now().isoformat(timespec="seconds")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path, value):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def read_games(path, newer, older):
    games = []
    with path.open(encoding="utf-8-sig") as source:
        while game := chess.pgn.read_game(source):
            if game.errors:
                raise ValueError(f"Invalid PGN in {path}: {game.errors}")
            if game.headers.get("Result") not in {"1-0", "0-1", "1/2-1/2"}:
                raise ValueError(f"Unfinished game in {path}")
            if {game.headers["White"], game.headers["Black"]} != {newer, older}:
                raise ValueError(f"Unexpected players in {path}")
            moves = list(game.mainline_moves())
            if len(moves) < 6:
                raise ValueError(f"Opening missing from {path}")
            games.append(game)
    for i in range(0, len(games) - 1, 2):
        first, second = games[i:i + 2]
        if (list(first.mainline_moves())[:6] != list(second.mainline_moves())[:6] or
                first.headers["White"] != second.headers["Black"] or
                first.headers["Black"] != second.headers["White"]):
            raise ValueError(f"Opening pair or colors did not match in {path}")
    return games


def update_report(output, status):
    rows = []
    for newer, older in PAIRS:
        name = f"ModemCE{newer}-vs-ModemCE{older}"
        wins = losses = draws = 0
        completed = {item["batch"] for item in status["completed_batches"] if item["match"] == name}
        for batch in sorted(completed):
            path = output / name / f"batch-{batch:02d}.pgn"
            for game in read_games(path, f"ModemCE{newer}", f"ModemCE{older}"):
                result = game.headers["Result"]
                if result == "1/2-1/2":
                    draws += 1
                elif game.headers["White" if result == "1-0" else "Black"] == f"ModemCE{newer}":
                    wins += 1
                else:
                    losses += 1
        total = wins + losses + draws
        percent = f"{100 * (wins + draws / 2) / total:.2f}%" if total else "—"
        rows.append(f"| CE{newer} vs CE{older} | {wins}–{losses}–{draws} | {total} | {percent} | [{name}/]({name}/) |")
    text = "\n".join([
        "# Overnight paired-opening matches", "",
        f"Status: **{status['state']}**. Last updated (UTC): {status['updated_utc']}.", "",
        "Each row is a separate head-to-head comparison; score is from the first engine's perspective.",
        "Each batch uses five fixed six-ply openings, played twice with colors swapped. The 25-opening",
        "set is traversed twice for a target of 100 games per matchup. Results are stochastic.", "",
        "Time control: **30 seconds plus 0.2 seconds per move**, 1,000 ms Cute Chess time margin,",
        "one game at a time, 200-full-move draw limit. The engine's own opening books remain enabled.",
        "The matches use the same 25 openings; they do not sample all possible openings or opponents.", "",
        "The table includes only fully completed and validated batches; partial batches are kept separately.", "",
        "| Match | Wins–losses–draws | Games | Score | Records |",
        "| --- | ---: | ---: | ---: | --- |", *rows, "",
        "Individual batch PGNs and logs are in the linked folders. [settings.json](settings.json)",
        "records binary and opening hashes; [status.json](status.json) records progress and errors.",
        "The earlier 3+0.03-second results are in [the extended report](../2026-11-22-extended/README.md).",
        "",
    ])
    (output / "README.md").write_text(text, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--deadline-utc", required=True,
                        help="ISO UTC cutoff, e.g. 2026-11-22T23:00:00+00:00")
    args = parser.parse_args()
    deadline = datetime.fromisoformat(args.deadline_utc)
    if deadline.utcoffset() != timedelta(0):
        parser.error("deadline must include UTC offset +00:00")
    if not CLI.is_file() or not OPENINGS.is_file():
        parser.error("Cute Chess CLI and the opening PGN must be available")
    versions = sorted({version for pair in PAIRS for version in pair})
    for version in versions:
        if not (ROOT / f"dist/ModemCE{version}.exe").is_file():
            parser.error(f"Missing ModemCE{version}.exe")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    settings = {
        "started_utc": iso_now(), "deadline_utc": deadline.isoformat(),
        "last_batch_start_utc": (deadline - timedelta(minutes=30)).isoformat(),
        "cutechess_cli_sha256": sha256(CLI), "openings_sha256": sha256(OPENINGS),
        "engines_sha256": {f"ModemCE{v}": sha256(ROOT / f"dist/ModemCE{v}.exe") for v in versions},
        "pairs": PAIRS, "time_control": "30+0.2", "time_margin_ms": 1000,
        "max_full_moves": 200, "concurrency": 1, "openings": OPENING_COUNT,
        "games_per_batch": GAMES_PER_BATCH, "batches_per_pair_target": MAX_BATCHES_PER_PAIR,
        "opening_set": "benchmarks/openings/overnight.pgn",
        "engine_book": "enabled", "engine_randomness": "unseeded",
    }
    atomic_json(output / "settings.json", settings)
    status = {"state": "running", "updated_utc": iso_now(), "completed_batches": [], "error": None}

    def save():
        status["updated_utc"] = iso_now()
        atomic_json(output / "status.json", status)
        update_report(output, status)

    save()
    try:
        for batch in range(MAX_BATCHES_PER_PAIR):
            for newer, older in PAIRS:
                if utc_now() >= deadline - timedelta(minutes=30):
                    status["state"] = "stopped before deadline"
                    save()
                    return
                name = f"ModemCE{newer}-vs-ModemCE{older}"
                folder = output / name
                folder.mkdir(exist_ok=True)
                prefix = folder / f"batch-{batch + 1:02d}"
                opening_start = 1 + ((batch * OPENINGS_PER_BATCH) % OPENING_COUNT)
                command = [str(CLI), "-engine", f"cmd={ROOT / f'dist/ModemCE{newer}.exe'}",
                           f"name=ModemCE{newer}", "-engine", f"cmd={ROOT / f'dist/ModemCE{older}.exe'}",
                           f"name=ModemCE{older}", "-each", "proto=uci", "tc=30+0.2", "timemargin=1000",
                           "-openings", f"file={OPENINGS}", "format=pgn", "plies=6", "order=sequential",
                           f"start={opening_start}", "-repeat", "-games", "2", "-rounds", "5",
                           "-concurrency", "1", "-maxmoves", "200", "-pgnout", str(prefix.with_suffix(".pgn")), "fi"]
                print(f"{iso_now()} Starting {name} batch {batch + 1}/10", flush=True)
                with prefix.with_suffix(".log").open("w", encoding="utf-8") as log:
                    log.write("Command: " + subprocess.list2cmdline(command).replace(str(ROOT), "<PROJECT>") + "\n\n")
                    log.flush()
                    proc = subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
                    try:
                        returncode = proc.wait(timeout=max(1, (deadline - utc_now()).total_seconds() - 30))
                    except subprocess.TimeoutExpired:
                        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], capture_output=True)
                        proc.wait(timeout=10)
                        status["state"] = "stopped at deadline"
                        save()
                        return
                if returncode:
                    raise RuntimeError(f"Cute Chess exited {returncode}; see {prefix}.log")
                games = read_games(prefix.with_suffix(".pgn"), f"ModemCE{newer}", f"ModemCE{older}")
                if len(games) != GAMES_PER_BATCH:
                    raise RuntimeError(f"Expected {GAMES_PER_BATCH} games in {prefix}, got {len(games)}")
                status["completed_batches"].append({"match": name, "batch": batch + 1,
                                                    "games": len(games), "opening_start": opening_start})
                save()
                print(f"{iso_now()} Completed {name} batch {batch + 1}/10", flush=True)
        status["state"] = "complete"
    except Exception as exc:
        status["state"] = "failed"
        status["error"] = str(exc)
        print(f"Error: {exc}", file=sys.stderr, flush=True)
    save()
    if status["state"] == "failed":
        raise SystemExit(1)


if __name__ == "__main__":
    # Keep the system awake for the requested run; restore normal behavior on exit.
    if os.name == "nt":
        import ctypes
        kernel32 = ctypes.windll.kernel32
        if not kernel32.SetThreadExecutionState(0x80000001):
            raise OSError("Could not keep the system awake during the overnight run")
    try:
        main()
    finally:
        if os.name == "nt":
            kernel32.SetThreadExecutionState(0x80000000)
