"""Figures for the memo, from the pipeline outputs in data/derived/.

  fig_errors.png  : held-out error and bias by drainage area for bankfull and in-channel width and depth,
                    existing RiverShapeML data vs the expanded set (A vs B2)
  fig_product.png : median bankfull and in-channel width and depth vs drainage area, with the 90% prediction band

Usage: python memo/make_figures.py   (after ./run_all.sh)
"""
import sys
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DER, MEMO = ROOT / "data/derived", ROOT / "memo"
sys.path.insert(0, str(ROOT / "src"))
from metrics import summarize  # noqa: E402

BLUE, ORANGE, GREEN, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e6e5e0"
LABELS = ["<10", "10-100", "100-1k", "1k-10k", ">10k"]
plt.rcParams.update({"font.family": "Helvetica Neue", "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "axes.grid.axis": "y", "grid.color": GRID, "grid.linewidth": 0.6,
                     "legend.frameon": False, "savefig.dpi": 220})


TARGETS = [("TW_bf", "Bankfull width"), ("Y_bf", "Bankfull depth"), ("TW_in", "In-channel width"), ("Y_in", "In-channel depth")]
VAR = [("A_status_quo", BLUE, "Existing RiverShapeML data (A)"), ("B2_plus_new_sites", GREEN, "Expanded training set (B2)")]


def fig_errors():
    fig, axes = plt.subplots(2, 4, figsize=(7.2, 3.4), sharex=True, sharey="row")
    x = np.arange(len(LABELS))
    for col, (target, name) in enumerate(TARGETS):
        p = pd.read_parquet(DER / f"runs/riverml_{target}/predictions.parquet")
        s = summarize(p[p.variant.isin([v for v, *_ in VAR])], ["da_bin"])
        s["da_bin"] = s.da_bin.astype(str)
        for row, metric in enumerate(["median_abs_err_%", "bias_%"]):
            ax = axes[row, col]
            for k, (v, color, lab) in enumerate(VAR):
                vals = s[s.variant == v].set_index("da_bin").reindex(LABELS)[metric].to_numpy()
                bars = ax.bar(x + (k - 0.5) * 0.38, vals, 0.36, color=color, label=lab, edgecolor="white", linewidth=0.8)
                for xi, val in zip(x + (k - 0.5) * 0.38, vals):
                    ax.text(xi, max(val, 0) + 2, f"{round(val):.0f}".replace("-0", "0"), ha="center", va="bottom",
                            fontsize=5.5, color=MUTED)
            ax.axhline(0, color=MUTED, linewidth=0.8)
            ax.set_xticks(x, ["<10", "10–\n100", "100–\n1k", "1k–\n10k", ">10k"], fontsize=6.5)
            if row == 0:
                ax.set_title(name, fontsize=8.5, color=INK, loc="left")
            if row == 1:
                ax.set_xlabel("Drainage area (km²)", fontsize=7.5)
        axes[0, 0].set_ylabel("Median abs. error (%)", fontsize=7.5)
        axes[1, 0].set_ylabel("Median bias (%)", fontsize=7.5)
    h, l = axes[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=2, fontsize=7, bbox_to_anchor=(0.5, 0))
    fig.tight_layout(rect=(0, 0.06, 1, 1), w_pad=0.4)
    fig.savefig(MEMO / "fig_errors.png"); plt.close(fig)


def fig_product():
    prod = pd.read_parquet(DER / "product_compare.parquet")
    edges = np.logspace(-1, 6.5, 31)
    prod["bin"] = pd.cut(prod.totdasqkm, edges)
    g = prod.groupby("bin", observed=True)
    mid = np.array([np.sqrt(iv.left * iv.right) for iv in g.size().index])
    keep = g.size().to_numpy() >= 50
    med = lambda c: g[c].median().to_numpy()[keep]
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 4.6), sharex=True)
    for r, (kind, kname) in enumerate([("bf", "Bankfull"), ("in", "In-channel")]):
        for c, (v, unit, ylim) in enumerate([("tw", "width", (1, 1500)), ("y", "depth", (0.05, 30))]):
            ax = axes[r, c]
            ax.axvspan(0.1, 5, color="#f1efe8", zorder=0)
            ax.fill_between(mid[keep], med(f"ours_{v}_{kind}_m_p05"), med(f"ours_{v}_{kind}_m_p95"), color=GREEN,
                            alpha=0.15, linewidth=0, label="90% prediction interval (expanded-set retrain)")
            lines = [("hydroshare", ORANGE, "2024 release"), ("ours", GREEN, "Expanded-set retrain")]
            if kind == "bf":
                lines.insert(0, ("deployed", BLUE, "Current model"))
            for src, color, lab in lines:
                ax.plot(mid[keep], med(f"{src}_{v}_{kind}_m"), color=color, linewidth=1.6, label=lab)
            if kind == "bf":
                ax.plot(mid[keep], med(f"bieger_{v}_bf_m"), color=MUTED, linewidth=1.3, linestyle=(0, (4, 3)),
                        label="Bieger et al. (2015) regional curve")
            ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(0.1, 3e6); ax.set_ylim(*ylim)
            ax.set_title(f"{kname} {unit}", fontsize=8.5, color=INK, loc="left")
            ax.set_ylabel(f"Median {unit} (m)", fontsize=7.5)
            ax.grid(True, which="major", axis="both", color=GRID, linewidth=0.6)
            if r == 1:
                ax.set_xlabel("Drainage area (km²)")
    h, l = axes[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=3, fontsize=7, bbox_to_anchor=(0.5, 0))
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.savefig(MEMO / "fig_product.png"); plt.close(fig)


if __name__ == "__main__":
    fig_errors()
    fig_product()
    print("wrote", MEMO / "fig_errors.png", MEMO / "fig_product.png")
