from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "norgespris_cohorts.csv"
OUT_MONTHLY = ROOT / "norgespris_monthly_event_study.csv"
OUT_STRATA = ROOT / "norgespris_stratum_effects.csv"
OUT_FIGURE = ROOT / "norgespris_event_study.png"
OUT_RESULTS = ROOT / "norgespris_results.json"

EARLY = "Ordered early"
CONTROL = "Not ordered"
TREATMENT_START = pd.Timestamp("2025-10-01")
POST_END = pd.Timestamp("2026-04-30")


def weighted_mean(values: pd.Series, weights: pd.Series) -> float:
    ok = values.notna() & weights.notna() & (weights > 0)
    return float(np.average(values[ok], weights=weights[ok]))


def bootstrap_two_way(
    frame: pd.DataFrame,
    value: str,
    weight: str,
    strata: str,
    block: str,
    draws: int = 5000,
    seed: int = 17011,
) -> np.ndarray:
    """Resample strata and calendar-week blocks independently."""
    rng = np.random.default_rng(seed)
    strata_values = frame[strata].drop_duplicates().to_numpy()
    block_values = frame[block].drop_duplicates().to_numpy()
    outputs = np.empty(draws)

    grouped = {(s, b): g for (s, b), g in frame.groupby([strata, block], sort=False)}
    for i in range(draws):
        sampled_s = rng.choice(strata_values, len(strata_values), replace=True)
        sampled_b = rng.choice(block_values, len(block_values), replace=True)
        numerator = 0.0
        denominator = 0.0
        for s in sampled_s:
            for b in sampled_b:
                g = grouped.get((s, b))
                if g is None:
                    continue
                v = g[value].to_numpy()
                w = g[weight].to_numpy()
                ok = np.isfinite(v) & np.isfinite(w) & (w > 0)
                numerator += np.sum(v[ok] * w[ok])
                denominator += np.sum(w[ok])
        outputs[i] = numerator / denominator
    return outputs


def main() -> None:
    cols = [
        "START_TIME",
        "PRICE_AREA",
        "ESTIMATED_ANNUAL_CONSUMPTION_GROUP",
        "NORGESPRIS_ORDER_STATUS",
        "CONSUMPTION",
        "METERINGPOINT_COUNT",
    ]
    df = pd.read_csv(DATA, usecols=cols)
    df = df[df["NORGESPRIS_ORDER_STATUS"].isin([EARLY, CONTROL])].copy()
    df = df.dropna(subset=["CONSUMPTION", "METERINGPOINT_COUNT"])
    df["date"] = pd.to_datetime(df["START_TIME"].str.slice(0, 10))
    df["month"] = df["date"].values.astype("datetime64[M]")
    df["stratum"] = (
        df["PRICE_AREA"] + " | " + df["ESTIMATED_ANNUAL_CONSUMPTION_GROUP"]
    )

    daily = (
        df.groupby(["stratum", "PRICE_AREA", "ESTIMATED_ANNUAL_CONSUMPTION_GROUP",
                    "NORGESPRIS_ORDER_STATUS", "date"], observed=True)
        .agg(consumption=("CONSUMPTION", "sum"),
             meters=("METERINGPOINT_COUNT", "median"),
             hours=("START_TIME", "count"))
        .reset_index()
    )
    daily["kwh_per_meter"] = daily["consumption"] / daily["meters"]

    wide = daily.pivot(
        index=["stratum", "PRICE_AREA", "ESTIMATED_ANNUAL_CONSUMPTION_GROUP", "date"],
        columns="NORGESPRIS_ORDER_STATUS",
        values=["kwh_per_meter", "meters", "consumption"],
    )
    wide.columns = [f"{a}__{b}" for a, b in wide.columns]
    wide = wide.reset_index()
    wide["gap_log"] = np.log(wide[f"kwh_per_meter__{EARLY}"]) - np.log(
        wide[f"kwh_per_meter__{CONTROL}"]
    )
    wide["weight"] = wide[f"meters__{EARLY}"]
    wide["prior_date"] = wide["date"] - pd.DateOffset(years=1)

    prior = wide[["stratum", "date", "gap_log"]].rename(
        columns={"date": "prior_date", "gap_log": "gap_log_prior"}
    )
    matched = wide.merge(prior, on=["stratum", "prior_date"], how="left")
    matched["yoy_gap_change"] = matched["gap_log"] - matched["gap_log_prior"]
    matched["week"] = matched["date"].dt.to_period("W-SUN").astype(str)

    post = matched[(matched["date"] >= TREATMENT_START) & (matched["date"] <= POST_END)].copy()
    placebo = matched[
        (matched["date"] >= TREATMENT_START - pd.DateOffset(years=1))
        & (matched["date"] <= POST_END - pd.DateOffset(years=1))
    ].copy()

    beta_did = weighted_mean(post["yoy_gap_change"], post["weight"])
    beta_placebo = weighted_mean(placebo["yoy_gap_change"], placebo["weight"])
    beta_ddd = beta_did - beta_placebo

    boot_did = bootstrap_two_way(post, "yoy_gap_change", "weight", "stratum", "week")
    boot_placebo = bootstrap_two_way(
        placebo, "yoy_gap_change", "weight", "stratum", "week", seed=17012
    )
    boot_ddd = boot_did - boot_placebo

    # Flexible pre-period prediction of the cohort gap. The control cohort's
    # load proxies the common weather/heating shock; interactions allow early
    # adopters to have a different heating sensitivity within each stratum.
    wide["log_control_load"] = np.log(wide[f"kwh_per_meter__{CONTROL}"])
    wide["month_of_year"] = wide["date"].dt.month
    wide["day_of_week"] = wide["date"].dt.dayofweek
    strata_dummies = pd.get_dummies(wide["stratum"], dtype=float)
    x_parts = [
        strata_dummies,
        pd.get_dummies(
            wide["stratum"] + "|m" + wide["month_of_year"].astype(str), dtype=float
        ),
        pd.get_dummies(
            wide["stratum"] + "|d" + wide["day_of_week"].astype(str), dtype=float
        ),
    ]
    for power in (1, 2, 3):
        x_parts.append(strata_dummies.mul(wide["log_control_load"] ** power, axis=0))
    x_flexible = pd.concat(x_parts, axis=1).to_numpy(float)

    def flexible_residuals(train_end: str, test_start: str, test_end: str) -> tuple[float, pd.DataFrame]:
        train = wide["date"] <= pd.Timestamp(train_end)
        test = (wide["date"] >= pd.Timestamp(test_start)) & (wide["date"] <= pd.Timestamp(test_end))
        model = LinearRegression(fit_intercept=False).fit(
            x_flexible[train], wide.loc[train, "gap_log"], sample_weight=wide.loc[train, "weight"]
        )
        result = wide.loc[test, ["stratum", "date", "weight", "gap_log"]].copy()
        result["residual"] = result["gap_log"].to_numpy() - model.predict(x_flexible[test])
        result["week"] = result["date"].dt.to_period("W-SUN").astype(str)
        return weighted_mean(result["residual"], result["weight"]), result

    beta_flexible, flexible_post = flexible_residuals(
        "2025-09-30", "2025-10-01", "2026-04-30"
    )
    beta_flexible_placebo, flexible_placebo = flexible_residuals(
        "2024-09-30", "2024-10-01", "2025-04-30"
    )
    beta_flexible_adjusted = beta_flexible - beta_flexible_placebo
    boot_flexible = bootstrap_two_way(
        flexible_post, "residual", "weight", "stratum", "week", seed=17013
    )
    boot_flexible_placebo = bootstrap_two_way(
        flexible_placebo, "residual", "weight", "stratum", "week", seed=17014
    )
    boot_flexible_adjusted = boot_flexible - boot_flexible_placebo

    def summary(beta: float, draws: np.ndarray) -> dict[str, float]:
        lo, hi = np.quantile(draws, [0.025, 0.975])
        return {
            "log_points": beta,
            "percent": 100 * np.expm1(beta),
            "ci_log_low": float(lo),
            "ci_log_high": float(hi),
            "ci_percent_low": 100 * np.expm1(float(lo)),
            "ci_percent_high": 100 * np.expm1(float(hi)),
        }

    # Monthly matched event series: same calendar month relative to one year earlier.
    monthly = (
        daily.groupby(["stratum", "PRICE_AREA", "ESTIMATED_ANNUAL_CONSUMPTION_GROUP",
                       "NORGESPRIS_ORDER_STATUS", daily["date"].dt.to_period("M")], observed=True)
        .agg(consumption=("consumption", "sum"), meters=("meters", "median"))
        .reset_index()
        .rename(columns={"date": "month_period"})
    )
    monthly["month"] = monthly["month_period"].dt.to_timestamp()
    monthly["kwh_per_meter"] = monthly["consumption"] / monthly["meters"]
    mw = monthly.pivot(
        index=["stratum", "PRICE_AREA", "ESTIMATED_ANNUAL_CONSUMPTION_GROUP", "month"],
        columns="NORGESPRIS_ORDER_STATUS",
        values=["kwh_per_meter", "meters", "consumption"],
    )
    mw.columns = [f"{a}__{b}" for a, b in mw.columns]
    mw = mw.reset_index().sort_values(["stratum", "month"])
    mw["gap_log"] = np.log(mw[f"kwh_per_meter__{EARLY}"]) - np.log(
        mw[f"kwh_per_meter__{CONTROL}"]
    )
    mw["yoy_gap_change"] = mw["gap_log"] - mw.groupby("stratum")["gap_log"].shift(12)
    mw["weight"] = mw[f"meters__{EARLY}"]
    event = (
        mw.dropna(subset=["yoy_gap_change"])
        .groupby("month")
        .apply(lambda g: pd.Series({
            "effect_log": weighted_mean(g["yoy_gap_change"], g["weight"]),
            "n_strata": g["stratum"].nunique(),
        }), include_groups=False)
        .reset_index()
    )
    event["effect_percent"] = 100 * np.expm1(event["effect_log"])
    event["post"] = event["month"] >= TREATMENT_START
    event.to_csv(OUT_MONTHLY, index=False)

    # Stratum-specific matched DiD and linear-trend-adjusted DDD.
    s_post = post.groupby("stratum").apply(
        lambda g: weighted_mean(g["yoy_gap_change"], g["weight"]), include_groups=False
    )
    s_placebo = placebo.groupby("stratum").apply(
        lambda g: weighted_mean(g["yoy_gap_change"], g["weight"]), include_groups=False
    )
    strata = pd.concat([s_post.rename("did_log"), s_placebo.rename("placebo_log")], axis=1)
    strata["ddd_log"] = strata["did_log"] - strata["placebo_log"]
    for c in ["did_log", "placebo_log", "ddd_log"]:
        strata[c.replace("_log", "_percent")] = 100 * np.expm1(strata[c])
    strata.reset_index().to_csv(OUT_STRATA, index=False)

    # Aggregate volume implications for early adopters, Oct 2025-Apr 2026.
    post_early = daily[
        (daily["NORGESPRIS_ORDER_STATUS"] == EARLY)
        & (daily["date"] >= TREATMENT_START)
        & (daily["date"] <= POST_END)
    ]
    observed_kwh = float(post_early["consumption"].sum())
    treated_meters = float(
        post_early.groupby("stratum")["meters"].median().sum()
    )

    def volume(beta: float) -> dict[str, float]:
        effect_kwh = observed_kwh * (1 - np.exp(-beta))
        return {
            "observed_early_gwh": observed_kwh / 1e6,
            "effect_gwh": effect_kwh / 1e6,
            "effect_kwh_per_treated_meter": effect_kwh / treated_meters,
            "treated_meters": treated_meters,
        }

    # Plot the matched event series.
    fig, ax = plt.subplots(figsize=(10, 5.5))
    colors = np.where(event["post"], "#c7362f", "#1767ce")
    ax.bar(event["month"], event["effect_percent"], width=24, color=colors)
    ax.axhline(0, color="#202020", linewidth=1)
    ax.axvline(TREATMENT_START, color="#202020", linestyle="--", linewidth=1.2)
    ax.set_title("Tidlige bestillere relativt til ikke-bestillere")
    ax.set_subtitle = None
    ax.set_ylabel("Årsdifferanse i forbruk per målepunkt (%)")
    ax.set_xlabel("")
    ax.grid(axis="y", alpha=0.25)
    fig.text(0.01, 0.01, "Kilde: Elhub. Samme måned året før er kontrollert bort. Rød = etter innføringen.", fontsize=9)
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(OUT_FIGURE, dpi=180)
    plt.close(fig)

    results = {
        "sample": {
            "rows_hourly_primary": int(len(df)),
            "start": str(df["date"].min().date()),
            "end": str(df["date"].max().date()),
            "strata": int(daily["stratum"].nunique()),
            "post_days": int(post["date"].nunique()),
        },
        "matched_did": summary(beta_did, boot_did),
        "placebo_2024": summary(beta_placebo, boot_placebo),
        "trend_adjusted_ddd": summary(beta_ddd, boot_ddd),
        "flexible_load_adjusted": summary(beta_flexible, boot_flexible),
        "flexible_load_placebo_2024": summary(
            beta_flexible_placebo, boot_flexible_placebo
        ),
        "flexible_load_bias_adjusted": summary(
            beta_flexible_adjusted, boot_flexible_adjusted
        ),
        "volume_matched_did": volume(beta_did),
        "volume_trend_adjusted_ddd": volume(beta_ddd),
        "volume_flexible_load_adjusted": volume(beta_flexible_adjusted),
        "notes": [
            "Primary comparison excludes late adopters.",
            "Matched DiD compares Oct 2025-Apr 2026 with identical calendar dates one year earlier.",
            "Trend-adjusted DDD subtracts the corresponding Oct 2024-Apr 2025 placebo change.",
            "Intervals use a two-way bootstrap over the nine strata and calendar-week blocks.",
            "Flexible load adjustment predicts the early-vs-control gap using only pre-policy data, with stratum-specific seasonality, weekday effects, and a cubic function of control-cohort load.",
        ],
    }
    OUT_RESULTS.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
