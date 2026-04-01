"""Entry point: compare two EEG derivatives."""

from _ios import load
from _logger import logger
from _metrics import compute_metrics
from _viz import dual_derivative_figure as viz

fpath1 = ""
fpath2 = ""

if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Compare two EEG derivatives")
    p.add_argument("--a", default=fpath1 or None, required=not fpath1)
    p.add_argument("--b", default=fpath2 or None, required=not fpath2)
    p.add_argument("--out", default="result.json")
    args = p.parse_args()

    logger.info("Loading derivative A: %s", args.a)
    d1 = load(args.a)
    logger.info("Loading derivative B: %s", args.b)
    d2 = load(args.b)

    logger.info("Computing metrics…")
    m1 = compute_metrics(d1)
    m2 = compute_metrics(d2)

    logger.info("Comparing and saving → %s", args.out)
    viz(m1, m2, save=args.out)
    logger.info("Done.")
