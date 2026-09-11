"""Steg 3: Månedlige spotpriser per prisområde (NOK/kWh eks. mva).

Kilde: hvakosterstrommen.no (Nord Pool day-ahead), timesdata fra 2021-12-01.
Jan–nov 2021 mangler her; supplér fra Nord Pool/ENTSO-E om nødvendig, eller
start panelet i des. 2021 (anbefalt – se notat).

Vi lager både enkelt månedssnitt og forbruksveid snitt (veid med NO-områdets
husholdningsforbruk per time fra Elhub hvis tilgjengelig – her: enkelt snitt).
"""
import time
import datetime as dt
import requests
import pandas as pd
from config import RAW, PROC, HKS_URL, PRICE_AREAS, END

START_HKS = dt.date(2021, 12, 1)


S = requests.Session()


def fetch_day(area: str, d: dt.date):
    url = HKS_URL.format(y=d.year, m=d.month, d=d.day, area=area)
    for attempt in range(5):
        try:
            r = S.get(url, timeout=30)
            break
        except requests.exceptions.RequestException:
            time.sleep(5 * (attempt + 1))
    else:
        raise RuntimeError(f"ga opp: {url}")
    if r.status_code == 404:
        return None
    r.raise_for_status()
    js = r.json()
    df = pd.DataFrame(js)
    df["area"] = area
    return df


def main():
    end = dt.date.fromisoformat(END)
    cache = RAW / "spot_hourly.parquet"
    if cache.exists():
        hourly = pd.read_parquet(cache)
        done = set(zip(hourly.area, pd.to_datetime(hourly.time_start.str[:10]).dt.date))
    else:
        hourly, done = pd.DataFrame(), set()
    parts = [hourly] if len(hourly) else []
    for area in PRICE_AREAS:
        d = START_HKS
        while d <= end:
            if (area, d) not in done:
                df = fetch_day(area, d)
                if df is not None:
                    parts.append(df)
                time.sleep(0.1)
                if len(parts) % 200 == 0:
                    pd.concat(parts).to_parquet(cache, index=False)
            d += dt.timedelta(days=1)
        print(f"{area}: ferdig t.o.m. {end}")
        pd.concat(parts).to_parquet(cache, index=False)
    hourly = pd.concat(parts)
    hourly["maned"] = hourly["time_start"].str[:7]   # time_start er lokal tid med offset
    monthly = (hourly.groupby(["area", "maned"], as_index=False)
                     .agg(spot_nok_kwh=("NOK_per_kWh", "mean"),
                          spot_p90=("NOK_per_kWh", lambda x: x.quantile(0.9)),
                          n_timer=("NOK_per_kWh", "size")))
    monthly["spot_ore_kwh"] = monthly["spot_nok_kwh"] * 100
    monthly.to_parquet(PROC / "spot_month.parquet", index=False)
    print(monthly.tail())


if __name__ == "__main__":
    main()
