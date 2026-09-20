# Vurdering av Codex' egne beregninger (norgespris_analyse_komplett.zip)

Dato: 20.09.2026. Filene ligger i `verifisering/codex_ekstern/`. Alle tall er til godkjenning.

## Konklusjon

Codex kommer til samme hovedresultat som vårt: bestillerne økte forbruket med om lag 3 prosent vinteren 2025/26, med placebo nær null. Codex' tall er regnet på det samme åpne Elhub-uttrekket som vårt, og jeg har reprodusert de sentrale tallene fra våre egne månedsdata. Det nye i Codex' arbeid er en timebasert test av mekanismen: forbruksgapet mellom bestillere og ikke-bestillere er størst i timene der Norgespris gir størst prisfordel, og det mønsteret finnes ikke i placebovinteren. Den testen bør vi ta inn som robusthet, etter egen kjøring på fulle data. To av Codex' spesifikasjoner bør ikke brukes som hovedtall: den trendjusterte (3,8 prosent) hviler på en lineær framskriving av ett års drift, og den «foretrukne» (2,8 prosent) trekker et placeboavvik fra som like gjerne kan være støy. Zip-filens rådatafil er avkortet og reproduserer ikke resultatene.

## Hva Codex har gjort

Utfall er logaritmen til kWh per målepunkt, gapet er tidlig bestilt minus ikke bestilt i samme prisområde, forbruksklasse og dag (eller time). Sent bestilte er utelatt. Ni strata (NO1, NO2, NO5 × Lav, Medium, Høy), vektet med antall tidlig bestilte målere.

| Spesifikasjon | Effekt | Intervall | Kommentar |
|---|---:|---:|---|
| Sesongmatchet DiD: gap minus gap samme dato ett år før | 3,28 | 2,57–4,13 | Ett førår (2024/25) |
| Placebo: samme grep ett år tidligere | −0,49 | −0,92 til −0,05 | |
| «Trendjustert DDD»: DiD minus placebo | 3,79 | 2,96–4,74 | Antar at driften i 2024/25 fortsetter |
| Fleksibel: gap predikert fra førdata (stratum × måned, ukedag, kubisk i ikke-bestillernes last) | 3,01 | 2,35–3,94 | Nærmest vår D7 |
| Samme, placeboår 2024/25 | 0,22 | −0,13 til 0,58 | |
| Codex' foretrukne: fleksibel minus placebo | 2,79 | 2,00–3,79 | |
| Timemodell: temperatur- og kalenderjustert nivå, minus placebo | 2,81 | 2,35–3,26 | |

Intervallene er bootstrap over ni strata og kalenderuker. Volum: 6 200 GWh forbruk hos tidlig bestilte oktober–april; merforbruk 168 GWh (122–226) med den foretrukne koeffisienten, 341 kWh per målepunkt. Ikke oppskalert til alle husholdninger.

Timetesten: for hver time og hvert stratum predikeres gapet fra en førperiodemodell med time-i-uken, kalendermåned, kubisk oppvarmingsgrad (Open-Meteo, tre punkter per område) og kubisk i ikke-bestillernes last. Prediksjonsavviket i vinteren 2025/26 regresseres på timens prisfordel: effektiv marginalpris med strømstøtte (spot under terskel, terskel + 10 prosent av overskytende over) minus 40 øre. Helning 5,1 log-prosentpoeng per krone/kWh i behandlingsvinteren, −1,3 i placebovinteren, differanse 6,4 (5,3–7,8). Uten kontroll for ikke-bestillernes last: 7,1.

## Kontroll mot våre data

Regnet fra `data/processed/did_month.parquet` (måned, tidlig mot ikke bestilt, årsdifferanse i gap, vektet med n_mp tidlig):

| Størrelse | Vår gjenregning | Codex |
|---|---:|---:|
| Sesongmatchet DiD, log | 0,0327 | 0,0323 |
| Placebo, log | −0,0053 | −0,0049 |
| Månedlig event-study okt. 2025–apr. 2026, prosent | 1,65 / 2,09 / 2,88 / 4,30 / 4,75 / 3,76 / 3,85 | identisk |
| Førperiode okt. 2024–sep. 2025, prosent | −1,25 til +0,37 | identisk |
| Tidlig bestilte målere | 493 315 | 493 315 |
| Forbruk tidlig bestilte okt.–apr., GWh | 6 200,09 | 6 200,09 |
| Stratumeffekter, prosent | 1,99–5,37 | 1,97–5,31 |

Små avvik i DiD og placebo skyldes at Codex aggregerer per dag (måler = median av timetellinger) og vekter dagene, mens vi bruker måneder. Datagrunnlaget er det samme. Mot vårt hoveddesign: D7 gir 3,0 prosent (2,5–3,7) med to førår og felles sesongprofil; Codex' fleksible modell gir 3,0 (2,3–3,9). Vår placebo −0,2, Codex' −0,5 og +0,2 avhengig av modell.

## Vurdering, punkt for punkt

1. **Ett førår mot to.** Codex' matchede DiD bruker bare 2024/25 som referanse. Vår D7 bruker snittet av 2023/24 og 2024/25. Med ett år bærer tilfeldige forskjeller i det ene året rett inn i estimatet. Placeboen på −0,5 viser at gapet falt litt fra 2023/24 til 2024/25; den matchede DiD-en på 3,3 inneholder dermed en ukjent del drift. To førår demper dette. Vår 3,0 og Codex' 3,3 er begge innenfor hverandres intervall.

2. **Trendjustert DDD på 3,8 bør ikke brukes.** Den tar DiD minus placebo, som er å anta at gapet ville fortsatt å falle med 0,5 prosentpoeng per år uten Norgespris. Førperioden i event-studien viser ingen jevn trend (−1,25 i oktober 2024 til +0,37 i september 2025, uten mønster). Codex bruker den heller ikke som hovedtall.

3. **Fleksibel modell: ikke-bestillernes last som regressor.** Gapet er log(tidlig) minus log(ikke bestilt), og modellen bruker log(ikke bestilt) som forklaringsvariabel. Variabelen står altså på begge sider. Tanken er å fange at bestillere kan reagere annerledes på kulde enn ikke-bestillere, og i førdata er det et gyldig grep. Risikoen er ekstrapolering: januar 2026 var kaldere enn noen måned i førperioden, og en kubisk funksjon utenfor treningsområdet kan gi vilkårlige prediksjoner. At resultatet (3,0) ligger nær den matchede DiD-en og vår D7, tyder på at dette ikke slår ut her. Det bør uansett rapporteres med og uten lastkontrollen, slik Codex gjør for timemodellen.

4. **Å trekke fra placeboavviket.** Codex' foretrukne tall (2,8) er fleksibel modell minus placeboavviket 0,22. Det behandler placeboen som et biasestimat som gjentar seg, ikke som en test. Intervallet for placeboen dekker null, så fratrekket kan like gjerne fjerne støy som skjevhet, og det legger placeboens varians på toppen av hovedestimatets. Jeg foretrekker å rapportere 3,0 med placeboen som separat kontroll, som vi gjør. Forskjellen mellom 2,8 og 3,0 er uten praktisk betydning, og begge ligger i vårt intervall.

5. **Inferens.** Bootstrap over ni strata med tilbakelegging gir ikke godt kalibrerte intervaller med ni enheter, og Codex sier det selv. Vår wild cluster bootstrap med 27 klustre (2,5–3,7) og Codex' intervall (2,3–3,9) er like brede. Ingen av dem fanger usikkerheten i selve identifikasjonsantakelsen.

6. **Sent bestilte utelatt.** Rimelig valg når inntredelsesforløpet er ukjent. Vår D7 tar dem med via dose fra daglige tellinger og får samme størrelsesorden. De to valgene supplerer hverandre.

7. **Volum.** 168 GWh og 341 kWh per målepunkt gjelder de 493 315 tidlig bestilte i de ni strataene, som er husholdninger med årsforbruk 1 000–50 000 kWh. Beregningen er riktig gitt koeffisienten. Vår aggregering (forbruksandel 0,77 × effekt = 2–3 prosent for alle husholdninger) svarer på et annet spørsmål og er ikke i konflikt.

8. **Timetesten er det nye bidraget.** Den tester mekanismen direkte: er merforbruket størst når prisfordelen er størst? Ja, og placebovinteren viser ingen slik helning. Det er vanskelig å forklare med seleksjon alene, siden seleksjonen skulle gi et nivåskift, ikke en time-for-time samvariasjon med prisfordelen. Tre forbehold:
   - Prisfordelen i 2025/26 lå i 87 prosent av time-strataene mellom 25 og 50 øre (39 651 av 45 792). Helningen identifiseres av de om lag 6 100 observasjonene i ytterkantene. Placebovinteren hadde langt lavere priser (snitt 13 øre mot 35), så de to helningene er estimert på ulike prisintervaller.
   - Prisfordelen er en funksjon av spotprisen, som samvarierer med kulde og time på døgnet. Modellen kontrollerer for temperatur, time i uken og ikke-bestillernes last, men en restsammenheng kan ikke utelukkes.
   - Tersklene 73 øre (2024), 75 øre (2025) og 77 øre (2026) eks. mva og 90 prosent dekning over terskel oppgis med lenker til Regjeringen og NVE. 2024 og 2025 stemmer med det jeg kjenner; 2026-terskelen er ikke kontrollert av meg: [verifiseres mot NVE før bruk]. Strømstøtten gjelder også bare forbruk opp til 5 000 kWh per måned, som ikke betyr noe for husholdningsgruppene her.

9. **Reproduserbarhet fra zip-filen.** `norgespris_cohorts.csv` i zip-filen dekker 01.10.2023 til 01.04.2024 (119 108 rader), mens Codex oppgir 407 376 rader til 30.04.2026. Skriptene kan derfor ikke kjøres på zip-innholdet. Datasettet er det samme som vi har fullstendig i `data/raw/elhub/`, så vi kan kjøre begge Codex-skriptene selv.

10. **Språk.** Codex skriver «sterk kausal støtte» og «styrker en kausal tolkning». For vår bruk: resultatene er forenlige med en kausal effekt og uforenlige med de enkleste seleksjonsforklaringene. Filene inneholder lang tankestrek ett sted.

## Anbefaling

- Behold D7 på 3,0 prosent (2,5–3,7) som hovedtall. Codex' 2,8–3,3 er uavhengig bekreftelse på samme data.
- Kjør Codex' timetest selv på fulle data (`analyze_norgespris_hourly.py` mot `data/raw/elhub/`), med terskel for 2026 kontrollert mot NVE, og rapporter helningen med og uten lastkontroll. Legg den inn i metodenotatet som robusthetstest av mekanismen.
- Rapporter Codex' matchede DiD med ett førår som følsomhet for valg av førperiode.
- Bruk ikke den trendjusterte varianten.
