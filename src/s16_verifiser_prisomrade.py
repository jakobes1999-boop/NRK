"""Oppgave C: Verifiser kommune -> prisområde mot en uavhengig kilde.

Bakgrunn (se ARBEIDSLOGG.md, punkt C og geo.py sin docstring): det finnes ingen offisiell,
maskinlesbar tabell kommune->prisområde. src/geo.py bruker fylkesregel + NVEs vannkraftdatabase
(kraftverkenes ElspotomraadeNummer per (fylke, kommunenavn)) + to manuelle unntak. 27 kommuner
er overstyrt fra fylkesregelen av NVE-koblingen; disse var uverifisert mot en uavhengig kilde.

Forsøk på maskinlesbar kilde (dokumentert, ikke brukt til sluttresultatet):
  - Elhub sine egne datasett har KOMMUNE/KOMMUNENUMMER og PRISOMRÅDE som separate,
    IKKE koblede nedbrytninger (sjekket i data/raw/consumption_per_group_municipality_hour.csv.gz
    og consumption_per_group_mba_hour.csv.gz: forskjellige kolonner, ingen felles nøkkel per rad).
  - NVE Atlas' gamle GIS-tjeneste for elspotområder (gis3.nve.no/map/rest/services/Mapservices/
    Elspot/MapServer/0, lag "ElSpot_omraade") svarer 500 "Service ... not started" ved forsøk
    05.09.2026 – tjenesten er ikke i drift. Det nyere domenet "nve.geodataonline.no" som dukket
    opp i søk, finnes ikke (DNS-oppslag feiler) – stammer trolig fra en foreldet lenke.
  - Ingen treff på et ferdig GIS-lag eller CSV med kommune<->prisområde fra Statnett, RME eller
    Geonorge innenfor rimelig søkeinnsats.

Kilde brukt: VGs "Strømprisen" (www.vg.no/stromprisen/kommune/<slug>/), som for hver kommune
oppgir en entydig "Kommune: <navn> (NOx)"-kobling. VG oppgir selv kildene Statnett, Nasdaq,
Nord Pool, NVE, Entsoe og Enova for siden, og har en eksplisitt advarsel: "Noen områder langs
regiongrensene får strøm fra en annen region enn resten av kommunen. Sjekk gjerne med din
strømleverandør hvilken region du tilhører." – dvs. VG bekrefter selv at prisområder ikke alltid
følger kommunegrenser eksakt. Dette er en sekundærkilde (redaksjonelt bygget datasett), ikke en
offisiell forskrift-/registerkilde – se svakheter i md-rapporten.

Alle 27 overstyrte kommuner + de 2 manuelle unntakene (Bømlo/Sveio) ble sjekket enkeltvis i
nettleser 05.09.2026 (se kildeliste under). Resultatene er lagt inn her som en liten,
sporbar referansetabell (kommunenummer -> prisområde + URL), IKKE hentet automatisk
(siden er en client-rendered SvelteKit-app uten stabilt API egnet for automatisert nedlasting).
"""
import io
import pandas as pd
from config import OUT

HENTET = "2026-09-05"
VG_BASE = "https://www.vg.no/stromprisen/kommune/"

# knr (2024) -> (kommune, prisområde ifølge VG, URL-slug brukt, bekreftet)
VG_KILDE = {
    "3320": ("Flå", "NO5", "flå", True),
    "3322": ("Nesbyen", "NO5", "nesbyen", True),
    "3324": ("Gol", "NO5", "gol", True),
    "3326": ("Hemsedal", "NO5", "hemsedal", True),
    "3328": ("Ål", "NO5", "ål", True),
    "3330": ("Hol", "NO5", "hol", True),
    "3431": ("Dovre", "NO3", "dovre", True),
    "3432": ("Lesja", "NO3", "lesja", True),
    "3433": ("Skjåk", "NO3", "skjåk", True),
    "3434": ("Lom", "NO3", "lom", True),
    "3435": ("Vågå", "NO3", "vågå", True),
    "3437": ("Sel", None, "sel", False),  # VG-siden ga 404 på slugen "sel" og "sel-kommune"; ikke funnet 05.09.2026
    "4602": ("Kinn", "NO3", "kinn", True),
    "4611": ("Etne", "NO2", "etne", True),
    "4614": ("Stord", "NO2", "stord", True),
    "4615": ("Fitjar", "NO2", "fitjar", True),
    "4616": ("Tysnes", "NO2", "tysnes", True),
    "4637": ("Hyllestad", "NO3", "hyllestad", True),
    "4645": ("Askvoll", "NO3", "askvoll", True),
    "4646": ("Fjaler", "NO3", "fjaler", True),
    "4647": ("Sunnfjord", "NO3", "sunnfjord", True),
    "4648": ("Bremanger", "NO3", "bremanger", True),
    "4649": ("Stad", "NO3", "stad", True),
    "4650": ("Gloppen", "NO3", "gloppen", True),
    "4651": ("Stryn", "NO3", "stryn", True),
    "5042": ("Lierne", "NO4", "lierne", True),
    "5044": ("Namsskogan", "NO4", "namsskogan", True),
    "4612": ("Sveio", "NO2", "sveio", True),   # manuelt unntak i geo.py (Sunnhordland)
    "4613": ("Bømlo", "NO2", "bømlo", True),   # manuelt unntak i geo.py (Sunnhordland)
}


def main():
    tab = pd.read_csv(OUT / "tab_kommune_prisomrade.csv", dtype={"knr": str})
    panel_knr = set()
    try:
        panel = pd.read_parquet("../data/processed/panel.parquet")
        panel_knr = set(panel.knr.astype(str).str.zfill(4))
    except Exception:
        try:
            panel = pd.read_parquet("data/processed/panel.parquet")
            panel_knr = set(panel.knr.astype(str).str.zfill(4))
        except Exception as e:
            print(f"Advarsel: fant ikke panel.parquet ({e}); i_panel blir False for alle.")

    rows = []
    for knr, (navn, pa_vg, slug, bekreftet) in VG_KILDE.items():
        our = tab.loc[tab.knr == knr]
        if our.empty:
            continue
        our = our.iloc[0]
        url = VG_BASE + slug + "/"
        if not bekreftet:
            samsvar = "ikke_verifisert"
        elif our.prisomrade == pa_vg:
            samsvar = "samsvar"
        else:
            samsvar = "AVVIK"
        rows.append({
            "knr": knr,
            "kommune": our.kommune,
            "var_pa": our.prisomrade,
            "var_pa_kilde": our.pa_kilde,
            "kilde_pa": pa_vg if pa_vg else "",
            "kilde_url": url,
            "kilde_hentet": HENTET,
            "i_panel": knr in panel_knr,
            "samsvar": samsvar,
        })
    ver = pd.DataFrame(rows).sort_values("knr")
    ver.to_csv(OUT / "tab_prisomrade_verifisering.csv", index=False, encoding="utf-8")

    n_samsvar = (ver.samsvar == "samsvar").sum()
    n_avvik = (ver.samsvar == "AVVIK").sum()
    n_uverifisert = (ver.samsvar == "ikke_verifisert").sum()
    n_i_panel = ver.i_panel.sum()

    md = io.StringIO()
    md.write("# Verifisering av kommune -> prisområde (oppgave C)\n\n")
    md.write(f"Hentet/sjekket: {HENTET}. Skript: `src/s16_verifiser_prisomrade.py`. "
             "Endrer ikke `src/geo.py` eller panelet – kun rapportering.\n\n")

    md.write("## Metode og kilder\n\n")
    md.write(
        "Det finnes ingen offisiell, maskinlesbar tabell kommune->prisområde i Norge "
        "(prisområder følger overføringsnettets kapasitetsgrenser, ikke administrative "
        "kommunegrenser). Tre maskinlesbare kandidater ble undersøkt og forkastet:\n\n"
        "1. **Elhub** (data.elhub.no): `consumption_per_group_municipality_hour` har "
        "KOMMUNE/KOMMUNENUMMER, `consumption_per_group_mba_hour` har PRISOMRÅDE – men dette er "
        "to separate nedbrytninger uten felles rad-nøkkel. Elhub publiserer ikke en egen "
        "kommune<->prisområde-koblingstabell (sjekket i datakatalogen, https://dok.elhub.no/data/"
        "Datasett.835354661.html, 05.09.2026).\n"
        "2. **NVE Atlas / GIS3** (`https://gis3.nve.no/map/rest/services/Mapservices/Elspot/"
        "MapServer/0`, lag `ElSpot_omraade`): tjenesten svarte `{\"error\":{\"code\":500,"
        "\"message\":\"Service Mapservices/Elspot/MapServer not started \"}}` ved gjentatte forsøk "
        "05.09.2026 – ikke i drift. Domenet `nve.geodataonline.no` som også dukket opp i søk "
        "finnes ikke (DNS-oppslag feiler).\n"
        "3. **Geonorge/Statnett/RME**: ingen ferdig nedlastbart GIS-lag eller CSV med "
        "kommune<->prisområde ble funnet innenfor rimelig søkeinnsats.\n\n"
        "Kilden som faktisk ble brukt er **VGs «Strømprisen»** "
        "(`https://www.vg.no/stromprisen/kommune/<kommune>/`), som for hver norsk kommune "
        "oppgir en entydig kobling «Kommune: <navn> (NOx)». Siden oppgir selv kildene "
        "**Statnett, Nasdaq, Nord Pool, NVE, Entsoe og Enova**. Dette er en redaksjonell/"
        "sekundær kilde, ikke en offisiell forskrift eller et primært register – men den "
        "bygger uttalt på de samme primærkildene (Statnett/NVE) som resten av norsk "
        "kraftprisjournalistikk, og er uavhengig konstruert av geo.py sin NVE-kraftverk-baserte "
        "kobling. VG-siden advarer selv eksplisitt: «Noen områder langs regiongrensene får "
        "strøm fra en annen region enn resten av kommunen. Sjekk gjerne med din strømleverandør "
        "hvilken region du tilhører.» – dvs. VG bekrefter at prisområde-grensen ikke alltid "
        "følger kommunegrensen eksakt (se eget avsnitt under).\n\n"
        "Alle 27 overstyrte kommuner (pa_kilde=\"nve\" i `tab_kommune_prisomrade.csv`) og de "
        "2 manuelle unntakene (pa_kilde=\"unntak\": Bømlo, Sveio) ble sjekket enkeltvis i "
        "nettleser 05.09.2026 – se URL-liste i `tab_prisomrade_verifisering.csv`. Siden er en "
        "client-rendered SvelteKit-app uten stabilt offentlig API; oppslagene ble derfor gjort "
        "manuelt (én per kommune), IKKE med et automatisert nedlastingsskript. De 99 kommunene "
        "med ren fylkesregel (pa_kilde=\"fylke\") og de 229 der fylke og NVE er enige "
        "(pa_kilde=\"fylke=nve\") er IKKE sjekket mot VG i denne runden (for stort omfang for "
        "manuell sjekk) – kontrollen er avgrenset til de kommunene der geo.py faktisk overstyrer "
        "eller gjør unntak, som er de eneste med reell risiko for feil.\n\n"
    )

    md.write("## Resultat\n\n")
    md.write(f"- Sjekket: {len(ver)} kommuner (27 NVE-overstyringer + 2 manuelle unntak)\n")
    md.write(f"- Samsvar med VG: **{n_samsvar}**\n")
    md.write(f"- Avvik: **{n_avvik}**\n")
    md.write(f"- Ikke verifisert (fant ingen VG-side): **{n_uverifisert}**\n")
    md.write(f"- Herav i panelet (`data/processed/panel.parquet`, 197 kommuner NO1/NO2/NO5): "
             f"**{n_i_panel}**\n\n")

    if n_avvik:
        md.write("### Avvik\n\n")
        md.write(ver.loc[ver.samsvar == "AVVIK",
                          ["knr", "kommune", "var_pa", "kilde_pa", "kilde_url"]
                          ].to_markdown(index=False))
        md.write("\n\n")
    else:
        md.write("### Avvik\n\nIngen avvik funnet: alle 28 kommuner som ble bekreftet mot VG "
                 "stemmer overens med `tab_kommune_prisomrade.csv`.\n\n")

    md.write("### Ikke verifisert\n\n")
    uv = ver.loc[ver.samsvar == "ikke_verifisert", ["knr", "kommune", "var_pa", "var_pa_kilde"]]
    if len(uv):
        md.write(uv.to_markdown(index=False))
        md.write(
            "\n\nSel (3437) ga 404 på VGs kommune-URL (både «sel» og «sel-kommune» ble "
            "forsøkt 05.09.2026); ikke lykkes å få tak i riktig URL-slug innenfor rimelig "
            "innsats. Indirekte støtte: Sel ligger midt i Nord-Gudbrandsdal, og alle de fem "
            "nabokommunene i samme NVE-overstyrte gruppe (Dovre, Lesja, Skjåk, Lom, Vågå) er "
            "bekreftet NO3 mot VG, og NVEs egen regionbeskrivelse (sitert i søk 05.09.2026) "
            "plasserer eksplisitt «Innlandet vest og nord for Vågåmo» i NO3 – som også "
            "omfatter Sel. `prisomrade=NO3` for Sel i `tab_kommune_prisomrade.csv` anses "
            "derfor som sannsynlig riktig, men er ikke direkte bekreftet mot en uavhengig "
            "kilde.\n\n"
        )
    else:
        md.write("Ingen.\n\n")

    md.write("## De 12 overstyrte/unntaks-kommunene som faktisk inngår i panelet\n\n")
    md.write(
        "Av de 29 sjekkede kommunene er det disse 12 som har prisområde NO1/NO2/NO5 og dermed "
        "faktisk påvirker analysen i `data/processed/panel.parquet` (resten – NO3/NO4 – er "
        "utenfor NRK/OEs analyseområde):\n\n"
    )
    ip = ver.loc[ver.i_panel, ["knr", "kommune", "var_pa", "var_pa_kilde", "samsvar"]]
    md.write(ip.to_markdown(index=False))
    md.write("\n\n")

    md.write("## Kommuner delt mellom prisområder\n\n")
    md.write(
        "VGs egen tekst på forsiden av Strømprisen (https://www.vg.no/stromprisen/, hentet "
        f"{HENTET}) sier eksplisitt: «Noen områder langs regiongrensene får strøm fra en "
        "annen region enn resten av kommunen. Sjekk gjerne med din strømleverandør hvilken "
        "region du tilhører.» Dette bekrefter at prisområde-grensen ikke alltid følger "
        "kommunegrensen eksakt – men VG oppgir ingen liste over hvilke kommuner dette gjelder, "
        "og det ble ikke funnet noen slik liste hos NVE/Statnett/RME innenfor søkeinnsatsen i "
        "denne runden. `src/geo.py` sin egen NVE-kraftverk-kobling har samme svakhet innebygd: "
        "når et kraftverk-datasett gir `n_omrader > 1` for en kommune (flere kraftverk i "
        "forskjellige prisområder), faller koblingen tilbake til fylkesregelen i stedet for å "
        "velge riktig område for forbrukssiden – se `nve_area_by_name()` i geo.py "
        "(`pa_nve == \"flere\"` behandles ikke som entydig). Ingen av de 197 kommunene i "
        "panelet er identifisert som delt i denne runden, men muligheten er ikke uttømmende "
        "utelukket.\n\n"
    )

    md.write("## Hva som IKKE ble verifisert\n\n")
    md.write(
        "- De 99 kommunene med ren fylkesregel og de 229 der fylke og NVE-kobling er enige "
        "(`pa_kilde` i {\"fylke\", \"fylke=nve\"}) – ikke sjekket mot en uavhengig kilde i "
        "denne runden.\n"
        "- Sel (3437), se over.\n"
        "- Om noen av de 197 panelkommunene er reelt delt mellom to prisområder (VGs "
        "grenseadvarsel over) – ingen autoritativ liste funnet.\n"
        "- VGs egen kobling er ikke en offisiell/forskriftsmessig kilde; den er inkludert fordi "
        "den er den eneste kommune-for-kommune-kilden som faktisk ble funnet, og fordi den er "
        "uavhengig av NVE-kraftverk-metoden i geo.py. Den bør behandles som en sterk, men ikke "
        "endelig, bekreftelse.\n"
    )

    with open(OUT / "tab_prisomrade_verifisering.md", "w", encoding="utf-8") as f:
        f.write(md.getvalue())

    print(f"Skrevet: {OUT / 'tab_prisomrade_verifisering.csv'}")
    print(f"Skrevet: {OUT / 'tab_prisomrade_verifisering.md'}")
    print(f"Samsvar: {n_samsvar}, avvik: {n_avvik}, ikke verifisert: {n_uverifisert}, i panel: {n_i_panel}")


if __name__ == "__main__":
    main()
