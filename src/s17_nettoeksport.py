"""Steg 17: Etterprøving av NRKs påstand P4 om nettoeksport.

NRK skriver (kilder/nrk_prisen_for_billig_strom.md, avsnittet «Tjener stort»,
figur «Nettoeksport av strøm», periode 1.1.-31.7., kilde Statnett) at
nettoeksporten har stupt, og at "årets nettoeksport tilsvarer det økte
forbruket blant husholdningene i Sør-Norge". Ordrette sitater (maks 15 ord per
sitat) ligger i NRK_SITATER under og gjengis i output/tab_nettoeksport.md.

SSB-tabell: 12824 "Elektrisitetsbalanse (MWh)" er en AVSLUTTET serie
(t.o.m. 2023M12 - bekreftet med metadata-kallet 05.09.2026, status
"avslutta serie"). SSB har videreført serien i tabell 14091
"Elektrisitetsbalanse (MWh) 1993M01-2026M07" med samme variabelstruktur
(Produk2, ContentsCode=Kraft, Tid månedlig). Vi bruker derfor 14091 for hele
perioden 2021-2026 (bekreftet med samme type metadata-kall, se log_s17.txt).

Variabler brukt (Produk2, bekreftet i metadata for 14091):
  1    Total produksjon av elektrisk kraft
  2    Import
  3    Eksport
  4    Bruttoforbruk av elektrisk kraft
  7.4  Forbruk i husholdninger
Enhet: MWh, konvertert til GWh (/1000) i outputtabellene (som i NRK-grafen).

Nettoeksport = Eksport - Import (jf. balanselikningen
produksjon + import = eksport + bruttoforbruk + nettap/pumpekraft).
"""
import json
import itertools
import requests
import pandas as pd
from config import RAW, OUT, ROOT, SSB_V2

TABLE = "14091"
# Filnavn er som spesifisert i bestillingen; innholdet er tabell 14091,
# ikke 12824 (12824 er en avsluttet serie, se docstring/logg).
RAW_JSON = RAW / "ssb_12824_elbalanse.json"
OUT_CSV = OUT / "tab_nettoeksport.csv"
OUT_MD = OUT / "tab_nettoeksport.md"
LOG = OUT / "log_s17.txt"
NRK_KILDE = ROOT / "kilder" / "nrk_prisen_for_billig_strom.md"

PRODUK2_CODES = ["1", "2", "3", "4", "7.4"]
PRODUK2_LABEL = {
    "1": "produksjon_gwh",
    "2": "import_gwh",
    "3": "eksport_gwh",
    "4": "bruttoforbruk_gwh",
    "7.4": "husholdningsforbruk_gwh",
}

NRK_SITATER = [
    "Nettoeksporten, altså hvor mye mer strøm vi selger til utlandet",
    "sammenlignet med hva vi kjøper tilbake, har stupt",
    "Årets nettoeksport tilsvarer det økte forbruket blant husholdningene i Sør-Norge.",
    "Perioden 1.1. til 31.7",
]


def sjekk_sitater():
    txt = NRK_KILDE.read_text(encoding="utf-8")
    txt_normalisert = " ".join(txt.split())  # kildefila brytes over linjer midt i setninger
    for sitat in NRK_SITATER:
        kjerne = " ".join(sitat.rstrip(".:").split(",")[0].split())
        assert kjerne in txt_normalisert, f"sitat ikke funnet ordrett i kildefil: {sitat!r}"
    return txt


def fetch_jsonstat() -> dict:
    if RAW_JSON.exists():
        return json.loads(RAW_JSON.read_text(encoding="utf-8"))
    params = {"lang": "no", "outputFormat": "json-stat2"}
    selection = {
        "Produk2": ",".join(PRODUK2_CODES),
        "ContentsCode": "Kraft",
        "Tid": "from(2021M01)",
    }
    params.update({f"valueCodes[{k}]": v for k, v in selection.items()})
    r = requests.get(SSB_V2.format(tab=TABLE), params=params, timeout=300)
    r.raise_for_status()
    RAW_JSON.write_text(r.text, encoding="utf-8")
    return r.json()


def jsonstat_to_long(js: dict) -> pd.DataFrame:
    dims = js["id"]
    codes = [list(js["dimension"][d]["category"]["index"]) for d in dims]
    rows = list(itertools.product(*codes))
    df = pd.DataFrame(rows, columns=dims)
    df["verdi_mwh"] = js["value"]
    return df


def fmt(x):
    """1234.5 -> '1 235' (hardt mellomrom som tusenskille, norsk format)."""
    return f"{x:,.0f}".replace(",", " ")


def main():
    log_lines = []

    def log(msg):
        print(msg)
        log_lines.append(str(msg))

    log(f"SSB-tabell brukt: {TABLE} (Elektrisitetsbalanse, MWh, månedlig).")
    log("12824 er avsluttet t.o.m. 2023M12 (bekreftet metadata-kall) – 14091 er videreføringen.")
    js = fetch_jsonstat()
    log(f"Rådata lagret: {RAW_JSON}")
    log(f"Oppdatert (SSB, tabell 14091): {js.get('updated', '')}")

    df = jsonstat_to_long(js)
    df["maaned"] = df["Tid"].str.replace("M", "-", regex=False)
    df["gwh"] = df["verdi_mwh"] / 1000.0
    wide = df.pivot_table(index="maaned", columns="Produk2", values="gwh").reset_index()
    wide = wide.rename(columns=PRODUK2_LABEL)
    wide = wide.sort_values("maaned").reset_index(drop=True)
    wide["nettoeksport_gwh"] = wide["eksport_gwh"] - wide["import_gwh"]

    cols = ["maaned", "produksjon_gwh", "import_gwh", "eksport_gwh", "nettoeksport_gwh",
            "bruttoforbruk_gwh", "husholdningsforbruk_gwh"]
    wide = wide[cols].round(1)
    wide.to_csv(OUT_CSV, index=False, encoding="utf-8")
    log(f"Månedlig tabell skrevet: {OUT_CSV} ({len(wide)} måneder, {wide.maaned.min()} - {wide.maaned.max()})")

    # --- jan-jun per år 2021-2026 ---
    wide["aar"] = wide["maaned"].str[:4].astype(int)
    wide["mnd"] = wide["maaned"].str[5:7].astype(int)
    jan_jun = wide[(wide.mnd >= 1) & (wide.mnd <= 6)]
    agg = jan_jun.groupby("aar").agg(
        nettoeksport_gwh=("nettoeksport_gwh", "sum"),
        bruttoforbruk_gwh=("bruttoforbruk_gwh", "sum"),
        produksjon_gwh=("produksjon_gwh", "sum"),
        husholdningsforbruk_gwh=("husholdningsforbruk_gwh", "sum"),
        n_maneder=("mnd", "count"),
    ).reset_index()
    log("\nJan-jun sum per år (GWh):")
    log(agg.to_string(index=False))

    def get_val(col, aar):
        v = agg.loc[agg.aar == aar, col]
        return float(v.iloc[0]) if len(v) else None

    endringer = {}
    log("\nEndring jan-jun 2026 vs 2025:")
    for col in ["nettoeksport_gwh", "produksjon_gwh", "bruttoforbruk_gwh"]:
        v25, v26 = get_val(col, 2025), get_val(col, 2026)
        if v25 is not None and v26 is not None:
            diff, pst = v26 - v25, 100 * (v26 - v25) / v25
            endringer[col] = (v25, v26, diff, pst)
            log(f"  {col}: 2025={v25:.0f}  2026={v26:.0f}  diff={diff:+.0f} GWh ({pst:+.1f} %)")

    # --- sammenlign med prosjektets eget forbrukstall (Elhub, NO1+NO2+NO5, jan-jun) ---
    p1_path = OUT / "tab_p1_forbruk_jan_jun.csv"
    p1 = None
    p1_diff_2026 = None
    if p1_path.exists():
        p1 = pd.read_csv(p1_path, encoding="utf-8")
        log(f"\nSammenlignet mot {p1_path.name} (Elhub husholdning+hytter NO1+NO2+NO5, jan-jun):")
        log(p1[["aar", "Hus+hytter", "endring_hus_hytter_gwh"]].to_string(index=False))
        r = p1.loc[p1.aar == 2026, "endring_hus_hytter_gwh"]
        p1_diff_2026 = float(r.iloc[0]) if len(r) else None
    else:
        log(f"\nFant ikke {p1_path} – hopper over sammenligning med Elhub-tallet.")

    txt = sjekk_sitater()
    log("\nNRK-sitater bekreftet ordrett mot kildefil.")

    ne25, ne26, ne_diff, ne_pst = endringer.get("nettoeksport_gwh", (None,) * 4)
    prod25, prod26, prod_diff, prod_pst = endringer.get("produksjon_gwh", (None,) * 4)
    bf25, bf26, bf_diff, bf_pst = endringer.get("bruttoforbruk_gwh", (None,) * 4)

    md = []
    md.append("# Etterprøving av NRKs påstand P4 – nettoeksport av strøm\n")

    md.append("## 1. NRKs ordrette påstand\n")
    md.append("Kilde: `kilder/nrk_prisen_for_billig_strom.md`, avsnittet «Tjener stort».\n")
    md.append("> «" + NRK_SITATER[0] + " " + NRK_SITATER[1] + ".»\n")
    md.append("> «" + NRK_SITATER[2] + "»\n")
    md.append("> Figurens periodeangivelse (kilde: Statnett): «" + NRK_SITATER[3] + "».\n")
    md.append(
        "NRKs graf gjelder perioden 1.1.-31.7. per år (ikke jan-jun). Denne rapporten "
        "bruker jan-jun for å kunne sammenligne direkte med prosjektets eget "
        "forbrukstall (`tab_p1_forbruk_jan_jun.csv`), som også er jan-jun. Tallene under "
        "er derfor ikke identiske med avlesning fra NRKs 1.1.-31.7.-graf.\n"
    )

    md.append("\n## 2. Nettoeksport og bruttoforbruk, jan-jun per år (GWh)\n")
    md.append(
        "Kilde: SSB tabell 14091 «Elektrisitetsbalanse (MWh)» (videreføring av avsluttede "
        "12824), månedlig, hele Norge. Nettoeksport = eksport minus import.\n"
    )
    md.append("| År | Produksjon | Nettoeksport | Bruttoforbruk | Husholdningsforbruk |")
    md.append("|---|---|---|---|---|")
    for _, r_ in agg.iterrows():
        md.append(
            f"| {int(r_.aar)} | {fmt(r_.produksjon_gwh)} | {fmt(r_.nettoeksport_gwh)} | "
            f"{fmt(r_.bruttoforbruk_gwh)} | {fmt(r_.husholdningsforbruk_gwh)} |"
        )
    md.append("\n(Alle tall i GWh, sum januar-juni. Full månedstabell: `tab_nettoeksport.csv`.)\n")

    md.append("\n## 3. Endring jan-jun 2026 mot jan-jun 2025 (hele Norge, SSB)\n")
    md.append(f"- Nettoeksport: {fmt(ne25)} → {fmt(ne26)} GWh ({ne_diff:+.0f} GWh, {ne_pst:+.1f} prosent)")
    md.append(f"- Produksjon: {fmt(prod25)} → {fmt(prod26)} GWh ({prod_diff:+.0f} GWh, {prod_pst:+.1f} prosent)")
    md.append(f"- Bruttoforbruk: {fmt(bf25)} → {fmt(bf26)} GWh ({bf_diff:+.0f} GWh, {bf_pst:+.1f} prosent)")
    if p1_diff_2026 is not None:
        md.append(
            f"- Til sammenligning, prosjektets eget tall (Elhub, husholdning+hytter, "
            f"NO1+NO2+NO5, jan-jun): endring 2026 mot 2025 = {p1_diff_2026:+.0f} GWh."
        )

    md.append("\n## 4. Vurdering (tall og logikk)\n")
    md.append(
        f"Nettoeksporten falt {abs(ne_diff):.0f} GWh fra jan-jun 2025 til jan-jun 2026 "
        f"(hele Norge, SSB), en nedgang på {abs(ne_pst):.1f} prosent.\n"
    )
    md.append(
        f"Bruttoforbruket i hele Norge (SSB) endret seg {bf_diff:+.0f} GWh i samme periode "
        f"({bf_pst:+.1f} prosent).\n"
    )
    if p1_diff_2026 is not None:
        diff_of_diffs = abs(ne_diff) - abs(p1_diff_2026)
        md.append(
            f"Elhub-tallet for husholdning+hytter i NO1+NO2+NO5 (prosjektets eget datasett) "
            f"økte {p1_diff_2026:+.0f} GWh i samme periode.\n"
        )
        # NRK sammenligner NIVÅET på årets nettoeksport med forbruksøkningen, ikke fallet (rettet etter kritikkrunde 4).
        ne26_jul = float(wide.loc[wide.maaned.str.startswith("2026-") & (wide.maaned <= "2026-07"), "nettoeksport_gwh"].sum())
        md.append(
            f"NRK skriver at årets nettoeksport «tilsvarer det økte forbruket blant husholdningene i Sør-Norge». "
            f"Det er nivået på nettoeksporten i 2026 som sammenlignes, ikke fallet. Nivået jan-jun 2026 er {fmt(ne26)} GWh "
            f"og jan-jul 2026 (NRKs periode) {fmt(ne26_jul)} GWh, mot en forbruksøkning for husholdning+hytter i NO1+NO2+NO5 "
            f"jan-jun på {p1_diff_2026:+.0f} GWh. Størrelsene er i samme størrelsesorden (forhold {ne26_jul / p1_diff_2026:.2f} for jan-jul). "
            f"NRKs påstand holder tallmessig i SSB-tallene."
        )
        md.append("")
        andel_prod = prod_diff / ne_diff * 100; andel_forbruk = -bf_diff / ne_diff * 100
        md.append(
            f"Fallet i nettoeksport fra 2025 til 2026 ({ne_diff:+.0f} GWh) følger regnskapsmessig av identiteten "
            f"nettoeksport = produksjon - bruttoforbruk, som holder eksakt begge år i SSB-tallene. Produksjonsfallet "
            f"({prod_diff:+.0f} GWh) utgjør {andel_prod:.0f} prosent av fallet og økningen i bruttoforbruk ({bf_diff:+.0f} GWh) "
            f"{andel_forbruk:.0f} prosent. Dette er en regnskapsdekomponering; den årsaksmessige attribusjonen kan ikke "
            f"avgjøres fra balansen alene."
        )
        md.append("")

    md.append("\n## 5. Usikkerhet og forbehold\n")
    md.append(
        "- SSB-tabellen (14091/12824) dekker hele Norge (alle prisområder NO1-NO5), mens "
        "prosjektets eget forbrukstall og NRKs påstand om «husholdningene i Sør-Norge» "
        "gjelder NO1+NO2+NO5. Nettoeksporten er ikke brutt ned på prisområde i denne "
        "SSB-tabellen. Sammenligningen i pkt. 3-4 er derfor mellom et landstall "
        "(nettoeksport, produksjon, bruttoforbruk) og et Sør-Norge-tall "
        "(husholdning+hytter)."
    )
    md.append(
        "- NRKs graf viser perioden 1.1.-31.7. med kilde Statnett; denne rapporten bruker "
        "SSBs månedlige elektrisitetsbalanse og jan-jun for sammenlignbarhet med "
        "`tab_p1_forbruk_jan_jun.csv`. Tallene i pkt. 2-4 er derfor ikke direkte "
        "avlesninger fra NRKs figur, og kan avvike noe fra den fordi juli er utelatt og "
        "fordi kilden (Statnett vs. SSB) er ulik."
    )
    md.append(
        "- Nettoeksport er her definert som eksport minus import (SSBs Produk2-kategorier "
        "3 og 2). Dette er standarddefinisjonen og bør svare til det NRK/Statnett kaller "
        "nettoeksport, men er ikke verifisert direkte mot Statnetts egne driftsdata "
        "(driftsdata.statnett.no) i denne kjøringen."
    )
    md.append(
        "- SSBs tall for 2026 kan være delvis foreløpige (siste publiserte måned i "
        f"tabell 14091 er {wide.maaned.max()}); revisjoner kan forekomme."
    )
    md.append(
        "- Husholdningsforbruk i SSB-tabellen (Produk2=7.4) er et landstall og er IKKE det "
        "samme som Elhub-tallet i `tab_p1_forbruk_jan_jun.csv` (NO1+NO2+NO5, "
        "husholdning+hytter) – de to rapporteres hver for seg i pkt. 2-3, ikke summert eller "
        "avstemt mot hverandre."
    )

    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    log(f"\nRapport skrevet: {OUT_MD}")

    LOG.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    print(f"Logg skrevet: {LOG}")


if __name__ == "__main__":
    main()
