# Next steps

Follow-ups the analysis points to, roughly in order of expected value.

## Done in v2.0

- **Gages that didn't link to a reach:** relinking through the NLDI now links 4,317 of 4,501 new candidate gages
  (previously 3,192); reach and gage drainage areas agree at a median ratio of 1.01 (91% within 25%).
- **In-channel targets and models:** targets at the 1-year flood (smallest annual peak), retrain, re-predict and
  compare, released with bankfull in v2.0.
- **Flood record matched to the measurement period:** annual peaks from water year 2000 onward, with bad-flag
  peaks dropped and one peak per water year.

## Most promising

1. **Sites without a long daily flow record** (~7,075 more candidates, mostly small streams: 985 under 10 km²
   and 2,159 at 10–100 km² of those with a known drainage area): usable if NWM-based flood frequencies are
   acceptable for their targets; RiverShapeML's training code has an NWM flood-frequency option.
2. **In-channel flow definition:** check which in-channel flow downstream users (e.g., flood mapping) need, and
   test the sensitivity of the in-channel product to it.

## Other candidates

- **Split-flow measurements** (kept separate in v2.0, as in HYDRoSWOT and RiverShapeML): sum flow, width and area per site and time where USGS records one row per
  channel, and drop exact duplicate rows; then rerun targets and models.
- **Basin-blocked cross-validation** (e.g., grouped by HUC-4) as a robustness check on the A vs B2 result.
- **Monotone constraints** in XGBoost (width and depth never decrease with drainage area or flow) to stop the
  upward bend below ~5 km², where 44% of reaches sit with almost no training data. Or blend toward a regional
  curve below the smallest training size.
- **Early stopping and regularization (measured):** a sweep with early stopping on validation (tree depth,
  min_child_weight, L2) picked depth 6, min_child_weight 5, ~2,450 trees for both width and depth. On the held-out
  test set (v2.0 targets) it matches the deployed settings (width log R² 0.82 vs 0.82; depth 0.77 vs 0.76) with
  ~4x fewer trees and much less memorization of training sites. Rerunning the sweep on the v2.0 targets ranks a few
  other settings marginally higher (within 1% in validation error); settings are not the accuracy bottleneck.
- **Reach-specific prediction intervals** (e.g., quantile models) instead of one interval per size class.
- **Measurement location as variability:** use the spread between measurement spots at a gage as an estimate of
  within-reach variability, or a per-site target uncertainty for weighting.
- **Questions rather than steps:** whether the HydroShare 2024 release should be updated to the current model (and
  its 932 repeated reach IDs (66,341 rows; perfect-square repeat counts suggest a many-to-many merge)); which bankfull definition downstream users need (2-year-flood water width vs
  field top-of-bank, ~1.5–2× apart).
- **Observation (not a step):** in an exploratory check at ~7,400 gaged reaches (not part of this pipeline),
  the NWM v2.1 2-year flood ran ~20% below the gage value overall and ~50% below for drainage areas < 10 km²
  (10th-90th percentile ratio 0.03-2.2; squared correlation of logs 0.72 overall, 0.03 under 10 km²). It is a key input to the current model, so small-stream inputs are
  weakest exactly where training data is thinnest.
