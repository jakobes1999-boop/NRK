# Etterprøving av NRKs analyse «Prisen for billig strøm»

*Arbeidsnotat, utkast 5. september 2026. Felt merket ⟦…⟧ fylles inn fra `output/` etter at pipelinen er kjørt med reelle data.*

## 1. Hva NRK har gjort

NRK (2026) hevder at Norgespris har økt husholdningenes strømforbruk, og illustrerer kostnaden ved billig strøm med hvor mye vann som må gjennom turbinene for å varme en dusj. Analysen bygger på to regnestykker. Det første er en omregning fra kilowattimer til vann: NRK bruker et vektet snitt av energiekvivalentene for kraftverkene i NO1 og NO2 fra NVE, som gir 1 429 liter vann per kilowattime. Det andre er en regresjon med faste effekter for kommuner, der månedlig husholdningsforbruk fra Elhub forklares med energigradtall fra Meteorologisk institutt, månedlig spotpris, innføringen av Norgespris, medianinntekt fra skattelistene og boligstørrelse fra SSB. Datasettet dekker 2021 til juni 2026 for NO1, NO2 og NO5. NRK rapporterer koeffisientene 0,0019 for gradtall, −0,0005 for spotpris, 0,0822 for Norgespris og 0,0024 for medianinntekt, alle signifikante på 0,1-prosentnivå, med en forklaringskraft på 93,8 prosent.

Koeffisientenes størrelse tilsier at den avhengige variabelen er logaritmen av forbruket. Norgespris-koeffisienten på 0,0822 skal da leses som at forbruket er om lag 8,6 prosent høyere etter innføringen, alt annet likt. Det er dette tallet som bærer saken.

## 2. Vann- og dusjregnestykket

Regnestykket henger sammen. 1 429 liter per kilowattime er det samme som en energiekvivalent på 0,700 kWh/m³, og 1,4 kWh ganger 1 429 liter gir 2 001 liter, som NRK runder til 2 000. Dusjen på 6 liter i minuttet ved 38 grader bruker om lag 0,21 kWh per minutt dersom inntaksvannet holder 8 grader; 1,4 kWh svarer da til en dusj på 6–7 minutter, eller rundt 40 liter varmtvann. Forholdet mellom kraftverksvann og dusjvann blir om lag 50 til 1 uavhengig av dusjens lengde. NRK oppgir en dusj på seks minutter; med 6 liter i minuttet og 38 grader krever 1,4 kWh da inntaksvann på om lag 4,6 grader, ikke 8. Forutsetningene er likevel innenfor det rimelige.

Selve energiekvivalenten etterprøver vi mot NVEs vannkraftdatabase (felt `EnEkv`, vektet med midlere årsproduksjon 1991–2020). Vårt anslag for NO1 og NO2 samlet er ⟦x,xxx⟧ kWh/m³, tilsvarende ⟦x xxx⟧ liter per kilowattime, det vil si ⟦x⟧ prosent fra NRKs tall (Tabell 1). Merk at NVE ikke oppgir energiekvivalent for alle småkraftverk, og at veiing med installert effekt i stedet for produksjon gir et noe annet tall. Avviket er uansett ikke av en størrelse som endrer poenget i saken.

*Tabell 1: Produksjonsveid energiekvivalent (fra `output/tab_energiekvivalent.csv`)*

| Område | Antall kraftverk | Produksjon (GWh/år) | kWh/m³ | Liter per kWh | Avvik fra NRK |
|---|---|---|---|---|---|
| NO1 | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| NO2 | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| NO1+NO2 | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |

## 3. Regresjonsanalysen: hva som kan gå galt

Det metodiske hovedspørsmålet er hvordan «innføring av Norgespris» er målt, og NRK oppgir ikke dette. Vi ser to muligheter, og de har ulike svakheter.

Dersom variabelen er en dummy som er lik én for alle kommuner fra oktober 2025, sammenlignes forbruket etter 1. oktober 2025 med forbruket før, justert for gradtall, spotpris og de øvrige kontrollvariablene. Da fanger koeffisienten alt annet som skjedde i samme periode og som ikke er dekket av kontrollvariablene: kaldere vinter enn gradtallene fanger opp (vind, snø, solinnstråling), fortsatt vekst i elbil- og varmepumpebestand, endret strømstøtte for dem som ikke valgte Norgespris, og endrede prisforventninger. Modellen kan i så fall ikke inneholde faste effekter for tid, for da ville Norgespris-dummyen vært perfekt kollineær med dem. Den høye forklaringskraften på 93,8 prosent er ikke et argument for at effekten er riktig identifisert; i et kommunepanel med faste effekter og gradtall forklares det aller meste av variasjonen uansett.

Dersom variabelen i stedet er andelen målere i kommunen som har valgt Norgespris, identifiseres effekten av at kommuner med høy oppslutning endrer forbruket mer enn kommuner med lav oppslutning. Det er et bedre design, fordi det tillater faste effekter for tid. Problemet blir da selvseleksjon: husholdninger som forventer høyt forbruk har mest å tjene på fastpris, og kommuner der mange velger Norgespris kan ha andre kjennetegn, for eksempel høy andel eneboliger med elektrisk oppvarming. Med faste effekter for kommune er nivåforskjeller ikke et problem, men ulike sesongprofiler og ulik følsomhet for kulde er det.

Elhub-dataene har i tillegg to egenskaper som påvirker tolkningen. Forbruksgruppen «Privat» omfatter både husholdninger og hytter, slik at forbruket i hyttekommuner svinger med hyttebruk. Og verdier basert på færre enn 100 målere er satt til null i Norgespris-statistikken, noe som gir målefeil i små kommuner. Vi vil også bemerke at medianinntekt innenfor en kommune bare varierer fra år til år, slik at inntektskoeffisienten på 0,0024 i praksis fanger en trend, ikke en inntektseffekt.

## 4. Vår etterprøving

Vi gjenskaper NRKs modell så tett som mulig og utvider den i to retninger. Datagrunnlaget er det samme som NRKs, med unntak av at vi bruker SSBs medianinntekt etter skatt (tabell 06944) i stedet for skattelistene, og at spotprisene starter i desember 2021 (hvakosterstrommen.no, Nord Pool day-ahead). Gradtall beregnes fra døgnmiddeltemperatur i MET Frost med 17 grader som basis. Kommune kobles til prisområde etter fylke med kjente unntak, kryssjekket mot NVEs kraftverksregister.

Modellene er som følger. M1 er NRK-lik: logaritmen av husholdningsforbruket forklares med gradtall, spotpris, medianinntekt, boligstørrelse og en Norgespris-dummy fra oktober 2025, med faste effekter for kommune og standardfeil klustret på kommune. M2 legger til kalendermåned. M3 erstatter dummyen med andel målere på Norgespris og legger til faste effekter for hver måned i panelet, slik at alt som er felles for alle kommuner i en måned tas ut. M4 er M3 med forbruk per målepunkt som avhengig variabel. M5 er en placebo: vi later som ordningen ble innført i oktober 2024 og kjører M1 på data til og med september 2025. Finner vi en «effekt» der, er M1-designet upålitelig.

*Tabell 2: Faste-effekter-regresjoner, log husholdningsforbruk (fra `output/tab_fe_resultater.csv`)*

| | NRK | M1 NRK-lik | M2 + sesong | M3 to-veis FE, andel | M4 per målepunkt | M5 placebo |
|---|---|---|---|---|---|---|
| Gradtall | 0,0019*** | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| Spotpris (øre/kWh) | −0,0005*** | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| Norgespris (dummy) | 0,0822*** | ⟦⟧ | ⟦⟧ | – | – | ⟦⟧ |
| Norgespris (andel målere) | – | – | – | ⟦⟧ | ⟦⟧ | – |
| Medianinntekt (1 000 kr) | 0,0024*** | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| Boligstørrelse (m²) | ikke oppgitt | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| R² | 0,938 | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |
| N | ikke oppgitt | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |

Koeffisienten for andel målere i M3 skal leses som effekten av å gå fra null til full oppslutning; ganget med faktisk oppslutning i området (⟦xx⟧ prosent per april 2026 ifølge Elhub) gir den effekten på samlet forbruk.

## 5. Eget design: bestillere mot ikke-bestillere

Elhub har publisert et engangsuttrekk som deler forbruket i NO1, NO2 og NO5 etter om måleren hadde bestilt Norgespris per april 2026, og etter gruppe for estimert årsforbruk. Serien går fra oktober 2023, altså to år før ordningen. Dette gir det NRKs kommunedata mangler: en kontrollgruppe som opplevde samme vær og samme spotpris, men ikke fikk fastpris. Sammenligningen innenfor grupper for årsforbruk fjerner dessuten den mest åpenbare seleksjonen, at storforbrukere velger Norgespris.

Vi estimerer en diff-in-diff-modell der logaritmen av forbruk per målepunkt forklares med faste effekter for gruppe (område × status × årsforbruksgruppe), faste effekter for område × måned og et samspill mellom «bestilt» og «etter 1. oktober 2025», vektet med antall målere. I tillegg estimerer vi effekten måned for måned med september 2025 som referanse. Månedene før oktober 2025 er en test av parallelle trender: dersom bestillerne allerede før ordningen utviklet seg annerledes enn ikke-bestillerne, er ikke designet troverdig.

Før ordningen brukte målere som senere bestilte Norgespris ⟦xx⟧ prosent mer per målepunkt enn dem som ikke bestilte (Tabell 3). Etter innføringen er forskjellen ⟦xx⟧ prosent, og diff-in-diff-estimatet er ⟦x,xxx⟧ (standardfeil ⟦⟧), det vil si ⟦x,x⟧ prosent høyere forbruk (Tabell 4). Snittet av koeffisientene før oktober 2025 er ⟦⟧, ⟦som er forenlig / ikke forenlig⟧ med parallelle trender (Figur 1).

*Tabell 3: Forbruk per målepunkt før oktober 2025, kWh per måned (fra `output/tab_did_nivaa_foer.csv`)*

| Område | Ikke bestilt | Bestilt | Forskjell |
|---|---|---|---|
| NO1 | ⟦⟧ | ⟦⟧ | ⟦⟧ prosent |
| NO2 | ⟦⟧ | ⟦⟧ | ⟦⟧ prosent |
| NO5 | ⟦⟧ | ⟦⟧ | ⟦⟧ prosent |

*Tabell 4: Diff-in-diff-estimat (fra `output/tab_did.csv`)*

| Koeffisient | Standardfeil | p-verdi | Effekt i prosent | N |
|---|---|---|---|---|
| ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ | ⟦⟧ |

*Figur 1: Event-study, forskjell i forbruk per målepunkt mellom bestillere og ikke-bestillere (`output/fig_event_study_did.png`)*

Også dette designet har begrensninger. Statusen er målt per april 2026, slik at husholdninger som bestilte sent i perioden regnes som behandlet fra oktober 2025. Det trekker estimatet mot null. Og fordi Norgespris og strømstøtte ikke kan kombineres, er kontrollgruppen ikke ubehandlet i streng forstand: den fikk strømstøtte i timer med høy pris. Effekten vi måler er derfor forskjellen mellom fastpris og strømstøtte, ikke mellom fastpris og full spotpris. Det er imidlertid også det relevante sammenligningsgrunnlaget for den politiske diskusjonen.

## 6. Foreløpig vurdering

⟦Fylles inn når tallene er klare. Sentrale spørsmål: (1) Gjenfinner vi NRKs 8 prosent i M1? (2) Overlever effekten to-veis faste effekter i M3, og er placeboen i M5 nær null? (3) Gir diff-in-diff-designet en effekt av samme størrelse, og holder parallelle trender? Dersom M1 gir 8 prosent men M3 og diff-in-diff gir vesentlig mindre, er NRKs tall antagelig for høyt og drevet av tidsvariasjon som ikke skyldes ordningen. Dersom alle tre designene gir samme størrelse, står NRKs konklusjon støtt.⟧

## Kilder

Elhub (2026): Datakatalog – forbruk per kommune, gruppe og time; Norgespris antall målere per kommune; forbruk etter Norgespris-bestillingsstatus, oktober 2023–april 2026. CC BY 4.0.
Elhub (2026): Hva er Norgespris. Ordningen gjelder 1. oktober 2025–31. desember 2026, 40 øre/kWh ekskl. mva., inntil 5 000 kWh per måned for bolig.
Meteorologisk institutt: Frost API, døgnmiddeltemperatur.
NRK (2026): Prisen for billig strøm, med metodebeskrivelse.
NVE: Vannkraftdatabasen, felt EnEkv og MidProd_91_20.
SSB: Tabell 06944 Inntekt for husholdninger; tabell 06513 Boliger etter bygningstype og bruksareal.
hvakosterstrommen.no: Spotpriser per time, NO1–NO5, fra 1. desember 2021.
