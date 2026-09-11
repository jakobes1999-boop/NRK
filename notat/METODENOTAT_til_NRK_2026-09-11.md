# Etterprøving av «Prisen for billig strøm»: data, modell og resultater

*Metodenotat til forfatteren av NRK-artikkelen 27. august 2026. Jakob Eiksund Sæthre, samfunnsøkonom, skrevet som privatperson. Utkast 11. september 2026. Alle tall er foreløpige og merket til godkjenning i `output/TIL_GODKJENNING.md`; de er ikke NRKs tall. Kode og tabeller kan gjøres tilgjengelig i sin helhet.*

## 1 Formål

Artikkelen oppgir en regresjon med faste effekter per kommune der koeffisienten for «Innføring av Norgespris» er 0,0822, tolket som at ordningen har økt husholdningenes strømforbruk i NO1, NO2 og NO5 med over 8 prosent. Jeg har forsøkt å gjenskape en modell av samme type på åpne data, testet den med en placebo, og deretter estimert effekten på nytt med et design som har en kontrollgruppe. Notatet beskriver data, spesifikasjoner og resultater slik at de kan etterprøves, og avslutter med spørsmål som bare NRK kan svare på.

Hovedresultatet er at en modell av NRKs type gir om lag 10 prosent på mine data, men også om lag 5 prosent når innføringen legges til et år uten Norgespris. Med kontrollgruppe fra Elhubs bestillingsdata er effekten om lag 3 prosent for dem som bestilte, med usikkerhetsintervall 2,5 til 3,7 prosent, og mellom −1 og +1 prosent i placebo. Grovt omregnet til alle husholdninger i Sør-Norge er effekten 2 til 3 prosent.

## 2 Data

Alle kilder er åpne. Tabell 1 viser hva som er brukt til hva.

**Tabell 1: Datakilder**

| Kilde | Datasett | Periode | Brukt til |
|---|---|---|---|
| Elhub, data.elhub.no (CC BY 4.0) | `consumption_per_group_municipality_hour`: kWh og antall målepunkter per time, kommune og forbruksgruppe | feb. 2022–apr. 2026 | Kommunepanelet (NRK-lik modell). Gruppen «Privat» omfatter husholdning og hytte samlet |
| Elhub | `consumption_per_norgespris_order_status_eac_group_mba_hour_20231001_20260430`: kWh og målepunkter per time, prisområde (NO1, NO2, NO5), forbruksgruppe og bestillingsstatus | okt. 2023–apr. 2026 | Hoveddesignet med kontrollgruppe |
| Elhub | `norgespris_count_per_mba_consumption_group` og `..._per_municipality_...`: målere med Norgespris per dag | fra 1. okt. 2025 | Oppslutning per kommune; inntredelsesforløp for sent bestilte |
| Elhub | `consumption_per_group_mba_hour`: kWh per time, prisområde og forbruksgruppe | jan. 2021–sep. 2026 | Forbruksøkning jan.–jun. 2026 mot 2025 |
| Meteorologisk institutt, Frost | Døgnmiddeltemperatur per stasjon i NO1/NO2/NO5-fylkene | hele perioden | Energigradtall: sum over måneden av (17 °C − døgnmiddel) for dager under 17 °C, per kommune fra nærmeste stasjon |
| hvakosterstrommen.no | Spotpris per time per prisområde | fra des. 2021 | Månedlig gjennomsnittlig spotpris i øre/kWh; effektiv pris med strømstøtte |
| SSB tabell 06944 | Medianinntekt etter skatt for husholdninger, per kommune | t.o.m. 2024, framskrevet 2025–26 | Kontrollvariabel |
| SSB tabell 06513 | Boliger etter bruksareal, per kommune | årlig | Gjennomsnittlig bruksareal, kontrollvariabel |
| SSB tabell 14091 | Elektrisitetsbalanse, månedlig | | Nettoeksport jan.–jul. 2026 |
| NVE, vannkraftdatabasen | Energiekvivalent per kraftverk | | Vannregnestykket («1 kWh = 1 429 liter») |
| Elhub, datakatalog (wiki) | Definisjon av forbruksgrupper og bestillingsstatus | | Se avsnitt 4 |

Kommuner er koblet til prisområde med fylkesregel og NVE-kraftverkenes område, med 27 overstyringer; 28 av 29 kontrollerte kommuner er bekreftet mot VGs strømprisoversikt. Kommuneinndelingen er 2024, omkodet med SSBs Klass 131. Norgespris-tellinger under 100 målere er anonymisert til null i Elhubs filer.

Elhubs kommunefil starter 1. februar 2022 og slutter 30. april 2026. Artikkelen oppgir perioden 2021 til juni 2026. Jeg har derfor om lag 17 måneder mindre enn NRK, og kan ikke skille husholdning fra hytte på kommunenivå.

## 3 Modell av NRKs type og placebo

### 3.1 Spesifikasjon

Panelet har 197 kommuner og 51 måneder, 10 047 observasjoner. Modell M1:

```
log(kWh_it) = a_i + b1·gradtall_it + b2·spot_it + b3·inntekt_it + b4·bruksareal_it + b5·Norgespris_t + e_it
```

der a_i er faste kommuneeffekter, inntekt er i 1 000 kroner, spot i øre/kWh, og Norgespris_t er 1 fra og med oktober 2025 for alle kommuner, 0 ellers. Estimert med linearmodels PanelOLS. Standardfeil er klustret på kommune, men for en variabel uten variasjon mellom kommuner er de ikke tolkbare; Driscoll-Kraay-standardfeil er rapportert ved siden av.

### 3.2 Resultater

**Tabell 2: NRK-lik modell (M1) og placebo (M5), til godkjenning**

| Variabel | NRK | M1, log kWh | M1b, log kWh per måler | M5 placebo (innføring okt. 2024, data t.o.m. sep. 2025) |
|---|---|---|---|---|
| Energigradtall | 0,0019 | 0,0019 | 0,0019 | |
| Spotpris (øre/kWh) | −0,0005 | −0,0004 | −0,0004 | |
| Medianinntekt | 0,0024 | 0,0009 per 1 000 kr | 0,0005 | |
| Norgespris | 0,0822 | 0,0950 | 0,0840 | 0,0509 |
| Tilsvarende prosent | 8,6 | 10,0 | 8,8 | 5,2 |
| R² (within) | 0,9376 | 0,941 | 0,941 | 0,950 |

Placeboen M5 er identisk med M1 bortsett fra at Norgespris-variabelen er satt til 1 fra oktober 2024, og at data etter september 2025 er tatt ut. Modellen finner da en «effekt» på 5,2 prosent (4,5 prosent per måler) i en periode uten Norgespris. Det viser at en felles 0/1-variabel uten tidsfaste effekter fanger opp alt som skiller de siste månedene fra gjennomsnittet av de foregående, etter justering for gradtall og spot, og ikke bare ordningen.

Å legge til kalendermånedseffekter (M2) reduserer koeffisienten til 0,072, og år × måned-effekter gjør en felles 0/1-variabel kollineær med tidseffektene. Å bytte spotprisen med den effektive marginalprisen husholdningene faktisk møtte under strømstøtten flytter M1 fra 0,0950 til 0,0940.

### 3.3 Hva jeg vet om NRKs spesifikasjon

Artikkelen oppgir ikke om venstresiden er logaritme, om forbruket er per måler, hvordan Norgespris er kodet, om det er tidsfaste effekter, vekting, eller enheten på inntekt. For å avgrense har jeg kjørt 6 384 varianter av modellen over disse valgene og sammenlignet med de fire oppgitte koeffisientene og R². Resultatet er at gradtallskoeffisienten 0,0019 og en spotkoeffisient nær −0,0005 bare oppstår uten egen sesongkontroll; med kalendermånedseffekter faller gradtallet til om lag 0,0011 og spot til −0,0002. R² på 93,76 prosent samsvarer med within-R² i en modell med kommuneeffekter og uten tidseffekter. Inntektskoeffisienten kan jeg ikke gjenskape i noen enhet; nærmeste er 0,0031. Det kan skyldes at NRK har inntektsdata for 2021 og 2025 som jeg mangler, eller et annet inntektsbegrep.

Konklusjonen er at NRKs modell etter alt å dømme har faste kommuneeffekter, ingen tidseffekter og en felles 0/1-variabel for Norgespris. Er det riktig, gjelder placeboresultatet over også NRKs modell. Er det feil, ber jeg om å få vite det, se avsnitt 7.

## 4 Hoveddesign: forskjell-i-forskjell på bestillingsstatus

### 4.1 Data og grupper

Elhubs uttrekk deler husholdningene i NO1, NO2 og NO5 etter bestillingsstatus og estimert årsforbruk (EAC). Definisjonene er fra Elhubs datakatalog:

- **Ikke bestilt**: 402 414 målere. **Bestilt tidlig**: bestilt senest 1. oktober 2025, 493 315 målere. **Bestilt sent**: bestilt 2. oktober 2025 til 30. april 2026, 367 106 målere. Norgespris gjelder fra bestillingsdagen.
- **Forbruksgrupper**: Lav 1 000–8 000 kWh, Medium 8 000–16 000 kWh, Høy 16 000–50 000 kWh per år.

Gruppene er faste kohorter med samme målepunkter gjennom hele serien fra oktober 2023, også før den enkelte bestilte. Timeforbruket er summert til måned og delt på antall målepunkter, slik at utfallet er kWh per måler per måned. Det gir 27 grupper (3 områder × 3 statuser × 3 forbruksklasser) observert i 31 måneder, 837 rader.

### 4.2 Spesifikasjon

Hovedmodellen (D7):

```
log(y_gt) = a_g + d_(område, måned, klasse) + s_(bestilt × kalendermåned × klasse) + b·bestilt_g·post_t + e_gt
```

- **a_g**: fast effekt per gruppe. Fjerner nivåforskjellen mellom bestillere og ikke-bestillere.
- **d**: fast effekt per prisområde × kalendermåned × forbruksklasse. Fjerner alt som er felles for bestillere og ikke-bestillere innen samme område, måned og klasse: gradtall, spotpris, ferier, målervekst.
- **s**: bestillernes avvik fra ikke-bestillerne for hver av de tolv kalendermånedene, separat per forbruksklasse. Fanger bestillernes eget sesongmønster, i praksis estimert på de to vintrene før ordningen.
- **b**: koeffisienten på bestilt × (måned ≥ oktober 2025). Dette er effekten.

Vektet minste kvadraters metode med antall målepunkter som vekt. Standardfeil klustret på gruppe (27 klustre), med t-fordeling med 26 frihetsgrader. Fordi 27 klustre er få, er hovedintervallet regnet med wild cluster bootstrap (Rademacher-vekter, 999 trekninger, testinversjon).

Den identifiserende antagelsen er at bestillere og ikke-bestillere ville utviklet seg parallelt uten ordningen, gitt gruppe- og sesongeffektene. Kontrasten er fastpris mot strømstøtte, ikke fastpris mot markedspris, siden ikke-bestillerne beholdt strømstøtten.

### 4.3 Resultater

**Tabell 3: Forskjell-i-forskjell, til godkjenning**

| Modell | Koeffisient | Prosent | Klustret SE | Bootstrap-KI, prosent | N |
|---|---|---|---|---|---|
| D7, bestilt × post | 0,0299 | 3,0 | 0,0028 | 2,5–3,7 | 837 |
| D7, tidlig × post | 0,0309 | 3,1 | 0,0030 | | 837 |
| D7, sent × post | 0,0286 | 2,9 | 0,0032 | | 837 |
| D7 placebo (innføring okt. 2024, data før okt. 2025) | −0,0019 | −0,2 | 0,0012 | −0,4 til +0,1 | 648 |
| D2 (felles sesongprofil, område × måned-effekter) | 0,0433 | 4,4 | 0,0112 | | 837 |

Placeboen legger innføringen til oktober 2024 og bruker bare data før oktober 2025. Den estimerer dermed sesongprofilen på ett år og tester på det neste.

### 4.4 Robusthet

- **Event-study på førperioden**: månedsvise avvik mellom bestillere og ikke-bestillere for oktober 2024 til september 2025, mot året før, ligger mellom −1,1 og +0,4 prosent, med snitt −0,2. Effekten på 3,0 prosent er tre ganger største førperiodeavvik.
- **Utelate én gruppe om gangen**: koeffisienten varierer mellom 0,0277 og 0,0316 over de 27 variantene.
- **Uvektet**: 0,0297. **Kluster på område × klasse (9)**: SE 0,0039, eksakt bootstrap-p 0,004. **Kluster på område (3)**: SE 0,0042.
- **Sent bestilte** fikk fastpris gradvis gjennom vinteren. Andelen av kohorten med Norgespris, beregnet fra Elhubs daglige tellinger, er 0,22 i oktober, 0,47 i november, 0,64 i desember, 0,79 i januar, 0,89 i februar, 0,95 i mars og 0,99 i april. Effekten for sent bestilte vokser med denne andelen, men sent-kohorten har også en egen sesongprofil i førperioden som har samme form, og de to kan ikke skilles uten kohortens faktiske inntredelsesforløp. Jeg bruker derfor ikke tidlig/sent-kontrasten som bevis.
- **Uavhengig reproduksjon**: alle modeller er reprodusert fra rådata med egen kode utenfor prosjektet, med avvik under 10⁻⁴.

### 4.5 Fra bestillere til alle husholdninger

Bestillerne står for 77 prosent av husholdningsforbruket i NO1, NO2 og NO5 i perioden etter oktober 2025. Under forutsetning av at ikke-bestillerne er upåvirket, er aggregert effekt 0,77 × 3,0 ≈ 2,3 prosent; med spennet i spesifikasjoner 2,0–3,4 prosent. Forutsetningen kan ikke testes, og en effekt på ikke-bestillerne på ±1 prosentpoeng flytter aggregatet om lag like mye.

## 5 Forbruksøkningen og hva Norgespris forklarer

Husholdninger og hytter i NO1, NO2 og NO5 brukte 18 119 GWh i januar–juni 2026 mot 15 796 GWh i januar–juni 2025, en økning på 14,7 prosent. Husholdninger alene økte 14,3 prosent. Med en Norgespris-effekt på 2–3 prosent forklarer ordningen om lag en femdel av økningen, forutsatt at vintereffekten holder for mai og juni, som ikke dekkes av bestillingsdataene. En grov dekomponering med gradtall tilskriver 8–14 av de 15 prosentpoengene vær: 2025 var mildt, og januar 2026 var den kaldeste måneden i panelet.

## 6 Forbehold

1. **Seleksjon.** Bestillerne valgte selv. Elhubs egen statistikk viser at oppslutningen er 77 prosent i høyforbruksgruppen, 62 i middels og 42 i lav, og at bestillere bruker mer per døgn enn ikke-bestillere også innenfor samme forbruksgruppe. Denne nivåforskjellen fjernes av gruppeeffektene. Det designet ikke fjerner, er en endring som traff bare bestillerne vinteren 2025/26 og ikke skyldes fastprisen. En slik endring på 3 prosentpoeng ville fjerne hele effekten. Placebo og event-study viser at slike avvik ikke har forekommet i førperioden, men kan ikke utelukke et engangsavvik.
2. **Kontrasten er mot strømstøtte.** Mot en verden uten støtte ville effekten trolig vært større. En mekanisk skalering med prisgapet gir om lag 4,4 prosent, men det er ikke identifisert.
3. **Periode og forbruksgruppe.** Kommunepanelet mangler 2021 og mai–juni 2026, og skiller ikke husholdning fra hytte. Bestillingsdataene slutter i april 2026.
4. **Sesongprofilen** er i praksis estimert på to førvintere. Placeboen bærer derfor mer av bevisbyrden enn standardfeilen.
5. **Prisområde per kommune** har ingen offisiell kilde; 28 av 29 kontrollerte er bekreftet mot VG.

## 7 Spørsmål til NRK

Følgende ville avgjøre om avsnitt 3 treffer NRKs modell, og gjøre det mulig å reprodusere den eksakt:

1. Er venstresiden logaritmen av kWh, eller kWh i nivå? Totalt per kommune, eller per målepunkt?
2. Er «Innføring av Norgespris» en 0/1-variabel fra oktober 2025 for alle kommuner, eller en andel bestillere per kommune?
3. Er det faste effekter for tid (kalendermåned, år, år × måned) i tillegg til kommune?
4. Hvilken R² er oppgitt (within, overall, justert)?
5. Hvordan er standardfeilene regnet, og hva er de klustret på?
6. Hvilken Elhub-fil og hvilke forbruksgrupper er brukt, og hvordan er 2021 dekket når den åpne kommunefilen starter i februar 2022?
7. Hvilken inntektsvariabel (begrep, enhet, årgang for 2025 og 2026)?
8. Er boligstørrelse en regressor eller bare datakilde?
9. Hvilken kilde er brukt for kommune til prisområde?

## 8 Referanser til Elhubs egne analyser

- Elhub, «Statistikk for Norgespris», elhub.no/data-og-innsikt/statistikk-for-norgespris. Løpende oppdatert dashbord med antall målere, forbruksandel og oppslutning per forbruksgruppe og prisområde. Viser at 60 prosent av husholdningsmålerne i Sør-Norge hadde Norgespris medio januar 2026, og at disse sto for over 70 prosent av husholdningenes forbruk.
- Elhub, «Hvor mye av strømforbruket er knyttet til Norgespris?», publisert 23. januar 2026, elhub.no/artikler/hvor-mye-av-stromforbruket-er-knyttet-til-norgespris, med analyse-PDF på cdn.sanity.io/files/c24ip8ds/production/6073cd06240e5a4a44a07108a48f956b48a37c6e.pdf (lagret i `kilder/elhub_analyse_forbruk_norgespris_2026-01.pdf`). Perioden 1. oktober 2025 til 18. januar 2026. Oppslutning 77/62/42 prosent i høy/middels/lav forbruksgruppe; gjennomsnittlig døgnforbruk 93,0 mot 87,2 kWh (høy), 44,8 mot 39,0 (middels) og 18,1 mot 14,1 (lav) for målere med og uten Norgespris, altså 4,0–5,8 kWh høyere hos bestillere innen samme gruppe. Elhub presiserer at tallene ikke er temperaturkorrigert, og analysen sammenligner nivåer, ikke endring. Den sier derfor noe om seleksjon inn i ordningen, ikke om effekten av den.
- Elhub, datakatalog for uttrekket etter bestillingsstatus, med definisjon av tidlig/sent og forbruksgrupper (Atlassian-wiki, side 2816081922).

## 9 Reproduserbarhet

Alle skript kjøres med `py run_all.py` fra prosjektroten og laster ned data fra kildene i tabell 1 (Frost krever gratis klient-ID). Modellene i avsnitt 3 ligger i `src/s07_estimate_fe.py`, hoveddesignet i `src/s12_kritikk2_beregninger.py` (D7) og `src/s14_wild_bootstrap.py`, spesifikasjonssøket i `src/s18_nrk_spesifikasjonssok.py`. Uavhengig reproduksjon ligger i `verifisering/`. Jeg deler gjerne hele mappen.
