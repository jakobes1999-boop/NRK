# Etterprøving av NRK «Prisen for billig strøm»

Reproduserbar etterprøving av NRKs analyse (nrk.no, 27.08.2026) av hvordan Norgespris påvirket
husholdningenes strømforbruk, og av regnestykket «1 kWh = 1 429 liter vann». Artikkelen ligger i
`kilder/`. Arbeidslogg i `ARBEIDSLOGG.md`, kritikk i `notat/KRITIKK_2026-09-05.md`.

## Oppsett

```bash
py -m pip install -r requirements.txt
# .env i prosjektroten: FROST_CLIENT_ID=...   (gratis: https://frost.met.no/auth/requestCredentials.html)
py run_all.py                     # alt; nedlasting tar ~40 min (Frost ~15, spot ~20, Elhub ~5)
py run_all.py --skip-download     # bare analyse på data som ligger i data/
```

## Steg

| Skript | Gjør | Kilde |
|---|---|---|
| `s01_download_elhub.py` | Forbruk per kommune/gruppe/time → måned; Norgespris-målere per kommune; forbruk etter bestillingsstatus | data.elhub.no (CC BY 4.0), gzip, `;`, desimalkomma |
| `s02_download_ssb.py` | Medianinntekt etter skatt (06944), boliger etter bruksareal (06513), omkodet til 2024-kommuner via Klass 131 | SSB PxWebApi v2 (JSON-stat2) |
| `s03_download_prices.py` | Spotpris per time NO1/NO2/NO5 → månedssnitt, fra des. 2021 | hvakosterstrommen.no |
| `s04_download_frost.py` | Døgnmiddeltemperatur → energigradtall (17 °C) per kommune og måned; stasjoner i NO1/NO2/NO5-fylker | MET Frost |
| `s05_nve_energiekvivalent.py` | Produksjonsveid energiekvivalent NO1+NO2 → liter per kWh | NVE vannkraftdatabase |
| `s06_build_panel.py` | Kommune × måned-panel (197 kommuner, feb 2022–apr 2026); `--fylke` gir robusthetsvariant uten NVE-kobling | `geo.py` |
| `s07_estimate_fe.py` | M1 NRK-lik, M2 + sesong, M3/M4 to-veis FE med andel, M5 placebo; per målepunkt-varianter; Driscoll-Kraay-SE | linearmodels |
| `s08_did_orderstatus.py` | DiD bestilt vs. ikke bestilt innen EAC-gruppe; nivå før, event-study (ujustert) | statsmodels |
| `s10_forbedret_modell.py` | Modeller som tar høyde for NRKs svakheter: F1–F7 (kommunepanel, husholdningsandel, egd×kommune, placebo, event-study) og D1–D6 (DiD sesongjustert, tidlig/sent, placebo) | |
| `s12_kritikk2_beregninger.py` | Beregninger fra kritikkrunde 2: fyringssesong, D7 (område×måned×EAC-FE), forbruksandel, dekomponering | |
| `s13_dose_sent.py` | Dose-respons for «Bestilt sent»: behandlingsandel per måned fra daglige tellinger; E0–E6 med felles og kohortspesifikk sesongprofil, simulert nullverdi, bootstrap, placebo, figur | Elhub-wiki (definisjon tidlig/sent) |
| `s13b_dose_robusthet.py` | Dosegrenser for kohorten, gradtall per kohort, leads | |
| `s14_wild_bootstrap.py` + `wcb.py` | Wild cluster bootstrap (WCR, Rademacher/Webb) for DiD-termer | |
| `s15_effektiv_pris.py` | Effektiv marginalpris med strømstøtte per område × måned; M1e/M2e/F2e/prisgap | timespot, `kilder/stromstotte_parametre.md` |
| `s16_verifiser_prisomrade.py` | Kommune→prisområde mot VG «Strømprisen» (sekundærkilde); kjøres separat | vg.no |
| `s17_nettoeksport.py` | Elektrisitetsbalanse månedlig, nettoeksport jan–jun per år | SSB 14091 |
| `s11_nrk_pastander.py` | Etterprøver «20 000 år dusj», dusjpris, inntekt↔oppslutning | |
| `vann_dusj.py` | Dusj- og vannregnestykket | |
| `s09_til_godkjenning.py` | Samler alle tall i `output/TIL_GODKJENNING.md` | |

Resultater i `output/` (CSV, PNG, logger). Notatet `notat/notat_etterproving.md` fylles først
etter at tallene i `TIL_GODKJENNING.md` er godkjent.

## Kjente forbehold

1. **Kommune→prisområde** har ingen offisiell kilde. 28 av 29 overstyrte kommuner bekreftet mot VG «Strømprisen» 05.09.2026 (`output/tab_prisomrade_verifisering.md`). `geo.py`: fylkesregel + NVE-kraftverkenes område per
   (fylkesnr, kommunenavn) + to manuelle unntak (Bømlo, Sveio). 27 kommuner overstyres; se
   `output/tab_kommune_prisomrade.csv`. Ikke verifisert mot Statnett/nettselskap.
2. **Elhub-gruppen «Privat»** = husholdning + hytte. Husholdningsandel Norgespris brukes som primær
   behandlingsvariabel (s10); Privat-andel er robusthet.
3. **Inntekt** finnes t.o.m. 2024 og framskrives; innen kommune-FE fanger den trend.
4. **Periode:** panelet er feb 2022–apr 2026 (Elhub kommunefil); NRK oppgir 2021–juni 2026.
5. **Anonymisering:** Norgespris-tall for < 100 målere er 0.
6. **Strømstøtte** er modellert som effektiv marginalpris i s15; NRK-lik koeffisient faller 9,1 → 8,7 prosent.
7. **DiD** har 27 klustre; wild cluster bootstrap i s14. Hovedtermer overlever; E6 Lav sent_dose gjør det ikke.
8. **Tidlig/sent:** tidlig = bestilt t.o.m. 01.10.2025, sent = 02.10.2025–30.04.2026 (Elhub-wiki, `kilder/elhub_wiki_norgespris_status.txt`). Norgespris
   gjelder fra bestillingsdagen; sent-gruppens behandlingsandel per måned i `output/tab_dose_sent.csv`. Statusuttrekket er en fast kohort
   (1,26 mill. målere, 43 prosent sene) mens dosen er fra alle husholdningsmålere (55 prosent sene utenfor kohorten).
   Kohortene har ulik sesongprofil også før ordningen; dose-resultatene er forenlige med en behandlingseffekt men avgjør ikke (KRITIKK3).

## Reproduksjon fra GitHub

Repoet https://github.com/jakobes1999-boop/NRK inneholder all kode, de bearbeidede datasettene
(`data/processed/`, 8 MB) og de små rådatafilene, slik at `py run_all.py --skip-download`
reproduserer alle tabeller i `output/` uten nettilgang. Ikke i repoet:

- **Store rådata** (Elhubs kommunefil, 509 MB, og statusuttrekket, 61 MB). Lastes ned med
  `py src/s01_download_elhub.py`; eksakte filnavn står i `src/config.py` (`ELHUB_FILES`).
  SSB-, Frost- og NVE-rådata lastes med s02, s04 og s05. Frost krever gratis klient-ID i `.env`
  (`FROST_CLIENT_ID`, `FROST_CLIENT_SECRET`).
- **NRKs artikkel** (opphavsrett). Metodeboksen er sitert i `notat/`; artikkelen ligger på
  nrk.no («Prisen for billig strøm», 27.08.2026).
- **Elhubs analyse** «Hvor mye av strømforbruket er knyttet til Norgespris?» (23.01.2026):
  https://elhub.no/artikler/hvor-mye-av-stromforbruket-er-knyttet-til-norgespris. Tekstutdrag i
  `kilder/elhub_analyse_forbruk_norgespris_2026-01.txt`.
- Utkast til debattinnlegg og Word-filer.

Datalisenser: Elhub CC BY 4.0; SSB CC BY 4.0; MET Frost CC BY 4.0; NVE NLOD; hvakosterstrommen.no
fri bruk med kreditering. Alle tall i `output/` og `notat/` er merket «til godkjenning» der de ikke
er gjennomgått. Tallene er ikke NRKs tall.
