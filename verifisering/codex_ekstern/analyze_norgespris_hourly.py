from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


ROOT = Path(__file__).resolve().parent
ELHUB = ROOT / "norgespris_cohorts.csv"
PRICES = ROOT / "norgespris_hourly_prices.csv"
WEATHER = ROOT / "norgespris_hourly_temperature.csv"
RESULTS = ROOT / "norgespris_hourly_results.json"
BIN_TABLE = ROOT / "norgespris_hourly_price_response.csv"
FIGURE = ROOT / "norgespris_hourly_dose_response.png"

EARLY = "Ordered early"
CONTROL = "Not ordered"

AREAS = ["NO1", "NO2", "NO5"]
WEATHER_POINTS = {
    "NO1": [(59.9139, 10.7522), (61.1153, 10.4662), (60.1905, 11.9977)],
    "NO2": [(58.1467, 7.9956), (58.9700, 5.7331), (59.2096, 9.6089)],
    "NO5": [(60.39299, 5.32415), (60.6296, 6.4222), (61.4522, 5.8572)],
}


def fetch_json(url: str, attempts: int = 5) -> object:
    req = urllib.request.Request(url, headers={"User-Agent": "norgespris-research/1.0"})
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(req, timeout=40) as response:
                return json.loads(response.read())
        except Exception:
            if attempt == attempts - 1:
                raise
            time.sleep(0.5 * 2**attempt)
    raise RuntimeError("unreachable")


def download_prices() -> pd.DataFrame:
    if PRICES.exists():
        return pd.read_csv(PRICES, parse_dates=["timestamp_utc"])
    days = pd.date_range("2024-10-01", "2025-04-30", freq="D").append(
        pd.date_range("2025-10-01", "2026-04-30", freq="D")
    )

    def one(day: pd.Timestamp, area: str) -> list[dict[str, object]]:
        url = (
            "https://www.hvakosterstrommen.no/api/v1/prices/"
            f"{day.year}/{day:%m-%d}_{area}.json"
        )
        payload = fetch_json(url)
        return [
            {
                "timestamp_utc": pd.Timestamp(row["time_start"]).tz_convert("UTC"),
                "price_area": area,
                "spot_nok_kwh": float(row["NOK_per_kWh"]),
            }
            for row in payload
        ]

    rows: list[dict[str, object]] = []
    tasks = [(day, area) for day in days for area in AREAS]
    print(f"prices: starting {len(tasks)} day-area requests")
    with ThreadPoolExecutor(max_workers=48) as pool:
        futures = {pool.submit(one, day, area): (day, area) for day, area in tasks}
        for i, future in enumerate(as_completed(futures), start=1):
            rows.extend(future.result())
            if i % 300 == 0:
                print(f"prices: {i}/{len(tasks)} day-area requests")
    frame = pd.DataFrame(rows).sort_values(["timestamp_utc", "price_area"])
    frame.to_csv(PRICES, index=False)
    return frame


def download_weather() -> pd.DataFrame:
    if WEATHER.exists():
        return pd.read_csv(WEATHER, parse_dates=["timestamp_utc"])
    rows: list[pd.DataFrame] = []
    for area, points in WEATHER_POINTS.items():
        point_frames = []
        for point_id, (lat, lon) in enumerate(points):
            params = urllib.parse.urlencode(
                {
                    "latitude": lat,
                    "longitude": lon,
                    "start_date": "2023-10-01",
                    "end_date": "2026-04-30",
                    "hourly": "temperature_2m",
                    "timezone": "GMT",
                }
            )
            payload = fetch_json("https://archive-api.open-meteo.com/v1/archive?" + params)
            hourly = payload["hourly"]
            point_frames.append(
                pd.DataFrame(
                    {
                        "timestamp_utc": pd.to_datetime(hourly["time"], utc=True),
                        f"temp_{point_id}": hourly["temperature_2m"],
                    }
                )
            )
        area_frame = point_frames[0]
        for extra in point_frames[1:]:
            area_frame = area_frame.merge(extra, on="timestamp_utc", validate="one_to_one")
        area_frame["temperature_c"] = area_frame.filter(like="temp_").mean(axis=1)
        area_frame["price_area"] = area
        rows.append(area_frame[["timestamp_utc", "price_area", "temperature_c"]])
    frame = pd.concat(rows, ignore_index=True).sort_values(["timestamp_utc", "price_area"])
    frame.to_csv(WEATHER, index=False)
    return frame


def make_hourly_gap() -> pd.DataFrame:
    cols = [
        "START_TIME",
        "PRICE_AREA",
        "ESTIMATED_ANNUAL_CONSUMPTION_GROUP",
        "NORGESPRIS_ORDER_STATUS",
        "CONSUMPTION",
        "METERINGPOINT_COUNT",
    ]
    df = pd.read_csv(ELHUB, usecols=cols)
    df = df[df["NORGESPRIS_ORDER_STATUS"].isin([EARLY, CONTROL])].copy()
    df["timestamp_utc"] = pd.to_datetime(df["START_TIME"], utc=True)
    df["local_time"] = df["timestamp_utc"].dt.tz_convert("Europe/Oslo")
    df["stratum"] = df["PRICE_AREA"] + " | " + df["ESTIMATED_ANNUAL_CONSUMPTION_GROUP"]
    df["kwh_per_meter"] = df["CONSUMPTION"] / df["METERINGPOINT_COUNT"]
    wide = df.pivot(
        index=["timestamp_utc", "local_time", "PRICE_AREA", "stratum"],
        columns="NORGESPRIS_ORDER_STATUS",
        values=["kwh_per_meter", "METERINGPOINT_COUNT"],
    )
    wide.columns = [f"{a}__{b}" for a, b in wide.columns]
    wide = wide.reset_index()
    wide["gap_log"] = np.log(wide[f"kwh_per_meter__{EARLY}"]) - np.log(
        wide[f"kwh_per_meter__{CONTROL}"]
    )
    wide["log_control_load"] = np.log(wide[f"kwh_per_meter__{CONTROL}"])
    wide["weight"] = wide[f"METERINGPOINT_COUNT__{EARLY}"]
    wide["hour_of_week"] = wide["local_time"].dt.dayofweek * 24 + wide["local_time"].dt.hour
    wide["month_of_year"] = wide["local_time"].dt.month
    wide["date"] = wide["local_time"].dt.tz_localize(None).dt.normalize()
    return wide


def add_prices_and_weather(frame: pd.DataFrame) -> pd.DataFrame:
    prices = download_prices()
    weather = download_weather()
    prices["timestamp_utc"] = pd.to_datetime(prices["timestamp_utc"], utc=True)
    # The source contains two conflicting duplicate rows at the 2024 autumn
    # clock change (NO1 and NO5). Average those two isolated source glitches.
    prices = prices.groupby(["timestamp_utc", "price_area"], as_index=False)["spot_nok_kwh"].mean()
    weather["timestamp_utc"] = pd.to_datetime(weather["timestamp_utc"], utc=True)
    out = frame.merge(
        weather,
        left_on=["timestamp_utc", "PRICE_AREA"],
        right_on=["timestamp_utc", "price_area"],
        how="left",
        validate="many_to_one",
    ).drop(columns="price_area")
    out = out.merge(
        prices,
        left_on=["timestamp_utc", "PRICE_AREA"],
        right_on=["timestamp_utc", "price_area"],
        how="left",
        validate="many_to_one",
    ).drop(columns="price_area")
    threshold = np.where(out["date"].dt.year == 2026, 0.77,
                np.where(out["date"].dt.year == 2025, 0.75, 0.73))
    spot = out["spot_nok_kwh"]
    out["standard_support_price"] = np.where(
        spot > threshold, threshold + 0.10 * (spot - threshold), spot
    )
    out["wedge_nok_kwh"] = out["standard_support_price"] - 0.40
    out["heating_degrees"] = np.maximum(0.0, 17.0 - out["temperature_c"])
    return out


def residualize_event(
    frame: pd.DataFrame,
    train_end: str,
    test_start: str,
    test_end: str,
    include_control_load: bool,
) -> pd.DataFrame:
    outputs = []
    for stratum, g in frame.groupby("stratum", sort=True):
        g = g.sort_values("timestamp_utc").copy()
        train = g["date"] <= pd.Timestamp(train_end)
        test = (g["date"] >= pd.Timestamp(test_start)) & (g["date"] <= pd.Timestamp(test_end))
        fit = g.loc[train].dropna(subset=["gap_log", "temperature_c", "weight"])
        score = g.loc[test].dropna(
            subset=["gap_log", "temperature_c", "weight", "spot_nok_kwh", "wedge_nok_kwh"]
        ).copy()

        def design(x: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
            pieces = [
                pd.get_dummies(x["hour_of_week"].astype(str), prefix="how", dtype=float),
                pd.get_dummies(x["month_of_year"].astype(str), prefix="mon", dtype=float),
            ]
            hd = x["heating_degrees"]
            pieces.extend([hd.rename("hd"), (hd**2).rename("hd2"), (hd**3).rename("hd3")])
            if include_control_load:
                lc = x["log_control_load"]
                pieces.extend([lc.rename("lc"), (lc**2).rename("lc2"), (lc**3).rename("lc3")])
            ans = pd.concat(pieces, axis=1)
            if columns is not None:
                ans = ans.reindex(columns=columns, fill_value=0.0)
            return ans

        x_train = design(fit)
        x_test = design(score, list(x_train.columns))
        model = LinearRegression().fit(x_train, fit["gap_log"], sample_weight=fit["weight"])
        score["residual"] = score["gap_log"] - model.predict(x_test)
        score["stratum"] = stratum
        outputs.append(score)
    return pd.concat(outputs, ignore_index=True)


def weighted_regression(frame: pd.DataFrame) -> dict[str, object]:
    strata = pd.get_dummies(frame["stratum"], dtype=float)
    x = np.column_stack([strata.to_numpy(), frame["wedge_nok_kwh"].to_numpy()])
    y = frame["residual"].to_numpy()
    w = frame["weight"].to_numpy()
    sw = np.sqrt(w)
    coef, *_ = np.linalg.lstsq(x * sw[:, None], y * sw, rcond=None)
    pred = x @ coef
    return {
        "slope_log_per_nok_kwh": float(coef[-1]),
        "slope_percent_per_nok_kwh": float(100 * coef[-1]),
        "weighted_mean_residual_log": float(np.average(y, weights=w)),
        "weighted_mean_residual_percent": float(100 * np.expm1(np.average(y, weights=w))),
        "weighted_mean_wedge": float(np.average(frame["wedge_nok_kwh"], weights=w)),
        "weighted_mean_temperature": float(np.average(frame["temperature_c"], weights=w)),
        "n_hour_strata": int(len(frame)),
        "n_hours": int(frame["timestamp_utc"].nunique()),
        "n_strata": int(frame["stratum"].nunique()),
        "r2": float(1 - np.sum(w * (y - pred) ** 2) / np.sum(w * (y - np.average(y, weights=w)) ** 2)),
    }


def bootstrap_week_stats(actual: pd.DataFrame, placebo: pd.DataFrame, draws: int = 2000) -> np.ndarray:
    rng = np.random.default_rng(171117)

    def pieces(frame: pd.DataFrame) -> tuple[list[str], dict[str, pd.DataFrame]]:
        f = frame.copy()
        f["week"] = f["date"].dt.to_period("W-SUN").astype(str)
        weeks = f["week"].drop_duplicates().tolist()
        return weeks, {week: g for week, g in f.groupby("week", sort=False)}

    aw, ag = pieces(actual)
    pw, pg = pieces(placebo)
    out = np.empty((draws, 2))
    for i in range(draws):
        aa = pd.concat([ag[w] for w in rng.choice(aw, len(aw), replace=True)], ignore_index=True)
        pp = pd.concat([pg[w] for w in rng.choice(pw, len(pw), replace=True)], ignore_index=True)
        fa = weighted_regression(aa)
        fp = weighted_regression(pp)
        out[i, 0] = fa["slope_log_per_nok_kwh"] - fp["slope_log_per_nok_kwh"]
        out[i, 1] = fa["weighted_mean_residual_log"] - fp["weighted_mean_residual_log"]
    return out


def binned_effects(actual: pd.DataFrame, placebo: pd.DataFrame) -> pd.DataFrame:
    bins = [-np.inf, 0.0, 0.25, 0.50, 0.75, np.inf]
    labels = ["≤ 0", "0–0.25", "0.25–0.50", "0.50–0.75", "> 0.75"]
    rows = []
    for name, data in [("Norgespris 2025–26", actual), ("Placebo 2024–25", placebo)]:
        f = data.copy()
        f["wedge_bin"] = pd.cut(f["wedge_nok_kwh"], bins=bins, labels=labels)
        for label, g in f.groupby("wedge_bin", observed=True):
            mean = np.average(g["residual"], weights=g["weight"])
            rows.append(
                {
                    "period": name,
                    "wedge_bin_nok_kwh": str(label),
                    "effect_log": mean,
                    "effect_percent": 100 * np.expm1(mean),
                    "mean_wedge_nok_kwh": np.average(g["wedge_nok_kwh"], weights=g["weight"]),
                    "n_hour_strata": len(g),
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    gap = make_hourly_gap()
    data = add_prices_and_weather(gap)
    actual = residualize_event(
        data, "2025-09-30", "2025-10-01", "2026-04-30", include_control_load=True
    )
    placebo = residualize_event(
        data, "2024-09-30", "2024-10-01", "2025-04-30", include_control_load=True
    )
    actual_temp_only = residualize_event(
        data, "2025-09-30", "2025-10-01", "2026-04-30", include_control_load=False
    )
    placebo_temp_only = residualize_event(
        data, "2024-09-30", "2024-10-01", "2025-04-30", include_control_load=False
    )

    fit_actual = weighted_regression(actual)
    fit_placebo = weighted_regression(placebo)
    fit_actual_temp = weighted_regression(actual_temp_only)
    fit_placebo_temp = weighted_regression(placebo_temp_only)
    slope_diff = fit_actual["slope_log_per_nok_kwh"] - fit_placebo["slope_log_per_nok_kwh"]
    slope_diff_temp = fit_actual_temp["slope_log_per_nok_kwh"] - fit_placebo_temp["slope_log_per_nok_kwh"]
    draws = bootstrap_week_stats(actual, placebo)
    slope_ci = np.quantile(draws[:, 0], [0.025, 0.975])
    level_ci = np.quantile(draws[:, 1], [0.025, 0.975])
    mean_diff = fit_actual["weighted_mean_residual_log"] - fit_placebo["weighted_mean_residual_log"]

    bins = binned_effects(actual, placebo)
    bins.to_csv(BIN_TABLE, index=False)

    result = {
        "main_model": {
            "actual": fit_actual,
            "placebo": fit_placebo,
            "slope_difference_log_per_nok_kwh": slope_diff,
            "slope_difference_percentage_points_per_nok_kwh": 100 * slope_diff,
            "slope_difference_ci_95_percentage_points_per_nok_kwh": [float(100 * slope_ci[0]), float(100 * slope_ci[1])],
            "mean_level_difference_log": mean_diff,
            "mean_level_difference_percent": float(100 * np.expm1(mean_diff)),
            "mean_level_difference_ci_95_percent": [
                float(100 * np.expm1(level_ci[0])),
                float(100 * np.expm1(level_ci[1])),
            ],
            "dose_component_at_actual_mean_wedge_percent": float(
                100 * np.expm1(slope_diff * fit_actual["weighted_mean_wedge"])
            ),
        },
        "temperature_only_robustness": {
            "actual": fit_actual_temp,
            "placebo": fit_placebo_temp,
            "slope_difference_log_per_nok_kwh": slope_diff_temp,
            "slope_difference_percentage_points_per_nok_kwh": 100 * slope_diff_temp,
        },
        "definitions": {
            "outcome": "log(kWh per meter, early orderers) - log(kWh per meter, non-orderers), hourly",
            "price_wedge": "effective marginal price under ordinary support minus NOK 0.40/kWh",
            "temperature": "mean hourly 2m temperature across three points in each price area",
            "calendar_controls": "stratum-specific hour-of-week and month-of-year fixed effects",
            "weather_controls": "stratum-specific cubic heating-degree function (17 C base)",
            "main_extra_control": "stratum-specific cubic log load among non-orderers",
            "inference": "independent calendar-week block bootstrap for actual and placebo periods, 2000 draws",
        },
    }
    RESULTS.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    order = ["≤ 0", "0–0.25", "0.25–0.50", "0.50–0.75", "> 0.75"]
    fig, ax = plt.subplots(figsize=(9.5, 5.4))
    for name, color, marker in [
        ("Norgespris 2025–26", "#c7362f", "o"),
        ("Placebo 2024–25", "#1767ce", "s"),
    ]:
        g = bins[(bins["period"] == name) & (bins["n_hour_strata"] >= 300)].set_index(
            "wedge_bin_nok_kwh"
        ).reindex(order).dropna()
        ax.plot(g["mean_wedge_nok_kwh"], g["effect_percent"], marker=marker, color=color, linewidth=2, label=name)
    ax.axhline(0, color="#222", linewidth=1)
    ax.set_xlabel("Marginal prisfordel med Norgespris (kr/kWh)")
    ax.set_ylabel("Temperatur- og kalenderjustert kohortgap (%)")
    ax.set_title("Øker forbruksgapet når Norgespris gir større prisfordel?")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(FIGURE, dpi=180)


if __name__ == "__main__":
    main()
