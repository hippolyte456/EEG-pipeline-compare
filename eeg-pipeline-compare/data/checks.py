"""Minimal checks for data catalog integrity (V1)."""

from __future__ import annotations

import json
from pathlib import Path


REQUIRED = {
	"analysis.json": ["version", "analysis_types"],
	"steps.json": ["version", "step_groups"],
	"signals.json": ["version", "signal_divergences"],
	"metrics.json": ["version", "metrics"],
}


def validate_data_catalogs(data_dir: str | Path) -> dict[str, list[str]]:
	data_path = Path(data_dir)
	report: dict[str, list[str]] = {}

	for fname, required_keys in REQUIRED.items():
		fpath = data_path / fname
		issues: list[str] = []

		if not fpath.exists():
			report[fname] = ["missing file"]
			continue

		try:
			payload = json.loads(fpath.read_text(encoding="utf-8"))
		except Exception as exc:
			report[fname] = [f"invalid JSON: {exc}"]
			continue

		for k in required_keys:
			if k not in payload:
				issues.append(f"missing key: {k}")

		report[fname] = issues

	return report