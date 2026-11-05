"""Release file for the re-predicted product: "ML-derived channel width and depth, expanded-set retrain".

One row per NHDPlusV2 reach (COMID): bankfull and in-channel width and depth from the expanded-set retrain, each
with split-conformal 90% prediction intervals (5th and 95th percentiles). Values in meters, rounded to the
millimeter. Reaches with a zero or missing drainage area have no interval (NaN). Columns are named as in the 2024
RiverShapeML HydroShare release (hf_id, hf_source, y_bf(m), y_inchan(m), tw_bf(m), tw_inchan(m)), plus the bounds.

Usage: python src/export_product.py
Output: data/derived/release/rivershapeml_expanded_set_v2.parquet  (attached to the GitHub release, not tracked)
"""
from pathlib import Path

import pandas as pd

DER = Path(__file__).resolve().parents[1] / "data/derived"
# column names follow the 2024 RiverShapeML HydroShare release (ml_channel_dimension.parquet), so the file can stand in
# for it; interval bounds are added as *_p05 / *_p95 in the same style
NAMES = {"tw_bf_m": "tw_bf(m)", "y_bf_m": "y_bf(m)", "tw_in_m": "tw_inchan(m)", "y_in_m": "y_inchan(m)"}


def main():
    d = pd.read_parquet(DER / "product_ours.parquet")
    out = pd.DataFrame({"hf_id": d.FEATUREID.astype("int64"), "hf_source": "reference_fabric"})
    for col in ["y_bf_m", "y_in_m", "tw_bf_m", "tw_in_m"]:
        out[NAMES[col]] = d[col].round(3).astype("float32")
    for col in ["y_bf_m", "y_in_m", "tw_bf_m", "tw_in_m"]:
        base = NAMES[col][:-3]
        for q in ["p05", "p95"]:
            out[f"{base}_{q}(m)"] = d[f"{col}_{q}"].round(3).astype("float32")
    (DER / "release").mkdir(exist_ok=True)
    path = DER / "release/rivershapeml_expanded_set_v2.parquet"
    out.to_parquet(path, index=False, compression="zstd")
    print(f"wrote {path.name}: {len(out):,} reaches; without intervals: {out['tw_bf_p05(m)'].isna().sum():,}")


if __name__ == "__main__":
    main()
