"""Run paired-color Cute Chess matches between consecutive ModemCE versions."""

import argparse
import hashlib
import json
import platform
import subprocess
from pathlib import Path

import chess.pgn


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CLI = ROOT / "tools/cutechess-1.5.1/cutechess-1.5.1-win64/cutechess-cli.exe"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cli", type=Path, default=DEFAULT_CLI)
    parser.add_argument("--rounds", type=int, default=4, help="two color-swapped games per round")
    parser.add_argument("--tc", default="3+0.03", help="seconds per game + increment per move")
    parser.add_argument("--first-version", type=int, default=2, help="first newer version to test")
    parser.add_argument("--last-version", type=int, default=12, help="last newer version to test")
    parser.add_argument("--output", type=Path, required=True, help="new output directory")
    args = parser.parse_args()
    if args.rounds < 1:
        parser.error("--rounds must be positive")
    if args.first_version < 2 or args.last_version < args.first_version:
        parser.error("version range must start at 2 or later and end at or after its start")
    cli = args.cli.resolve()
    if not cli.is_file():
        parser.error(f"Cute Chess CLI not found: {cli}")
    for version in range(args.first_version - 1, args.last_version + 1):
        if not (ROOT / f"dist/ModemCE{version}.exe").is_file():
            parser.error(f"Missing dist/ModemCE{version}.exe")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    def sha256(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    metadata = {
        "platform": platform.platform(),
        "processor": platform.processor(),
        "cutechess_cli_sha256": sha256(cli),
        "engine_sha256": {f"ModemCE{v}": sha256(ROOT / f"dist/ModemCE{v}.exe")
                          for v in range(args.first_version - 1, args.last_version + 1)},
        "rounds_per_match": args.rounds,
        "games_per_round": 2,
        "time_control": args.tc,
        "time_margin_ms": 1000,
        "concurrency": 1,
        "max_full_moves": 200,
    }
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    for newer in range(args.first_version, args.last_version + 1):
        older = newer - 1
        prefix = output / f"ModemCE{newer}-vs-ModemCE{older}"
        command = [str(cli), "-engine", f"cmd={ROOT / f'dist/ModemCE{newer}.exe'}",
                   f"name=ModemCE{newer}", "-engine", f"cmd={ROOT / f'dist/ModemCE{older}.exe'}",
                   f"name=ModemCE{older}", "-each", "proto=uci", f"tc={args.tc}",
                   "timemargin=1000", "-games", "2", "-rounds", str(args.rounds),
                   "-concurrency", "1", "-maxmoves", "200", "-pgnout", f"{prefix}.pgn"]
        print(f"Running ModemCE{newer} vs ModemCE{older}", flush=True)
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        prefix.with_suffix(".log").write_text(
            "Command: " + subprocess.list2cmdline(command).replace(str(ROOT), "<PROJECT>") + "\n\n"
            + result.stdout + result.stderr,
            encoding="utf-8")
        print(result.stdout, flush=True)
        if result.returncode:
            raise SystemExit(f"Match failed; see {prefix}.log")
        pgn = prefix.with_suffix(".pgn")
        with pgn.open(encoding="utf-8-sig") as games:
            results = []
            while game := chess.pgn.read_game(games):
                if game.errors or game.headers.get("Result") not in {"1-0", "0-1", "1/2-1/2"}:
                    raise SystemExit(f"Invalid or unfinished game in {pgn}")
                results.append(game.headers["Result"])
        if len(results) != 2 * args.rounds:
            raise SystemExit(f"Expected {2 * args.rounds} games in {pgn}, found {len(results)}")


if __name__ == "__main__":
    main()
