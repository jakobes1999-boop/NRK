# Hvilken modell har NRK brukt? Et spesifikasjonssøk forklart

Dato: 06.09.2026. Skript: `src/s18_nrk_spesifikasjonssok.py`. Tabeller: `output/tab_nrk_spes_sok.md` (topp 15, dimensjoner, spenn), `output/tab_nrk_spes_sok.csv` (alle kjøringer), `_dimensjoner.csv`, `_periode.csv`. Teknisk versjon av notatet: `NRK_SPESIFIKASJONSSOK_2026-09-06_v1_teknisk.md`.

**Alle tall er til godkjenning.** De er regnet på vårt eget panel (197 kommuner, februar 2022 til april 2026) og er ikke NRKs tall.

## Spørsmålet, og hvorfor det er viktig

NRK oppgir fire koeffisienter og en forklaringskraft, men ikke hvordan modellen er satt opp. Vi vet ikke om venstresiden er logaritme, om forbruket er per måler, hvordan Norgespris er kodet, om det er kontroll for sesong, hvilke enheter inntekt og spotpris står i, eller hvor mange kommuner som er med.

Det betyr noe for kritikken. Hovedinnvendingen vår er at NRKs modell mangler kontrollgruppe fordi Norgespris-variabelen er lik for alle kommuner og skifter på samme dato. Hvis NRK i stedet brukte oppslutningsandel per kommune, eller hadde sesongkontroll i modellen, ville innvendingen måtte formuleres annerledes. Vi trenger derfor å vite hvilke oppsett som er *forenlige* med tallene NRK oppgir, og hvilke som ikke er det.

## Metoden: bruk tallene som fingeravtrykk

Tanken er enkel. Hver koeffisient NRK oppgir er et avtrykk av modellen som laget den. Gradtallskoeffisienten forteller hvordan modellen håndterer sesong. Spotkoeffisienten forteller hvilken enhet prisen står i. Forklaringskraften forteller hvor mye variasjon modellen forklarer, og dermed hva slags R² det er. Kjører vi mange kandidatmodeller på våre data og ser hvilke som gir lignende avtrykk, kan vi utelukke oppsett som ikke passer og peke på dem som gjør det.

Rutenettet dekker ni valg:

| Valg | Alternativer testet |
|---|---|
| Venstreside | log kWh, log kWh per måler, kWh i nivå, kWh per måler i nivå |
| Norgespris-variabel | 0/1 fra oktober 2025, 0/1 fra september 2025, andel målere med Norgespris (Privat, husholdning) |
| Sesongkontroll (tids-FE) | ingen, kalendermåned, år, år × måned |
| Boligstørrelse | med, uten |
| Inntektsenhet | kroner, 1 000 kr, 10 000 kr, 100 000 kr, logaritme |
| Spotenhet | øre/kWh, kr/MWh, kr/kWh |
| Gradtallsbase | 17 grader, 18 grader |
| Vekting | uvektet, vektet med antall målere |
| Kommuneutvalg | alle 197, bare entydig prisområde, bare kommuner med egen værstasjon |

Det gir 784 kjernemodeller og 6 384 kjøringer når enhetsvalgene regnes med. For hver kjøring måler vi avstanden til NRKs tall som summen av relative avvik på de fire koeffisientene pluss avviket i R².

## Funn 1: gradtall og spotpris sier «ingen sesongkontroll»

Dette er det viktigste funnet. Gradtallskoeffisienten forteller hvor mye forbruket øker per grad kaldere. Har modellen ikke annen sesongkontroll, må gradtallet bære hele vinterøkningen alene, og koeffisienten blir høy. Legger man inn kalendermånedseffekter, tar de over mye av sesongen, og gradtallskoeffisienten faller.

| Sesongkontroll | Gradtall | Spot | R² within |
|---|---|---|---|
| Ingen | 0,00184–0,00190 | −0,00040 til −0,00032 | 0,935–0,961 |
| År-effekter | 0,00185–0,00191 | −0,00045 til −0,00040 | 0,937–0,963 |
| Kalendermåned-effekter | 0,00106–0,00114 | −0,00027 til −0,00019 | 0,958–0,980 |
| År × måned-effekter | 0,00068–0,00081 | −0,00012 til +0,00023 | 0,568–0,652 |
| **NRK** | **0,0019** | **−0,0005** | **0,9376** |

NRKs gradtall på 0,0019 treffes bare i de to første radene. Med kalendermånedseffekter halveres koeffisienten til 0,0011, og med år × måned-effekter blir den 0,0007. Spotkoeffisienten peker samme vei: negativ og nær −0,0005 uten sesongkontroll, nær null med. Vår nærmeste spot er −0,00045, 10 prosent fra NRKs.

**Én setning:** «NRKs gradtallskoeffisient er så høy at modellen ikke kan ha hatt egen sesongkontroll; gradtallet bærer hele vinteren alene.»

## Funn 2: forklaringskraften er «within-R²»

93,76 prosent kan bety tre ting. Overall-R² måler hvor mye av all variasjon, også mellom kommuner, modellen forklarer. Within-R² måler hvor mye av variasjonen *innenfor* hver kommune over tid som forklares. OLS-R² med kommunedummyer teller kommuneeffektene som forklaring.

| Type R² | Vår M1 |
|---|---|
| Overall | 0,13 |
| Within | 0,94 |
| OLS med kommunedummyer | 0,99 |

Bare within-R² er i riktig størrelsesorden. Det bekrefter at NRK har en modell med faste kommuneeffekter og rapporterer forklaringskraften slik programvare vanligvis gjør det for slike modeller. Nærmest 0,9376 kommer log samlet forbruk med år-effekter på utvalget med entydig prisområde: 0,93749.

## Funn 3: spot er i øre/kWh, gradtallsbasen betyr ingenting

Spot i kr/MWh ville gitt en koeffisient rundt −0,00004, i kr/kWh rundt −0,04. Bare øre/kWh gir størrelsesorden 0,0005. Gradtall med base 18 i stedet for 17 grader gir samme koeffisient til tredje desimal, fordi de to seriene har korrelasjon 0,9999.

## Funn 4: Norgespris-koeffisienten kan treffes på mange måter, og sier derfor lite

0,0822 treffes for eksempel av log samlet forbruk med 0/1-variabel fra september 2025 (0,0800–0,0815). Men den flyttes av nesten alt:

| Endring fra vår M1 (0,0950) | Ny koeffisient |
|---|---|
| Per måler i stedet for samlet | 0,0840 |
| 0/1 fra september i stedet for oktober | 0,0814 |
| Vektet med antall målere | 0,0859 |
| Kalendermåned-effekter | 0,0717 |
| Oppslutningsandel i stedet for 0/1 | 0,157–0,160 |
| Andel med år × måned-effekter | 0,241 |

Spennet i hele rutenettet er 0,048 til 0,32. At vi treffer 0,0822 beviser derfor ikke at vi har NRKs modell. Det viser snarere at tallet i stor grad er et spesifikasjonsvalg. Nivåmodeller er utelukket: der blir koeffisienten 817 867 kWh for samlet forbruk og 85,9 kWh per måler, så 0,0822 må være fra en logaritmisk venstreside. Det svarer til 8,6 prosent.

## Funn 5: inntekt treffes ikke

NRK oppgir 0,0024. Med log samlet forbruk får vi 0,0009 per 1 000 kroner. Med log per måler, inntekt i 10 000 kroner og vekting får vi 0,0031, som er nærmest i hele rutenettet, 30 prosent fra NRKs. Ingen kjøring treffer alle fire koeffisienter innenfor 30 prosent samtidig, og det er inntekten som binder.

Tre forklaringer kan ikke skilles på våre data: NRK har inntektstall for 2021 og 2025 som vi mangler, NRK bruker et annet inntektsbegrep enn medianinntekt etter skatt for husholdninger, eller NRK har en enhet vi ikke har testet. Inntektskoeffisienten er den minst stabile i vårt panel: 0,0008 på 2022–2024 og 0,0015 på 2023–2026. Periodeforskjellen alene kan være nok til å forklare avviket.

## Nærmeste oppsett

Etter kriteriet «minst mulig største avvik»: log kWh per måler, 0/1 fra oktober 2025, ingen sesongkontroll, med boligstørrelse, inntekt i 10 000 kr, spot i øre/kWh, vektet, kommuner med egen værstasjon. Gradtall 0,00187, spot −0,00035, Norgespris 0,0753, inntekt 0,00317, within-R² 0,961. Største avvik 32 prosent, på inntekt.

Nest beste familie: log samlet forbruk, 0/1 fra september 2025, ingen sesongkontroll. Gradtall 0,00190, spot −0,00036, Norgespris 0,080–0,082, within-R² 0,935–0,940, inntekt 0,0009.

## Hva dette betyr for kritikken

Tolkningen «0/1-variabel uten sesongkontroll» går fra indisium til godt underbygget. Det er ikke ett tall som avgjør det, men tre sammen: gradtall 0,0019, negativ spot rundt 0,0005 og R² i underkant av 94 prosent er hver for seg forenlige med flere oppsett, men bare sesongfrie oppsett gir alle tre samtidig.

Det innebærer at Norgespris-variabelen identifiseres ved at oktober 2025 til juni 2026 sammenlignes med gjennomsnittet av alle tidligere måneder, justert for gradtall. Det er nettopp oppsettet placebotesten M5 er kjørt i: den finner 5,2 prosent «effekt» av en innføring i oktober 2024. Placebo-argumentet står derfor som før.

To forbehold i vår disfavør: vi treffer ikke inntektskoeffisienten, og vi kan ikke utelukke at NRKs venstreside eller inntektsvariabel avviker fra vår på en måte som også påvirker Norgespris-koeffisienten. Og kalendermånedseffekter er ikke utelukket av Norgespris-koeffisienten alene, bare av gradtall, spot og R² sett sammen.

## Hva vi ikke kan avgjøre uten NRK

- **Perioden.** Elhubs kommunefil dekker 1. februar 2022 til 30. april 2026. NRK har 2021 og mai–juni 2026 i tillegg, om lag 17 måneder mer, inkludert prissjokkvinteren 2021. Kommunetall for disse månedene finnes ikke i åpne data.
- **Forbruksgruppen.** Kommunefilen har bare «Privat», altså husholdning og hytte samlet. Vi kan ikke skille ut husholdning alene per kommune.
- **Inntektsvariabelen.** Begrep, årgang og enhet er ikke oppgitt.
- **Kommuneutvalget.** Antall kommuner er ikke oppgitt. Utvalget flytter Norgespris-koeffisienten med opptil 0,0045.
- **Vekting og R²-definisjon.** Ikke oppgitt. Vekting flytter koeffisienten med 0,0091.

Fire spørsmål til NRK ville avgjøre alt: venstresidens form, Norgespris-kodingen, inntektsvariabelen og antall kommuner. Utkast ligger i `notat/SPORSMAL_ELHUB_NRK.md`.

## Slik kan det sies på 30 sekunder

«NRK oppgir fire koeffisienter men ikke modellen. Vi kjørte 6 000 varianter på åpne data og brukte koeffisientene som fingeravtrykk. Gradtallet på 0,0019 kan bare oppstå i en modell uten egen sesongkontroll; med kontroll halveres det. Forklaringskraften bekrefter en modell med faste kommuneeffekter og ingenting for tid. Det er nøyaktig den modelltypen som finner 5 prosent effekt i et år uten Norgespris. Det eneste vi ikke treffer er inntektskoeffisienten, og det kan skyldes at NRK har to år mer data enn vi har tilgang til.»
