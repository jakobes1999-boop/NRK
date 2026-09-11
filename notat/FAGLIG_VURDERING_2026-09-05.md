# Faglig vurdering av NRKs «Prisen for billig strøm» og av vår etterprøving

Utkast 5. september 2026, revidert etter to kritikkrunder (`KRITIKK_2026-09-05.md`, `KRITIKK2_2026-09-05.md`). Tallene er hentet fra `output/TIL_GODKJENNING.md` og `output/tab_kritikk2.md` og er ikke godkjent for bruk i notatet. Tabeller bruker punktum som desimaltegn.

## 1. Vurdering i kortform

NRK skriver at innføringen av Norgespris «sammenfaller med et hopp på over åtte prosent i strømforbruket», at forbruket økte mest der flest valgte ordningen, og at «flere årsaker kan ligge bak». Artikkelens komposisjon, med overskrifter om «prisen for billig strøm» og en omregning av hele forbruksøkningen til dusjår, inviterer likevel til å lese tallet som ordningens virkning. Det er den lesningen vi vurderer.

Regresjonen NRK bygger på har kommunefaste effekter og en variabel for perioden etter 1. oktober 2025, uten kontroll for felles tidsutvikling. Designet skiller ikke ordningen fra annet som skjedde etter oktober 2025. En placebotest på samme modellform gir et utslag på 4–5 prosent for en innføring som ikke fant sted. Dersom standardfeilene er klustret på kommune, som er det vanlige valget i et slikt oppsett, er de rapporterte signifikansnivåene ikke tolkbare. NRK oppgir ikke hvilke standardfeil som er brukt.

Et design som sammenligner husholdninger som bestilte Norgespris med husholdninger som ikke gjorde det, innenfor samme prisområde, måned og årsforbruksgruppe, gir en effekt på 2,4–4,4 prosent for bestillerne, med 3,0 prosent i den mest restriktive spesifikasjonen. Placeboene ligger mellom −1,3 og +1,3 prosent: den mest restriktive spesifikasjonen (D7) gir −0,2, mens den sesongkontrollerte placeboen i s13 gir −0,7 for tidlig bestilte (p 0,007). Omregnet til alle husholdninger i NO1, NO2 og NO5, veid med bestillernes forbruksandel, er effekten 2,0–3,4 prosent. Vår vurdering er at Norgespris har økt forbruket, og at effekten er mellom en firedel og fire tideler av det NRKs tall antyder. Effekten er målt relativt til strømstøtte, ikke til full markedspris.

Vannregnestykket i artikkelen er riktig. Sammenhengen mellom inntekt og oppslutning er statistisk sikker, men liten, drevet av NO1, og halveres når boligstørrelse tas med. Sammenligningen av dusjpris med og uten Norgespris er aritmetisk riktig, men blander pris med og uten merverdiavgift.

## 2. Hva NRK har gjort, og hva vi ikke vet

NRK oppgir metode og fire koeffisienter, men ikke spesifikasjonen. Alt i denne tabellens høyre kolonne er hypoteser.

| Element | NRKs opplysning | Vår hypotese |
|---|---|---|
| Avhengig variabel | «husholdningenes månedlige strømforbruk» per kommune | Logaritme av kWh, gitt koeffisientstørrelsene; trolig Elhub-gruppen «Privat» (husholdning + hytte); ukjent om totalt eller per måler |
| Norgespris-variabel | «innføring av Norgespris», koeffisient 0,0822 | Dummy fra oktober 2025 er mest sannsynlig, fordi NRKs R² på 93,76 prosent ligger nær within-R² i vår dummy-modell (0,94) og langt fra andel-modellene (0,61–0,63). Koeffisientstørrelsen skiller ikke: vår andel-modell gir 0,083–0,086 |
| Øvrige forklaringsvariabler | gradtall, månedlig spotpris, medianinntekt; boligstørrelse oppgis som datakilde | Koeffisient er publisert for fire variabler; om boligstørrelse inngår i regresjonen er ukjent |
| Faste effekter | kommune | Ingen tidsfaste effekter (en post-dummy ville vært kollineær) |
| Standardfeil | ikke oppgitt | Ukjent |
| Periode | 2021 til juni 2026 | Elhubs åpne kommunefil starter februar 2022; NRK har trolig annen tilgang |
| Utvalg | NO1, NO2, NO5 | Kommune→prisområde-kobling ikke oppgitt |

Den enkleste utbedringen av hele denne vurderingen er å be NRK om spesifikasjonen (avsnitt 8, punkt 1).

## 3. Datagrunnlaget i etterprøvingen

| Kilde | Innhold | Dekning | Merknad |
|---|---|---|---|
| Elhub, forbruk per kommune og time | Privat, Forretning, Industri | feb 2022–apr 2026 | 357 kommuner etter fjerning av «ukjent»; aggregert til måned |
| Elhub, forbruk per prisområde og time | Husholdning, Hytter, tre næringsgrupper | jan 2021–sep 2026 | brukes til forbruket januar–juni per år (avsnitt 5.3) |
| Elhub, Norgespris-målere per kommune | antall med Norgespris og totalt, Husholdning og Hytter | daglig fra 1. okt 2025 | < 100 målere er satt til 0 |
| Elhub, forbruk etter bestillingsstatus | Ikke bestilt / Bestilt tidlig / Bestilt sent × Husholdning Lav/Medium/Høy × NO1/NO2/NO5 | okt 2023–apr 2026, time | engangsuttrekk; status per april 2026; tidlig = bestilt t.o.m. 01.10.2025, sent = 02.10.2025–30.04.2026 (Elhub-wiki, kilder/elhub_wiki_norgespris_status.txt) |
| MET Frost | døgnmiddeltemperatur → gradtall (17 °C) | 923 stasjoner i sørlige fylker | 162 av 197 kommuner har egen stasjon, 35 får fylkessnitt |
| hvakosterstrommen.no | spotpris per time NO1/NO2/NO5 | des 2021–jun 2026 | Nord Pool day-ahead |
| SSB 06944 | median inntekt etter skatt per kommune | 2020–2024 | omkodet til 2024-kommuner; 2024 framskrives til 2025–2026 |
| SSB 06513 | boliger etter bruksareal | 2021–2026 | snitt bruksareal ved klassemidtpunkt |
| NVE vannkraftdatabase | energiekvivalent, midlere produksjon, prisområde | 1 459 kraftverk med begge felt | energiekvivalent og kommune→prisområde |

Kommunepanelet er 197 kommuner × 51 måneder, balansert og uten manglende verdier. Kommune→prisområde bygger på fylkesregel, overstyrt av NVEs kraftverk der alle kraftverk i kommunen ligger i ett område, pluss to manuelle unntak. Av panelets 197 kommuner er 12 tilordnet på annet grunnlag enn fylkesregelen (10 fra NVE, 2 manuelt). Koblingen er ikke verifisert mot Statnett eller nettselskap.

## 4. Identifikasjonsproblemene i et NRK-likt design

### 4.1 Før/etter uten kontrollgruppe

Med kommunefaste effekter og en felles dummy fra oktober 2025 sammenlignes forbruket etter innføringen med forbruket før, justert for gradtall og spotpris. Alt annet som endret seg samtidig havner i dummyen. Testen er placebo: samme modell på data til og med september 2025, med en oppdiktet innføring i oktober 2024.

| Modell | Norgespris-koeffisient | Prosent |
|---|---|---|
| M1 NRK-lik, total kWh | 0.095 | 10.0 |
| M1b NRK-lik, per måler | 0.084 | 8.8 |
| M2 M1 + kalendermåned | 0.072 | 7.4 |
| M5 placebo okt 2024, total kWh | 0.051 | 5.2 |
| M5b placebo okt 2024, per måler | 0.044 | 4.4 |

Placeboen viser at modellformen kan gi et utslag på om lag halvparten av NRKs tall uten at det fantes noen reform. Placeboperioden er ikke ren: den inneholder vinteren 2024/25 og et annet strømstøtteregime enn 2022–2023, så utslaget kan ha flere kilder. Det er nettopp poenget: designet kan ikke skille dem fra hverandre, og heller ikke fra en reform.

M1 er ikke en replikasjon av NRK. Gradtallskoeffisienten treffer (0,00188 mot 0,0019), spotpris avviker 26 prosent, inntekt med faktor 2,7, Norgespris-koeffisienten er 0,095 mot 0,082, og perioden er kortere. Vi viser at et NRK-likt design gir samme type resultat, ikke at vi har gjenskapt NRKs modell.

### 4.2 Standardfeil

Norgespris-dummyen er identisk for alle 197 kommuner. Klustring på kommune behandler da 197 kopier av samme tidsserie som uavhengig informasjon. Driscoll-Kraay-standardfeil, som tillater felles sjokk over tid, er 2,1–2,5 ganger større for M1–M2 og 7–8 ganger større for placeboen.

| Modell | Koeffisient | Se kluster | Se Driscoll-Kraay | p Driscoll-Kraay |
|---|---|---|---|---|
| M1 | 0.095 | 0.0069 | 0.0175 | < 0.001 |
| M5 placebo | 0.051 | 0.0023 | 0.0168 | 0.002 |

Vi vet ikke hvilke standardfeil NRK har brukt. Dersom de er klustret på kommune, er stjernene ikke tolkbare. Placeboen er «signifikant» også med Driscoll-Kraay, så hovedproblemet er identifikasjon, ikke inferens.

### 4.3 Målervekst

Antall målere vokste fra februar 2022 til april 2026 med 4,6 prosent i tredelen av kommunene med lavest Privat-oppslutning og 6,9 prosent i tredelen med høyest (aggregert, output/tab_malervekst_oppslutning.csv). Målt på husholdningsandel er spennet 4,8–6,0 og ikke monotont. Med totalt kWh som avhengig variabel legges denne veksten til «effekten». Per måler faller M1 fra 0,095 til 0,084.

### 4.4 Heterogen temperaturfølsomhet

NRK skriver at forbruket økte mest der flest valgte Norgespris. Det stemmer i data, men forklaringen er ikke entydig. Husholdningsoppslutningen korrelerer 0,20 med gjennomsnittlig boligstørrelse (0,31 for Privat-andelen inkludert hytter). Kommuner med store boliger og elektrisk oppvarming reagerer sterkere på kulde. Januar 2026 er den kaldeste enkeltmåneden i panelet (gradtall 711 uveid, mot 567–685 i tidligere januarmåneder). Fyringssesongen 2025/26 er derimot ikke den kaldeste: summen av gradtall oktober–april er 3 324 mot 3 589 i 2023/24, 3 309 i 2022/23 og 3 081 i 2024/25. Kontrasten mot det milde 2024/25 er 8 prosent.

I to-veis FE-modellen med Privat-andel faller koeffisienten på oppslutning × post fra 0,21 (M4) til 0,16 (F6) når hver kommune får sin egen gradtallshelning. Med husholdningsandel er koeffisienten 0,086 og ikke signifikant (p = 0,21). Denne koeffisienten kan verken bære NRKs påstand om heterogene effekter eller vår egen; se avsnitt 5.1.

### 4.5 Kontrollvariabler som ikke er identifisert

Medianinntekt varierer bare fra år til år innen kommune og er framskrevet fra 2024 for 5 516 av 10 047 rader. Koeffisienten fanger nominell trend. Boligstørrelse er nesten tidsinvariant og absorberes av kommunefaste effekter. NRKs inntektskoeffisient (0,0024 mot vår 0,0009) tilsier løpende skattelistetall med sterkere trend, som trolig gir lavere Norgespris-koeffisient enn de ellers ville fått.

## 5. Alternative design og resultater

### 5.1 Kommunepanel med to-veis faste effekter

Tidsfaste effekter tar ut alt som er felles for alle kommuner i en måned. Effekten identifiseres av at kommuner med høy oppslutning endrer forbruket mer enn kommuner med lav etter oktober 2025. Oppslutning er husholdningsandel i april 2026 som fast kjennetegn per kommune. F2 inneholder kommune- og måned-FE og kommunespesifikk gradtallshelning, og utelater spotpris, inntekt og boligstørrelse (absorbert eller ikke identifisert).

| Spesifikasjon (Y = log kWh per måler) | β (0→100 % oppslutning) | Se | p | Ved oppslutning 0,65 |
|---|---|---|---|---|
| F1 to-veis FE + kontroller | 0.085 | 0.069 | 0.22 | 5.7 % |
| F2 to-veis FE + gradtall × kommune | 0.086 | 0.069 | 0.21 | 5.8 % |
| F4 placebo okt 2024 på F2 | −0.002 | 0.015 | 0.91 | −0.1 % |
| F6 F2 med Privat-andel inkl. hytter | 0.160 | 0.079 | 0.04 | 10.9 % (ved 0,66) |
| F7 F2 på ren fylkesregel, 212 kommuner | 0.083 | 0.027 | 0.002 | 5.5 % |

Punktestimatet i F2 er i samme størrelsesorden som DiD-designet, men 95-prosentintervallet går fra −3 til +16 prosent og rommer null. Event-studien (F5) viser ingen nivåendring: snittet av oppslutning × måned-koeffisientene er −0,148 før ordningen og −0,152 etter, og 22 av 44 pre-koeffisienter er signifikante med spenn −0,36 til +0,12. Kommuner med høy oppslutning har en annen månedsprofil enn kommuner med lav, også etter kontroll for egen gradtallshelning. Kommunepanelet kan verken bekrefte eller avkrefte DiD-estimatet.

F7 er ikke en robusthetstest av samme kontrast. Fylkesregelen legger til 15 kommuner som NVE plasserer i NO3 (Nord-Gudbrandsdal, Sunnfjord, Nordfjord) med husholdningsoppslutning 0,00–0,20. Standardavviket i oppslutning øker fra 0,09 til 0,17, og det er grunnen til at standardfeilen faller fra 0,069 til 0,027. Disse kommunene ligger utenfor NRKs univers og er priset mot feil spotserie. F7 sier bare at punktestimatet ikke flyttes av geo-koblingen.

### 5.2 Diff-in-diff på bestillingsstatus

Elhubs uttrekk gir behandlings- og kontrollgruppe med to år før ordningen, innenfor prisområde og årsforbruksgruppe. Forbruk per måler forklares med gruppefaste effekter (område × status × årsforbruksgruppe), tidsfaste effekter og samspillet bestilt × etter oktober 2025, vektet med antall målere, klustret på gruppe.

Seleksjon før ordningen: bestillerne brukte 40–62 prosent mer per måler enn ikke-bestillerne. Innenfor årsforbruksgruppe er forskjellen 1–16 prosent. Størrelsesseleksjonen tas ut av gruppefaste effekter.

Sesongprofil: den ujusterte event-studien har pre-koeffisienter med snitt null, men med et sesongmønster: +1,6 til +3,2 prosent i desember–februar, −1 til −5 prosent i juni–august. Bestillerne er mer temperaturfølsomme enn ikke-bestillerne. Post-perioden er utelukkende vinter og vår, så det ujusterte estimatet overvurderer effekten. Vi kontrollerer for bestillernes egen sesongprofil fra de to årene før ordningen.

| Spesifikasjon | β | Se | Prosent | Klustre |
|---|---|---|---|---|
| D1 gruppe-FE + område×måned-FE | 0.059 | 0.028 | 6.1 | 27 |
| D2 + bestilt × kalendermåned | 0.043 | 0.011 | 4.4 | 27 |
| D2e sesongprofil per årsforbruksgruppe | 0.043 | 0.011 | 4.4 | 27 |
| D3 D1 + bestilt × gradtall | 0.043 | 0.013 | 4.4 | 27 |
| D7 område×måned×årsforbruksgruppe-FE + sesongprofil per gruppe | 0.030 | 0.003 | 3.0 | 27 |
| D6 kun Husholdning Lav | 0.038 | 0.004 | 3.9 | 9 |
| D6 kun Husholdning Medium | 0.026 | 0.003 | 2.6 | 9 |
| D6 kun Husholdning Høy | 0.024 | 0.003 | 2.4 | 9 |
| Placebo okt 2024 på D2 | 0.008 | 0.007 | 0.8 | 27 |
| Placebo okt 2024 på D3 | 0.013 | 0.010 | 1.3 | 27 |
| Placebo okt 2024 på D7 | −0.002 | 0.001 | −0.2 | 27 |

D2 gir 4,4 prosent, mens alle tre undergruppene ligger på 2,4–3,9. Gapet skyldes ikke sesongprofilen (D2e er identisk med D2), men at område×måned-effektene i D2 deles på tvers av årsforbruksgrupper. Når tidseffektene får variere per gruppe (D7), er effekten 3,0 prosent, og forbruksveid snitt av undergruppene er 2,6 prosent. D7 er den mest restriktive spesifikasjonen og har placebo −0,2 prosent. Vi bruker D7 som sentralanslag og 2,4–4,4 som spenn.

Sesongjustert event-study for post-månedene (D2-oppsett): 2,7 prosent i oktober, 3,3 i november, 3,8 i desember, 5,3 i januar, 5,7 i februar, 5,3 i mars, 4,9 i april, med standardfeil 1,0–1,3 prosentpoeng. Tidlig og sent bestilte følger samme bane med om lag 0,5 prosentpoengs avstand i D2, og gir 3,1 mot 2,9 prosent samlet i D7. Månedsvis i D7-rammen har sent bestilte 0,6 prosent i oktober mot 1,3 for tidlig bestilte med felles sesongprofil, og 0,8 mot 1,1 med sesongprofil per kohort; avstanden lukkes gjennom vinteren (output/tab_dose_sent.md). Forskjellen mot D2 (2,3 prosent i oktober) kan skyldes de delte område×måned-effektene i D2 eller overkorreksjon i D7; den er ikke avgjort.

Tre forhold begrenser tolkningen:

- **Effekten er relativ til strømstøtte.** Ikke-bestillerne fikk strømstøtte i timer med høy pris. Estimatet måler forskjellen mellom fastpris på 40 øre og strømstøttens marginalpris, ikke «effekten av billig strøm» mot markedspris.
- **Tidlig og sent.** Elhubs dokumentasjon definerer «tidlig» som bestilt til og med 1. oktober 2025 og «sent» som bestilt 2. oktober 2025 til 30. april 2026. Norgespris gjelder fra bestillingsdagen. Sent-gruppen trådte derfor inn gradvis: fra de daglige tellingene hadde 23 prosent av dem fastpris i oktober (målerveid månedssnitt), 48 i november, 65 i desember, 79 i januar, 90 i februar, 95 i mars og 99 i april. Dette gir en dose-respons-test (s13, kritisert i KRITIKK3). Resultatet avhenger av sesongkontrollen. Med felles sesongprofil for bestillerne, som i D7, følger sent-gruppens månedseffekt dosen: forholdet sent/tidlig går fra 0,46 i oktober til 1,13 i april, og en tilpasning av sent-effekten på dose × tidlig-effekten gir stigning 1,06 [0,89, 1,23]. Men de to kohortene har ulik sesongprofil også i de to vintrene før ordningen: sent-gruppen ligger 0,9–1,1 prosentpoeng over tidlig-gruppen i februar–april relativt til oktober. Med sesongprofil per kohort er forholdet 0,74 i oktober og 0,98 i april, stigningen 0,84 [0,70, 0,99] med konstant 0,7 prosentpoeng [0,1, 1,2], og E1 deler sent-effekten i nivå 1,3 prosentpoeng (p 0,10) og 2,1 prosent per fullt behandlet måler (p 0,03). Nullverdien for nivået er ikke null: et konstruert utfall uten seleksjon gir 0,4–0,8 prosentpoeng fordi per-enhets-effekten varierer over måneder. Placebo med dosen lagt ett år tilbake gir 1,5 prosent med felles sesong og 0,3 med sesong per kohort, som bekrefter at felles profil er utilstrekkelig. Vurdering: sent-gruppens forløp er forenlig med en behandlingseffekt, men testen skiller ikke en behandlingseffekt fra en kohortspesifikk sesongprofil, og nivå og dose er nær kolineære med sju postmåneder (korrelasjon 0,93). Effekten per fullt behandlet måler ligger i 1,6–4,6 prosent avhengig av spesifikasjon og dosegrense (E1 per kohort 1,6–2,1; E1 felles 2,7; E4 3,1–3,8; E2 4,6). I månedene før ordningen ligger sent-gruppen 0,4–0,5 prosentpoeng over tidlig-gruppen i april–juni 2025 og 0,3–0,6 under i oktober 2025–februar 2026, etter kontroll for kohortens egen sesongprofil (s13b, tabell 3b). Avviket i førperioden er større enn den samlede forskjellen etter ordningen (0,24 prosentpoeng), så tidlig/sent-kontrasten er ikke informativ om behandlingseffekt. s13 rokker ikke ved sentralanslaget 3,0, som kommer fra tidlig_post og er 3,0–3,2 i alle varianter, men bekrefter det heller ikke. Forutsetningen om at bestillingstidspunktet er uavhengig av forbruksutviklingen er ikke testet. At månedseffektene er størst i januar og februar, også for tidlig bestilte, korrelerer 0,78 med hvor mye kaldere månedene var enn referanseårene; D7-rammen mangler gradtall, og mønsteret bør ikke leses som sesongvarierende behandlingseffekt. Forbehold: dosen er beregnet fra alle husholdningsmålere (55 prosent sene blant målerne utenfor kohorten), mens statusuttrekket er en fast kohort på 1,26 millioner målere med 43 prosent sene; kohortens oktoberdose ligger logisk mellom 0,00 og 0,37 (s13b), og nedre grense løfter nivåskiftet fra 1,3 til 2,0 prosentpoeng.
- **Få klustre.** 27 grupper i de samlede modellene og 9 i undergruppemodellene gir nedadskjeve standardfeil. Punktestimatene er robuste; p-verdiene skal ikke tas bokstavelig. Placeboene på 0,8–1,3 prosent er ikke signifikante, men punktestimatene er opptil en tredel av D2-estimatet. Presisjonen tillater ikke å utelukke en skjevhet av den størrelsen i D2. Placeboen i D7 er nær null.

### 5.3 Fra bestillereffekt til samlet forbruk

Omregning til samlet husholdningsforbruk krever bestillernes forbruksandel, ikke målerandel, siden bestillerne bruker mer per måler. I bestillingsstatus-uttrekket er forbruksandelen i post-perioden 0,75 i NO1, 0,84 i NO2 og 0,70 i NO5, samlet 0,77. Målerandelen er 0,68. Omregningen forutsetter at ikke-bestillerne er upåvirket av ordningen; det kan ikke testes i designet, og brudd kan trekke i begge retninger.

| Bestillereffekt | Kilde | Aggregert, forbruksveid (0,77) |
|---|---|---|
| 4.4 % | D2 | 3.4 % |
| 3.0 % | D7 | 2.3 % |
| 2.6 % | forbruksveid snitt av D6 | 2.0 % |

Forbruket i Husholdning + Hytter i NO1, NO2 og NO5 var 18 119 GWh i januar–juni 2026, mot 15 796 GWh i 2025 og 18 075 GWh i 2021 (Elhubs prisområdeserie). Økningen fra 2025 er 2 323 GWh, 14,7 prosent. Med 2,0–3,4 prosent effekt på 2026-nivået svarer det til 360–620 GWh, eller 16–27 prosent av økningen. NRKs «20 000 år dusj» svarer til 2 453 GWh, 5,6 prosent over vår beregnede økning, trolig fordi NRK dekker en litt lengre periode. Dusjårene beskriver hele forbruksøkningen. Artikkelen sier ikke direkte at økningen skyldes ordningen, men komposisjonen inviterer til den lesningen.

Hva den øvrige økningen skyldes har vi ikke dekomponert fullt ut. Januar–april 2026 var forbruket per måler 15,2 prosent høyere enn i 2025, og målerveid gradtall 66 enheter høyere per måned. Med gradtallshelning 0,0011–0,0019 forklarer det 8–14 prosentpoeng. Mot 2024, som hadde nesten like høye gradtall, var forbruket per måler 5,4 prosent høyere i 2026 mens været forklarer 1–1,5 prosentpoeng. Den uforklarte delen mot 2024 er om lag 4 prosentpoeng, som er forenlig med en aggregert effekt på 2–3 prosent pluss annen vekst. Tilsvarende uforklart vekst finnes også mellom tidligere år (2024 mot 2023: 7–9 prosentpoeng), så den kan ikke tilskrives ordningen alene.

## 6. NRKs øvrige tallpåstander

| Påstand | Vår kontroll | Vurdering |
|---|---|---|
| 1 429 liter vann per kWh (vektet snitt NO1+NO2) | 1 485 l/kWh med produksjonsveiing (NO1 3 309, NO2 1 229) | Holder; avvik 3,9 prosent, innenfor rimelig valg av vekt |
| 6 min dusj à 6 l/min ved 38 °C = 1,4 kWh | Uten varmetap kreves inntaksvann 4,6 °C; med 90 prosent virkningsgrad på berederen gir 8 °C nøyaktig 1,4 kWh (vann_dusj.py) | Holder |
| 2 000 liter kraftverksvann per dusj | 1,4 × 1 429 = 2 001 | Holder |
| Dusj koster 70 øre med Norgespris, 2,10 kr til markedspris | 1,4 × 0,50 = 0,70 (40 øre + mva); 1,4 × 1,50 = 2,10 (150 øre uten mva) | Aritmetisk riktig, men inkonsistent: 70 øre er med mva, 2,10 kr uten. Med lik behandling er markedsprisdusjen 2,63 kr. Ingen husholdning møtte 150 øre; alternativet var spot med strømstøtte |
| Høyere inntekt, flere med Norgespris | Korrelasjon 0,17 samlet; 0,45 i NO1, 0,03 i NO2, 0,02 i NO5. Målerveid regresjon: +0,4 prosentpoeng per 10 000 kr (p = 0,001), +0,2 med boligstørrelse som kontroll (p = 0,002) | Statistisk sikker, men liten, drevet av NO1; boligstørrelse forklarer mer |
| Forbruket har økt mest der inntekten er høy | Ikke testet direkte | Ikke etterprøvd |
| Nettoeksporten tilsvarer forbruksøkningen | SSB 14091, hele landet: nettoeksport jan–jul 2026 2 682 GWh mot forbruksøkning 2 323 GWh for husholdning og hytter i NO1+NO2+NO5 | Holder i størrelsesorden; ikke kontrollert mot Statnetts tall og ikke brutt på prisområde |

To Elhub-uttrekk er uenige om oppslutningen: Norgespris-filen gir 0,61/0,75/0,59 for NO1/NO2/NO5 i april 2026, bestillingsstatus-uttrekket 0,64/0,78/0,62. Forskjellen på 2,7 prosentpoeng kan skyldes ulik telling (aktive avtaler per dag mot status per april) og anonymiseringen i kommunefilen.

## 7. Svakheter i egen analyse

1. **Kommune→prisområde er bare delvis verifisert.** De 12 panelkommunene som er tilordnet på annet grunnlag enn fylkesregelen, og de 15 som er tatt ut fordi NVE plasserer dem i NO3, er bekreftet mot en sekundærkilde (VG «Strømprisen», s16, svar lagret i data/raw/vg). De øvrige 185 er ikke kontrollert mot noen uavhengig kilde, og delte kommuner er ikke utelukket. Punktestimatene flyttes ikke (F7), men tabellene og utvalget gjør det.
2. **Strømstøtten er modellert i en tilleggsberegning, ikke i hovedmodellene.** s15 bytter spot mot effektiv marginalpris i s07-spesifikasjonen og flytter M1-koeffisienten fra 0,0950 til 0,0940, M2 fra 0,0717 til 0,0713. Hovedmodellene i avsnitt 4 og 5 bruker fortsatt spot, og 5 000 kWh-taket er ikke modellert noe sted. I førperioden var marginalprisen kappet over en terskel. Feilspesifikasjonen er størst i 2022, som er referanseåret i kommunepanelet, og kan være en medforklaring på placeboutslaget i M5.
3. **Perioden.** Kommunepanelet starter februar 2022 og slutter april 2026. Prisområdeserien dekker 2021, men mangler spotpris før desember 2021.
4. **Populasjoner.** Kommunepanelet bruker Privat (husholdning + hytte), DiD bruker husholdninger. Estimatene skal ikke settes i samme tabell uten forbehold.
5. **Anonymisering.** 13 av 1 379 kommune-måneder i post-perioden har oppslutning satt til null.
6. **Inferens i DiD.** 27 klustre samlet, 9 per undergruppe. Wild cluster bootstrap er gjort (s14, avsnitt 10): hovedtermene holder, dose-termen for gruppen Lav gjør det ikke.
7. **M1 er ikke en replikasjon** (avsnitt 4.1).
8. **Dekomponeringen av forbruksøkningen** i avsnitt 5.3 bruker enkle gradtallshelninger fra egne modeller og spenner fra 8 til 14 prosentpoeng værforklart. Den er en illustrasjon, ikke et estimat.

## 8. Foreslåtte utbedringer, prioritert

| Nr | Utbedring | Hva den avgjør | Innsats |
|---|---|---|---|
| 1 | **Be NRK om spesifikasjonen.** Spørsmålsliste skrevet 05.09.2026 (notat/SPORSMAL_ELHUB_NRK.md); ikke sendt. | Om avsnitt 4 treffer NRKs faktiske modell. | Lav for oss; avhenger av NRK. |
| 2 | **Effektiv marginalpris.** Gjort 05.09.2026 (s15). Strømstøtten trakk vinterprisen ned 19–53 prosent. NRK-lik koeffisient faller fra 9,1 til 8,7 prosent (log-log), med kalendermåned fra 6,9 til 6,6. I s07-spesifikasjonen eksakt: M1 0,0950 → 0,0940. Prisgap-modellen gir implisert egenpriselastisitet −0,10 (p 0,20), identifisert av oppslutning, ikke pris; D7 tilsvarer −0,05. | Strømstøtten forklarer ikke NRKs tall. | Gjort; parameter april–mai 2023 svakere belagt. |
| 3 | **Skjæringsdato tidlig/sent fra Elhub.** Funnet 05.09.2026 (Elhub-wiki), dose-respons i s13. Sent-gruppens effekt vokser i takt med inntreden, men mønsteret skilles ikke fra kohortenes ulike sesongprofil i reformfrie år. Gjenstår: kohortens eget inntredelsesforløp fra Elhub (daglige tellinger per status), leads-test. | Forenlig med behandlingseffekt; ikke avgjort. | Lav for det som er gjort; Elhub-forespørsel for resten. |
| 4 | **Wild cluster bootstrap.** Gjort 05.09.2026 (s14, WCR, B = 999). D7 p < 0,001 med KI [2,4, 3,7] prosent; placebo p 0,14; E1 sent_dose p 0,014. Ni-kluster-modellene: tidlig_post p 0,002–0,037; E6 Lav sent_dose overlever ikke (p 0,08–0,09). | Hovedtermene holder; per-gruppe-dosetall gjør det ikke. | Gjort. |
| 5 | **Verifiser prisområde.** Gjort 05.09.2026 (s16) mot VG «Strømprisen» som sekundærkilde; ingen offisiell liste finnes, NVEs karttjeneste var nede. 28 av 29 overstyrte kommuner bekreftet, Sel ikke slått opp, null avvik. Delte kommuner ikke utelukket. | Utvalg og spotserie står. | Gjort med sekundærkilde. |
| 6 | **Full dekomponering av forbruksøkningen 2025→2026 og 2024→2026** med gradtallshelninger fra D7-oppsettet og kontroll for målervekst. | Om «resten er vær» kan sies, og hvor stor den uforklarte delen er. | Lav–middels. |
| 7 | **Hytter som egen analyse.** Elhub skiller Husholdning og Hytter på prisområdenivå. | Om hyttebruk driver kommunepanelets variasjon, og om ordningen virker annerledes for hytter. | Middels. |
| 8 | **Time-oppløsning** i bestillingsstatus-uttrekket: er effekten konsentrert i timer med høy spotpris? | Mekanismen: prisrespons eller generell økning. | Middels. |
| 9 | **Deflatert inntekt eller drop inntekt** i NRK-lik modell. | Om NRKs inntektsvariabel bidrar til deres lavere Norgespris-tall. | Lav. |
| 10 | **Nettoeksport.** Gjort 05.09.2026 (s17, SSB 14091, hele landet). Jan–jun 2026 mot 2025: nettoeksport −10 168 GWh, produksjon −6 379 GWh, bruttoforbruk +3 789 GWh; husholdningene i Sør-Norge +2 323 GWh. | NRK sammenligner nivået på årets nettoeksport med forbruksøkningen, ikke fallet: jan–jul 2026 2 682 GWh mot 2 323 GWh, samme størrelsesorden. Fallet dekomponeres regnskapsmessig til 63 prosent produksjon og 37 prosent forbruk. | Gjort; ikke brutt på prisområde. |

Punkt 1–3 kan endre konklusjonen. Punkt 4–6 sikrer tallene som står. Resten er utvidelser.

## 9. Forslag til konklusjonsformulering i notatet

«Husholdninger som valgte Norgespris økte forbruket med 2–4 prosent sammenlignet med husholdninger som ikke gjorde det, med 3 prosent som sentralanslag. Effekten er målt relativt til strømstøtte, ikke til markedspris. Omregnet til alle husholdninger i NO1, NO2 og NO5 tilsvarer det 2–3 prosent, eller om lag en femdel av forbruksøkningen fra første halvår 2025 til første halvår 2026. NRK oppgir at innføringen sammenfaller med et hopp på over 8 prosent. Tallet kommer fra en modell uten kontroll for felles tidsutvikling, og samme modellform gir et utslag på 4–5 prosent for et tidspunkt der ordningen ikke fantes. Vannregnestykket i artikkelen er riktig. Omregningen av hele forbruksøkningen til 20 000 dusjår beskriver økningen, ikke ordningens virkning; en grov dekomponering tilsier at 8 til 14 av de 15 prosentene vekst i forbruk per måler januar–april kan tilskrives vær; dekomponeringen er en illustrasjon, ikke et estimat. NRKs påstand om at årets nettoeksport tilsvarer husholdningenes forbruksøkning i Sør-Norge holder i størrelsesorden.»

Formuleringen forutsetter at tallene i `TIL_GODKJENNING.md` godkjennes. Etter kritikkrunde 3 og 4 (avsnitt 10) står sentralanslaget 3 prosent på tidlig bestilte og på D7 samlet; tidlig/sent-kontrasten er ikke informativ, og om sent-gruppens forløp er behandling eller kohortforskjell kan ikke avgjøres uten Elhubs inntredelsesdata.

## 10. Utbedringer gjennomført 05.09.2026 og hva som gjenstår

Etter kritikkrunde 3 ble alle punkter som kunne løses med tilgjengelige data gjennomført (s13b, s14, s15, s16, s17). Resultatene endrer ikke sentralanslaget, men strammer inn hva som kan sies.

- **Usikkerhet med få klustre.** Wild cluster bootstrap endrer ikke konklusjonene for 27-kluster-modellene. Intervallene er fra 9 prosent smalere til 6 prosent videre enn t(G−1)-intervallene, og for E1 sent_dose faller p fra 0,031 til 0,015. D7-effekten 3,0 prosent har intervall 2,4–3,7. Placeboen er ikke signifikant i noen test (p 0,14). I modellene per forbruksgruppe med ni klustre faller signifikansen for bestiller-effekten fra under 0,001 til 0,001–0,038 (Rademacher og Webb), og dose-termen for gruppen Lav overlever ikke (p 0,08–0,09). Bootstrap-p er beregnet med K lik antall estimerte parametre, som gir 1 prosent lavere standardfeil enn statsmodels; en uavhengig kontroll fra kritikeren reproduserer D7-intervallet.
- **Dose-robusthet.** Med kohortens oktoberdose i hele det logiske spennet 0,00–0,37 er effekten per fullt behandlet måler 1,6–2,1 prosent med nivåskift og 3,1–3,8 uten. Tidlig bestilte er mer temperaturfølsomme enn sent bestilte (1,75 mot 1,0 prosent per hundre gradtall), men tidlig-effekten er 3,2–3,3 også med gradtall i modellen. Lead-testen er ikke identifisert: dose og neste måneds dose korrelerer 0,98 etter utpartialisering, og de to spesifikasjonene gir motsatt svar (E1 lead 0,16 prosent, p 0,85; E4 lead 2,7 prosent, p 0,08, med samtidig dose 0,7, p 0,66). I september 2025, før Norgespris gjaldt for noen, ligger tidlig-gruppen 0,5 prosent over ikke-bestillerne (p 0,06) og sent-gruppen 0,35 prosent (p 0,12). Verken forventningseffekt eller kohortforskjell i sesongprofil er utelukket. Gradtallet per område er målerveid over alle målere i kommunene, ikke over husholdningskohorten.
- **Effektiv marginalpris.** Husholdninger uten Norgespris betalte 19–53 prosent under spot i vintermånedene på grunn av strømstøtten. Å bytte spot med effektiv pris i den NRK-like modellen flytter Norgespris-koeffisienten fra 9,1 til 8,7 prosent. Feilmålt pris forklarer ikke NRKs tall.
- **Prisområde.** Alle overstyrte kommuner som kunne slås opp stemmer med en sekundærkilde. Kommuner som er delt mellom områder er ikke utelukket.
- **Nettoeksport.** NRK sammenligner nivået på årets nettoeksport med forbruksøkningen, ikke fallet. Januar–juli 2026 var nettoeksporten 2 682 GWh (SSB 14091, hele landet) mot en forbruksøkning på 2 323 GWh for husholdninger og hytter i NO1, NO2 og NO5, samme størrelsesorden. Fallet i nettoeksport januar–juni på 10 168 GWh følger av identiteten produksjon minus bruttoforbruk: produksjonsfallet på 6 379 GWh utgjør 63 prosent og forbruksøkningen på 3 789 GWh 37 prosent. Den årsaksmessige attribusjonen kan ikke leses ut av balansen. En første versjon av denne analysen sammenlignet fallet i stedet for nivået; det ble fanget i kritikkrunde 4.

**Gjenstår og krever eksterne svar** (notat/SPORSMAL_ELHUB_NRK.md): kohortens faktiske inntredelsesforløp og om tellingen 1. oktober er ved døgnstart eller døgnslutt (Elhub); NRKs spesifikasjon (NRK). Uten det første kan ikke behandlingseffekt og kohortforskjell skilles for sent-gruppen; uten det andre er avsnitt 4 en vurdering av et NRK-likt design, ikke av NRKs modell. 2021 mangler i kommunepanelet fordi Elhubs kommunefil starter i februar 2022. Punktene 6–9 i tabellen (full dekomponering, hytter, timeoppløsning, deflatert inntekt) er ikke gjort og påvirker ikke hovedkonklusjonen. 5 000 kWh-taket i strømstøtte og Norgespris er ikke modellert, og fordelingen over målere finnes ikke i uttrekket; taket er en kandidatforklaring på at effekten er størst i gruppen Lav og minst i Høy. Kritikkrunde 4 (KRITIKK4) fant og rettet en feillesning av NRKs eksportpåstand, en aritmetisk feil om produksjonsfallet, en feil påstand om bootstrapintervallenes bredde, og selektiv sitering av lead- og septembertestene.
