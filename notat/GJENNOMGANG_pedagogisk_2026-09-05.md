# Beregningene forklart, steg for steg

*Skrevet for at avsenderen skal kunne forklare hvert tall i debattinnlegget enkelt. Hvert steg viser hva som ble gjort, hvorfor, hva det ga, og hvordan det kan sies i én setning. Tall fra output/TIL_GODKJENNING.md; ikke godkjent ennå.*

## 0. Spørsmålet

NRK sier: Norgespris (fastpris 50 øre inkl. mva fra 1. oktober 2025) fikk husholdningene i Sør-Norge til å bruke over 8 prosent mer strøm. Vi spør: hva viser dataene faktisk, når man måler riktig?

Alt bygger på ett prinsipp. **For å måle effekten av noe, må man vite hva som ville skjedd uten.** Det kalles kontrafaktisk. Man kan ikke observere det, så man trenger en gruppe som ikke fikk tiltaket, men ellers opplevde det samme. Det er kontrollgruppen.

## 1. Datagrunnlaget

Alle kilder er åpne.

| Kilde | Hva | Brukt til |
|---|---|---|
| Elhub (data.elhub.no) | Timeforbruk per kommune og kundegruppe, feb 2022–apr 2026 | Kommunepanelet (NRK-likt design) |
| Elhub | Timeforbruk for husholdninger etter bestillingsstatus (ikke bestilt / bestilt tidlig / bestilt sent), okt 2023–apr 2026, NO1, NO2, NO5 | Hoveddesignet (kontrollgruppe) |
| Elhub | Antall Norgespris-målere per dag og kommune | Oppslutning, inntredelse |
| Meteorologisk institutt (Frost) | Døgntemperatur per stasjon | Gradtall = hvor kaldt |
| hvakosterstrommen.no | Spotpris per time per prisområde | Prisvariabel |
| SSB | Medianinntekt, boligstørrelse per kommune | Kontrollvariabler i NRK-likt design |
| NVE | Kraftverk med energiekvivalent | Vannregnestykket |

**Gradtall** er et mål på oppvarmingsbehov: for hver dag regnes hvor mange grader døgnmiddelet ligger under 17 °C, og det summeres over måneden. Kaldt = mange gradtall.

## 2. NRK-likt design: én sammenligning i tid

**Hva:** Et panel med 197 kommuner × 51 måneder. Forbruket (i logaritme, så koeffisienter kan leses som prosent) forklares med gradtall, spotpris, inntekt, boligstørrelse, en fast effekt per kommune, og en variabel som er 0 før oktober 2025 og 1 etter. Den siste er «Norgespris».

**Resultat:** koeffisient 0,095, altså om lag 10 prosent. NRK oppgir 0,0822. Gradtallskoeffisienten treffer NRKs eksakt (0,0019). Vi treffer altså samme type resultat med samme type modell, uten å kjenne NRKs eksakte oppsett.

**Problemet:** Variabelen «Norgespris» er lik for alle kommuner og skifter på samme dato. Den kan ikke skilles fra noe annet som også skiftet for alle etter oktober 2025. Modellen har kontroll for vær og pris, men bare med én felles helning, og ingenting for målervekst, elbiler, varmepumper eller at boligmassen vokser. Alt det tilskrives Norgespris.

**Beviset (placebo):** Vi lot som om Norgespris ble innført i oktober 2024, og kjørte samme modell på data som slutter i september 2025, altså før ordningen fantes. Resultat: 5,2 prosent «effekt» av en ordning som ikke eksisterte. Per måler 4,5. En modell som finner en effekt der det ikke er noen, kan ikke brukes til å tallfeste effekten der det er en.

**Én setning:** «NRKs modell sammenligner før og etter, uten noen som ikke fikk ordningen. Kjører man den på et år uten Norgespris, finner den likevel 5 prosent.»

## 2b. Hvor sikre er vi på at vi har samme modell som NRK?

Ikke sikre. NRKs metodeboks (kilder/nrk_prisen_for_billig_strom.md, linje 251–285) oppgir: regresjon med faste effekter per kommune («sammenligner hver kommune med seg selv over tid»), månedlig forbruk, variablene energigradtall, spotpris, «Innføring av Norgespris» og medianinntekt, periode 2021–juni 2026, NO1/NO2/NO5, R² 93,76 prosent. Boligstørrelse fra SSB nevnes som datakilde men står ikke i koeffisienttabellen.

Det som ikke oppgis: om venstresiden er logaritme (tolkningen «over 8 prosent» tyder på det), om forbruket er totalt eller per måler, hvordan Norgespris-variabelen er kodet (0/1 fra oktober 2025 for alle, eller oppslutningsandel per kommune), om det er tidsfaste effekter, om observasjonene er vektet, hvordan standardfeilene er regnet, og enheten på inntekt.

Det vi kan sammenligne (output/tab_fe_resultater.csv, M1):

| Variabel | NRK | Vår M1 | Merknad |
|---|---|---|---|
| Energigradtall | 0,0019 | 0,0019 | Sammenfaller på fjerde desimal |
| Spotpris | −0,0005 | −0,0004 | Samme fortegn og størrelsesorden |
| Medianinntekt | 0,0024 | 0,0009 per 1 000 kr | Enhet ukjent hos NRK; ikke sammenlignbar |
| Norgespris | 0,0822 | 0,0950 | Samme størrelsesorden |
| R² | 93,76 | 94,1 (within) | Nær |

Tre ting peker på 0/1-koding: R² på 94 prosent er hva én-veis FE med gradtall gir uten tidsfaste effekter (med år×måned-effekter ville en felles 0/1-variabel vært kollineær og ikke kunnet estimeres); koeffisienten leses av NRK direkte som «over 8 prosent» for alle husholdninger, som passer en dummy og ikke en andel; og gradtallskoeffisienten sammenfaller med vår, som viser at værkontrollen fungerer likt. Er variabelen i stedet oppslutningsandel per kommune, er kritikken om manglende kontrollgruppe svakere, men da skulle koeffisienten leses som effekt ved 100 prosent oppslutning, og «over 8 prosent» for alle ville vært feil tolkning.

Avvikene mellom 0,0822 og 0,0950 kan skyldes at NRK starter i 2021 (vi i februar 2022), går til juni 2026 (vi til april), måler per kommune uten å dele på målere, eller definerer variablene litt annerledes. Ingen av disse endrer poenget: modelltypen har ingen kontrollgruppe, og placeboen på vår versjon av den finner 5 prosent.

Derfor er innlegget formulert betinget («alt tyder på», «er det riktig»), og NRK bes oppgi spesifikasjonen.

**Spesifikasjonssøk 06.09.2026** (src/s18_nrk_spesifikasjonssok.py, notat/NRK_SPESIFIKASJONSSOK_2026-09-06.md, til godkjenning): 6 384 kjøringer over venstreside, Norgespris-koding, tids-FE, kontroller, enheter, vekting og utvalg. Gradtall 0,0019 og spot nær −0,0005 oppnås bare uten sesongkontroll (kalendermåned-FE halverer gradtallet til 0,0011). R² 93,76 samsvarer med within-R² uten tids-FE (våre 0,935–0,963), ikke overall (0,13) eller dummy-OLS (0,994). Spot er i øre/kWh. Norgespris 0,0822 treffes av flere varianter (0/1 fra september 2025 på log kWh gir 0,080–0,082). Inntekt 0,0024 treffes ikke (nærmest 0,0031 med per måler, 10 000 kr, vektet); enheten er ukjent og koeffisienten ustabil over perioder. Rådata fra Elhub starter februar 2022 og slutter april 2026, så NRKs 2021 og mai–juni 2026 kan ikke gjenskapes. Konklusjon: 0/1 uten tids-FE er fortsatt den mest sannsynlige tolkningen; placebo-argumentet står. Beviset i innlegget hviler ikke på at vi har gjettet riktig om NRK, men på at bestillingsdataene gir et annet svar enn enhver modell av NRKs type.

## 3. Hoveddesignet: sammenligning med en kontrollgruppe

**Hva:** Elhub deler husholdningene i tre: ikke bestilt, bestilt tidlig (til og med 1. oktober 2025), bestilt sent (2. oktober 2025–30. april 2026). Innenfor hvert prisområde og hver forbruksklasse (lavt, middels, høyt årsforbruk) sammenligner vi forbruk per måler for bestillere og ikke-bestillere, måned for måned, fra oktober 2023.

Dette kalles differanse-i-differanse. Logikken:

1. Bestillere og ikke-bestillere har ulikt nivå. Det er greit; vi ser bare på endring.
2. Begge gruppene møter samme vær og samme spotpris i samme område og måned. Det fanges av en fast effekt per område × måned × forbruksklasse.
3. Bestillerne kan ha en annen sesongprofil (bruker relativt mer om vinteren). Det fanges av en egen kalendermånedsprofil for bestillerne, estimert på de to vintrene før ordningen.
4. Det som står igjen etter oktober 2025 er effekten av å ha fastpris i stedet for strømstøtte.

**Resultat (D7):** 3,0 prosent høyere forbruk for bestillerne. Usikkerhetsintervall 2,5–3,7 prosent, regnet med wild cluster bootstrap fordi vi bare har 27 grupper (3 områder × 3 statuser × 3 klasser).

**Placebo:** Samme design med falsk innføring oktober 2024: −0,2 prosent, ikke signifikant. I en variant med separat sesongprofil for tidlig og sent bestilte gir placeboen −0,7 for tidlig bestilte. Spennet er −1 til +1. Ingen falsk effekt av samme størrelse som den ekte.

**Forbehold som må sies:** Bestillerne valgte selv. Designet forutsetter at gruppene ellers ville utviklet seg likt. Vi tester det med placebo og sesongkontroll, men kan ikke bevise det. Og effekten er målt mot strømstøtte (som kappet prisen over 75–77 øre i førperioden), ikke mot markedspris. Mot en verden uten støtte ville effekten vært større. 3 prosent er derfor i underkant.

**Én setning:** «Sammenligner man dem som bestilte med dem som ikke gjorde det, i samme område og samme måned, økte bestillerne forbruket med om lag 3 prosent.»

## 3b. Spesifikasjonen av hovedmodellen (D7)

Fra src/s12_kritikk2_beregninger.py, linje 49. Vektet MKM (vekt = antall målere), klustrede standardfeil på gruppe.

```
log_y ~ C(g) + C(pa_t_eac) + bestilt:C(mnd):C(eac) + bestilt_post
```

Én rad er én gruppe i én måned. Gruppe = prisområde × bestillingsstatus × forbruksklasse (3 × 3 × 3 = 27), oktober 2023 til april 2026, 837 rader. Placebo: data til og med september 2025, 648 rader.

| Ledd | Hva det er | Hva det fjerner |
|---|---|---|
| `log_y` | log(kWh per måler i gruppen) | Koeffisienter leses som prosent |
| `C(g)` | Fast effekt per gruppe (27) | Nivåforskjellen mellom gruppene («endring, ikke nivå») |
| `C(pa_t_eac)` | Fast effekt per område × kalendermåned × forbruksklasse | Alt som er felles for bestillere og ikke-bestillere i samme område, måned og klasse: vær, spotpris, ferier, målervekst |
| `bestilt:C(mnd):C(eac)` | Bestillernes avvik per kalendermåned (12), separat per klasse (3) | Bestillernes eget sesongmønster, identifisert av førperioden («deres egen sesongprofil») |
| `bestilt_post` | 1 for bestillere fra okt. 2025 | Effekten: 0,0299 = 3,0 prosent |

Placebo: samme formel, `bestilt_post` = 1 for bestillere fra okt. 2024, kun data før okt. 2025: −0,0019 (p 0,13). Tidlig/sent: `tidlig_post + sent_post` i stedet for `bestilt_post`: 3,1 og 2,9 prosent. Intervallet 2,5–3,7 prosent er fra wild cluster bootstrap (s14; grensene 0,0242–0,0366 er logpoeng), ikke fra den klustrede standardfeilen 0,0028, fordi 27 klustre er få.

Forbehold: sesongprofilen (36 parametre, 33 uavhengige) er i praksis estimert på to førvintere. Derfor bærer placeboen mer av bevisbyrden enn standardfeilen. Verifisering 06.09.2026: tolkningen av `bestilt_post` som snitt av sju månedsavvik er eksakt for uvektet modell (0,02965); målervektet gir 0,02988. Se notat/VERIFISERING_codex_2026-09-06.md.

## 3c. Hvordan sesongprofilen identifiseres, og hva tidlig/sent er

**Sesongprofilen.** Førperioden okt. 2023–sep. 2025 inneholder hver kalendermåned to ganger; etterperioden okt. 2025–apr. 2026 inneholder sju kalendermåneder én gang. For januar har modellen tre observasjoner av forskjellen bestillere minus ikke-bestillere (2024, 2025, 2026) og to størrelser: januar-profilen (lik alle år) og `bestilt_post` (felles for alle sju vintermåneder). Fordi `bestilt_post` ikke kan tilpasse seg januar spesielt, blir januar-profilen i praksis snittet av 2024 og 2025, og `bestilt_post` blir snittet over sju måneder av avviket fra eget førgjennomsnitt. Mai–september har ingen etterobservasjon, så profilen der er ren førperiode. Svakhet: to vintre er tynt for et normalmønster. Placeboen (innføring okt. 2024) estimerer profilen på ett år og tester på det neste: −0,2 prosent.

**Tidlig og sent (Elhub-definisjon).** Tidlig = bestilt senest 1. oktober 2025 (493 315 målere). Sent = bestilt 2. oktober 2025–30. april 2026 (367 106). Ikke bestilt: 402 414. Norgespris gjelder fra bestillingsdagen, så sent-kohorten kom inn gradvis. Dose = andel av sent-kohorten med fastpris, regnet fra Elhubs daglige målertelling (forutsetter at kohorten følger totalen): okt. 0,22, nov. 0,47, des. 0,64, jan. 0,79, feb. 0,89, mar. 0,95, apr. 0,99.

Brukt på tre måter:

1. *To behandlingsgrupper i D7:* tidlig 3,1 prosent, sent 2,9. Begge behandles som fullt behandlet fra oktober, så sent-tallet er i underkant per faktisk behandlet måler. Nesten lik effekt for to grupper som valgte på ulikt tidspunkt støtter hovedresultatet.
2. *Dose-respons-test (s13):* effekten for sent bør vokse med dosen om den skyldes fastprisen. Med felles sesongprofil stiger effekten nesten én til én med dosen (helning 1,06, KI 0,89–1,23) og nivået i oktober er nær null.
3. *Der det stopper:* med egen sesongprofil for sent-kohorten viser førperioden at sent-bestillerne brukte 0,4–1,1 prosentpoeng mer enn tidlig i feb.–apr., relativt til oktober. Det har samme fasong som dosekurven, så «effekt vokser med dose» kan ikke skilles fra «sent har brattere vinter». Full effekt spriker 1,6–4,6 prosent etter valg av profil. Konklusjon: ikke informativ, holdt utenfor innlegget, står på spørsmålslisten til Elhub (faktisk inntredelsesforløp per kohort).

## 3d. Hvordan dosen er regnet, og hvilke førdata vi har

Elhubs daglige fil (data/processed/elhub_np_mba_daily.parquet) har per dag, prisområde og forbruksgruppe antall målere i alt og antall med Norgespris. Den starter 1. oktober 2025, dagen ordningen trådte i kraft, og går til 2. september 2026.

For husholdninger i hvert av NO1, NO2 og NO5 (src/s13_dose_sent.py):

1. Antall Norgespris-målere 1. oktober 2025 = alle tidlig bestilte.
2. Antall 30. april 2026 = tidlig + alle sent bestilte (sent-vinduet slutter der).
3. Per dag: dose = (antall den dagen − antall 1. okt.) / (antall 30. apr. − antall 1. okt.), avkortet til 0–1. Andelen av tilstrømningen i sent-vinduet som var inne den dagen.
4. Månedssnitt av de daglige dosene: okt. 0,22, nov. 0,47, des. 0,64, jan. 0,79, feb. 0,89, mar. 0,95, apr. 0,99.
5. Koblet på DiD-data etter område og måned; `sent_dose` = dose for sent-radene, 0 for alle andre og for hele førperioden. Dosen varierer ikke med forbruksklasse.

Forutsetning i steg 3: økningen i Norgespris-målere er ikke bare sent-kohorten i statusuttrekket, men inkluderer også nye målere og målere utenfor uttrekket (43 prosent av kohortens bestillere er sene, mot 55 prosent av alle Norgespris-målere). Totalens tilstrømningskurve brukes som anslag på kohortens. Kohortens eget forløp er ikke publisert; det står på Elhub-listen.

| Datasett | Start | Slutt | Brukt til |
|---|---|---|---|
| Daglig Norgespris-telling | 1. okt. 2025 | 2. sep. 2026 | Dose. Kan ikke gå lenger tilbake |
| Forbruk etter bestillingsstatus | okt. 2023 | apr. 2026 | DiD, to førvintre. Uttrekket slutter i april, derfor DiD også |
| Kommunepanel | feb. 2022 | apr. 2026 | NRK-likt design |

Lengre førdata hjelper ikke dosen, som per definisjon er null før oktober 2025. Det som ville hjulpet er kohortens faktiske inntredelsesforløp, eller et oppdatert statusuttrekk for mai–august 2026, der dosen er 1 for alle sene og identifikasjonsproblemet mot sesongprofilen faller bort.

## 4. Fra bestillere til alle husholdninger

Bestillerne står for 77 prosent av husholdningsforbruket i Sør-Norge (ikke 65 prosent av målerne, det er forbruket som teller). 3 prosent × 0,77 ≈ 2,3 prosent. Med spennet 2,4–4,4 fra ulike spesifikasjoner blir det 2,0–3,4 prosent aggregert.

Forutsetning: ikke-bestillerne er upåvirket. Det kan vi ikke teste. Derfor «grovt omregnet».

**Én setning:** «For alle husholdninger i Sør-Norge tilsvarer det 2–3 prosent.»

## 5. Hvor mye av forbruksøkningen er Norgespris?

Husholdninger og hytter i NO1, NO2 og NO5 brukte 18 119 GWh i januar–juni 2026 mot 15 796 i 2025. Det er 2 323 GWh, eller 14,7 prosent mer. Norgespris forklarer 2–3 prosentpoeng av det, om lag en femdel.

Resten er ikke beregnet presist. En grov dekomponering med gradtall sier at 8–14 av de 15 prosentpoengene er vær: 2025 var mildt, januar 2026 var kaldeste enkeltmåned i perioden. Derfor «det meste av resten ser ut til å være vær».

**Én setning:** «Forbruket økte 15 prosent fra 2025. Norgespris står for om lag en femdel. Resten er i hovedsak været.»

## 6. Kontrollene av eget regnestykke

- **Strømstøtte som effektiv pris.** Vi regnet ut hvilken pris husholdningene faktisk møtte per time (spot minus 90 prosent av det over terskelen) og byttet den inn for spot i NRK-designet. Koeffisienten gikk fra 0,0950 til 0,0940. Strømstøtten forklarer ikke NRKs tall.
- **Få grupper.** Vanlige standardfeil er for små med 27 grupper. Wild cluster bootstrap gir intervallet 2,5–3,7. Hovedresultatet holder. Tallene per forbruksklasse (9 grupper) blir langt mer usikre.
- **Kommunepanel med tidskontroll.** Legger man år×måned-effekter til NRK-designet og bruker oppslutningsandel per kommune, får man 5,8 prosent, men intervallet er −3 til +16. Det kan ikke skille 3 fra 8. Derfor er bestillingsdataene hovedkilden.
- **Tidlig og sent bestilte.** Sent bestilte fikk fastpris gradvis gjennom vinteren. Deres effekt vokser i takt med det, men vi klarer ikke skille dette fra at kohortene har ulik sesongprofil. Det trenger data fra Elhub. Ikke brukt i innlegget.

## 7. NRKs andre påstander

- **1 kWh = 1 429 liter vann.** NVEs energiekvivalenter for kraftverk i NO1 og NO2, produksjonsveid, gir 1 485 liter per kWh. Holder innen 4 prosent.
- **Seks minutter dusj = 1,4 kWh.** 36 liter varmet fra 8 til 38 °C er 1,26 kWh; med 90 prosent virkningsgrad på berederen er det 1,4. Holder.
- **20 000 dusjår.** Det er en omregning av hele forbruksøkningen (2 323 GWh ≈ 2 453 GWh for 20 000 dusjår), ikke av Norgespris-effekten. Riktig regnet, men beskriver økningen, ikke ordningen.
- **Nettoeksporten tilsvarer forbruksøkningen.** SSB: nettoeksport januar–juli 2026 var 2 682 GWh mot forbruksøkning 2 323. Holder i størrelsesorden. Fallet i nettoeksport fra 2025 (10 168 GWh) skyldes 63 prosent lavere produksjon og 37 prosent høyere forbruk i hele landet.
- **Inntekt og oppslutning.** Korrelasjonen mellom medianinntekt og oppslutning på kommunenivå er 0,17, 0,45 i NO1. Rikere kommuner bestiller litt mer, som NRK sier.

## 8. Hvordan hele resonnementet kan sies på 30 sekunder

«NRK måler før og etter, uten kontrollgruppe. Den modellen finner 5 prosent effekt også i et år uten Norgespris, så den kan ikke brukes. Elhub har data der man kan sammenligne dem som bestilte med dem som ikke gjorde det, i samme område og måned. Da er effekten om lag 3 prosent for bestillerne, 2–3 for alle, og null når man tester på et falskt innføringsår. Norgespris økte forbruket, men med en femdel av det NRK antyder. Vannregnestykket deres er riktig.»

## 9. Spørsmål du vil få, og svaret

- *Hvordan vet du hva NRK gjorde?* Jeg vet det ikke. Artikkelen oppgir metoden, ikke spesifikasjonen. Jeg har bygget samme type modell og får samme type tall. Jeg har bedt NRK oppgi spesifikasjonen.
- *De som bestilte er annerledes enn de som ikke gjorde det.* Ja. Derfor sammenligner jeg endring, ikke nivå, kontrollerer for deres egen sesongprofil fra før ordningen, og tester med placebo.
- *Du måler mot strømstøtte, ikke mot markedspris.* Riktig. Det gjør 3 prosent til et forsiktig anslag, ikke et for høyt.
- *Er 3 prosent lite?* Nei. Det er 400–500 GWh i halvåret, og det er en reell kostnad. Poenget er at det ikke er 8.
- *Hvorfor bryr du deg når retningen er riktig?* Fordi tallet brukes til å beslutte. En effekt målt uten kontrollgruppe er ikke en effekt.

## 9b. Den svakeste antagelsen: ingen bestillerspesifikk endring vinteren 2025/26

**Hva designet fjerner:** faste nivåforskjeller, forskjeller som gjentar seg med kalenderen, og alt som treffer alle i samme område og måned. **Hva det ikke fjerner:** noe nytt vinteren 2025/26 som traff bestillerne mer enn ikke-bestillerne og ikke skyldes fastprisen. Eksempler: bestillerne (oftere huseiere med høy inntekt) kjøpte flere elbiler eller varmepumper akkurat denne vinteren; bestillerne er mer følsomme for kulde enn ikke-bestillerne (gradtall er felles per område, følsomheten kan være ulik); folk som planla å bruke mer strøm valgte fastpris, slik at bestillingen er symptom på en planlagt økning, ikke årsak.

**Hvorfor tre prosentpoeng:** effekten er 3,0. Et tenkt sjokk på 1 prosentpoeng gir 2,0 igjen, 2 gir 1,0, 3 gir null (verifisering/seleksjon_sensitivitet.csv). Det sier hvor stort sjokket måtte være, ikke at det finnes. I førperioden svinger forskjellen mellom gruppene høyst 1,1 prosentpoeng i en enkeltmåned og null i snitt (verifisering/pre_event_study.csv). Et sjokk på 3 prosentpoeng over en hel vinter er tre ganger større enn det største avviket observert uten ordning.

**Hvorfor placebo ikke hjelper:** placeboen tester om gruppene *pleier* å utvikle seg ulikt fra år til år. Svaret er nei. Men et sjokk som bare traff 2025/26 finnes ikke i 2023–2025-dataene, så en test på de årene kan ikke oppdage det. Placeboen utelukker gjentakende mønstre, ikke et engangsmønster som kom samme vinter som ordningen.

**Hvordan det kunne testes:** elbil- og varmepumperegistreringer per bestillingsstatus; timefordeling av økningen (ladetimer?); dose-respons på sent-kohorten med Elhubs faktiske inntredelsesforløp.

**Én setning:** «Jeg har vist at bestillere og ikke-bestillere pleide å følge hverandre. Det jeg ikke kan utelukke, er at noe annet enn fastprisen fikk akkurat bestillerne til å bruke mer akkurat denne vinteren. Det måtte i så fall være tre ganger større enn noe jeg har sett i årene før.»

