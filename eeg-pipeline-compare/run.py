from __future__ import annotations

import argparse
from pathlib import Path

from _analysis import run_dual_derivative_analysis, save_analysis
from _viz import render_console_summary


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Compare 2 EEG derivatives (V1)")
	parser.add_argument("path_a", help="Path to derivative A (file or directory)")
	parser.add_argument("path_b", help="Path to derivative B (file or directory)")
	parser.add_argument(
		"--out",
		default="analysis.json",
		help="Output JSON path (default: analysis.json)",
	)
	return parser.parse_args()


def main() -> int:
	args = parse_args()
	result = run_dual_derivative_analysis(args.path_a, args.path_b)
	save_analysis(result, Path(args.out))
	print(render_console_summary(result))
	return 0


if __name__ == "__main__":
	raise SystemExit(main())