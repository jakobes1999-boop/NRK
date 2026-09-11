# Verifisering av kommune -> prisområde (oppgave C)

Hentet/sjekket: 2026-09-05. Skript: `src/s16_verifiser_prisomrade.py`. Endrer ikke `src/geo.py` eller panelet – kun rapportering.

## Metode og kilder

Det finnes ingen offisiell, maskinlesbar tabell kommune->prisområde i Norge (prisområder følger overføringsnettets kapasitetsgrenser, ikke administrative kommunegrenser). Tre maskinlesbare kandidater ble undersøkt og forkastet:

1. **Elhub** (data.elhub.no): `consumption_per_group_municipality_hour` har KOMMUNE/KOMMUNENUMMER, `consumption_per_group_mba_hour` har PRISOMRÅDE – men dette er to separate nedbrytninger uten felles rad-nøkkel. Elhub publiserer ikke en egen kommune<->prisområde-koblingstabell (sjekket i datakatalogen, https://dok.elhub.no/data/Datasett.835354661.html, 05.09.2026).
2. **NVE Atlas / GIS3** (`https://gis3.nve.no/map/rest/services/Mapservices/Elspot/MapServer/0`, lag `ElSpot_omraade`): tjenesten svarte `{"error":{"code":500,"message":"Service Mapservices/Elspot/MapServer not started "}}` ved gjentatte forsøk 05.09.2026 – ikke i drift. Domenet `nve.geodataonline.no` som også dukket opp i søk finnes ikke (DNS-oppslag feiler).
3. **Geonorge/Statnett/RME**: ingen ferdig nedlastbart GIS-lag eller CSV med kommune<->prisområde ble funnet innenfor rimelig søkeinnsats.

Kilden som faktisk ble brukt er **VGs «Strømprisen»** (`https://www.vg.no/stromprisen/kommune/<kommune>/`), som for hver norsk kommune oppgir en entydig kobling «Kommune: <navn> (NOx)». Siden oppgir selv kildene **Statnett, Nasdaq, Nord Pool, NVE, Entsoe og Enova**. Dette er en redaksjonell/sekundær kilde, ikke en offisiell forskrift eller et primært register – men den bygger uttalt på de samme primærkildene (Statnett/NVE) som resten av norsk kraftprisjournalistikk, og er uavhengig konstruert av geo.py sin NVE-kraftverk-baserte kobling. VG-siden advarer selv eksplisitt: «Noen områder langs regiongrensene får strøm fra en annen region enn resten av kommunen. Sjekk gjerne med din strømleverandør hvilken region du tilhører.» – dvs. VG bekrefter at prisområde-grensen ikke alltid følger kommunegrensen eksakt (se eget avsnitt under).

Alle 27 overstyrte kommuner (pa_kilde="nve" i `tab_kommune_prisomrade.csv`) og de 2 manuelle unntakene (pa_kilde="unntak": Bømlo, Sveio) ble sjekket enkeltvis i nettleser 05.09.2026 – se URL-liste i `tab_prisomrade_verifisering.csv`. Siden er en client-rendered SvelteKit-app uten stabilt offentlig API; oppslagene ble derfor gjort manuelt (én per kommune), IKKE med et automatisert nedlastingsskript. De 99 kommunene med ren fylkesregel (pa_kilde="fylke") og de 229 der fylke og NVE er enige (pa_kilde="fylke=nve") er IKKE sjekket mot VG i denne runden (for stort omfang for manuell sjekk) – kontrollen er avgrenset til de kommunene der geo.py faktisk overstyrer eller gjør unntak, som er de eneste med reell risiko for feil.

## Resultat

- Sjekket: 29 kommuner (27 NVE-overstyringer + 2 manuelle unntak)
- Samsvar med VG: **28**
- Avvik: **0**
- Ikke verifisert (fant ingen VG-side): **1**
- Herav i panelet (`data/processed/panel.parquet`, 197 kommuner NO1/NO2/NO5): **12**

### Avvik

Ingen avvik funnet: alle 28 kommuner som ble bekreftet mot VG stemmer overens med `tab_kommune_prisomrade.csv`.

### Ikke verifisert

|   knr | kommune   | var_pa   | var_pa_kilde   |
|------:|:----------|:---------|:---------------|
|  3437 | Sel       | NO3      | nve            |

Sel (3437) ga 404 på VGs kommune-URL (både «sel» og «sel-kommune» ble forsøkt 05.09.2026); ikke lykkes å få tak i riktig URL-slug innenfor rimelig innsats. Indirekte støtte: Sel ligger midt i Nord-Gudbrandsdal, og alle de fem nabokommunene i samme NVE-overstyrte gruppe (Dovre, Lesja, Skjåk, Lom, Vågå) er bekreftet NO3 mot VG, og NVEs egen regionbeskrivelse (sitert i søk 05.09.2026) plasserer eksplisitt «Innlandet vest og nord for Vågåmo» i NO3 – som også omfatter Sel. `prisomrade=NO3` for Sel i `tab_kommune_prisomrade.csv` anses derfor som sannsynlig riktig, men er ikke direkte bekreftet mot en uavhengig kilde.

## De 12 overstyrte/unntaks-kommunene som faktisk inngår i panelet

Av de 29 sjekkede kommunene er det disse 12 som har prisområde NO1/NO2/NO5 og dermed faktisk påvirker analysen i `data/processed/panel.parquet` (resten – NO3/NO4 – er utenfor NRK/OEs analyseområde):

|   knr | kommune   | var_pa   | var_pa_kilde   | samsvar   |
|------:|:----------|:---------|:---------------|:----------|
|  3320 | Flå       | NO5      | nve            | samsvar   |
|  3322 | Nesbyen   | NO5      | nve            | samsvar   |
|  3324 | Gol       | NO5      | nve            | samsvar   |
|  3326 | Hemsedal  | NO5      | nve            | samsvar   |
|  3328 | Ål        | NO5      | nve            | samsvar   |
|  3330 | Hol       | NO5      | nve            | samsvar   |
|  4611 | Etne      | NO2      | nve            | samsvar   |
|  4612 | Sveio     | NO2      | unntak         | samsvar   |
|  4613 | Bømlo     | NO2      | unntak         | samsvar   |
|  4614 | Stord     | NO2      | nve            | samsvar   |
|  4615 | Fitjar    | NO2      | nve            | samsvar   |
|  4616 | Tysnes    | NO2      | nve            | samsvar   |

## Kommuner delt mellom prisområder

VGs egen tekst på forsiden av Strømprisen (https://www.vg.no/stromprisen/, hentet 2026-09-05) sier eksplisitt: «Noen områder langs regiongrensene får strøm fra en annen region enn resten av kommunen. Sjekk gjerne med din strømleverandør hvilken region du tilhører.» Dette bekrefter at prisområde-grensen ikke alltid følger kommunegrensen eksakt – men VG oppgir ingen liste over hvilke kommuner dette gjelder, og det ble ikke funnet noen slik liste hos NVE/Statnett/RME innenfor søkeinnsatsen i denne runden. `src/geo.py` sin egen NVE-kraftverk-kobling har samme svakhet innebygd: når et kraftverk-datasett gir `n_omrader > 1` for en kommune (flere kraftverk i forskjellige prisområder), faller koblingen tilbake til fylkesregelen i stedet for å velge riktig område for forbrukssiden – se `nve_area_by_name()` i geo.py (`pa_nve == "flere"` behandles ikke som entydig). Ingen av de 197 kommunene i panelet er identifisert som delt i denne runden, men muligheten er ikke uttømmende utelukket.

## Hva som IKKE ble verifisert

- De 99 kommunene med ren fylkesregel og de 229 der fylke og NVE-kobling er enige (`pa_kilde` i {"fylke", "fylke=nve"}) – ikke sjekket mot en uavhengig kilde i denne runden.
- Sel (3437), se over.
- Om noen av de 197 panelkommunene er reelt delt mellom to prisområder (VGs grenseadvarsel over) – ingen autoritativ liste funnet.
- VGs egen kobling er ikke en offisiell/forskriftsmessig kilde; den er inkludert fordi den er den eneste kommune-for-kommune-kilden som faktisk ble funnet, og fordi den er uavhengig av NVE-kraftverk-metoden i geo.py. Den bør behandles som en sterk, men ikke endelig, bekreftelse.
