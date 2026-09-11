# Spesifikasjonssøk: hvilken modell reproduserer NRKs koeffisienter?

Dato: 06.09.2026. Skript: `src/s18_nrk_spesifikasjonssok.py`.
Tabeller: `output/tab_nrk_spes_sok.csv`, `output/tab_nrk_spes_sok.md`,
`output/tab_nrk_spes_sok_dimensjoner.csv`, `output/tab_nrk_spes_sok_periode.csv`.

**Alle tall i notatet er til godkjenning.** De er regnet på vårt eget panel
(`data/processed/panel.parquet`, 197 kommuner, februar 2022 – april 2026) og er ikke
NRKs tall.

Mål for søket er NRKs metodeboks (`kilder/nrk_prisen_for_billig_strom.md`, linje 251–285):
energigradtall 0,0019, månedlig spotpris −0,0005, innføring av Norgespris 0,0822,
medianinntekt 0,0024, forklaringskraft 93,76 prosent.

Rutenettet dekker venstresidens form (log kWh, log kWh per måler, kWh og kWh per måler i
nivå), Norgespris-koding (0/1 fra oktober 2025, 0/1 fra september 2025, andel målere for
Privat og for husholdning), tids-FE (ingen, kalendermåned, år, år × måned), bruksareal med
og uten, inntekt i kr, 1 000 kr, 10 000 kr, 100 000 kr og log, spot i øre/kWh, kr/MWh og
kr/kWh, gradtall med base 17 og 18 grader, uvektet og vektet med antall målepunkter, og tre
kommuneutvalg. Til sammen 784 kjernemodeller og 6 384 kjøringer etter enhetsvalg.

## 1 Konklusjon

Tre av NRKs fire koeffisienter og forklaringskraften lar seg gjenskape på våre data, mens
inntektskoeffisienten ikke gjør det. Gradtallskoeffisienten treffer 0,0019 i praktisk talt
alle spesifikasjoner uten sesongkontroll (spenn 0,00184–0,00191), spotkoeffisienten kommer
nærmest med −0,00045 mot NRKs −0,0005, og Norgespris-koeffisienten 0,0822 ligger godt
innenfor spennet vårt (0,048–0,32 avhengig av spesifikasjon). Forklaringskraften 93,76
prosent samsvarer med within-R² – vår tilsvarende ligger på 0,9353–0,9633 – og ikke med
overall-R² (0,13) eller OLS-R² med kommunedummyer (0,9937). Inntektskoeffisienten kommer
ikke nærmere enn 0,0031 mot NRKs 0,0024, og da bare med log kWh per måler, inntekt i
10 000 kr og vekting; med log samlet forbruk og inntekt i 1 000 kr får vi 0,0009–0,0011.
Ingen av de 6 384 kjøringene treffer alle fire koeffisientene innenfor 30 prosent relativt
avvik samtidig, og bindingen ligger i inntekt. Spot- og gradtallsnivåene identifiserer to
enhetsvalg: spot er oppgitt i øre/kWh, og gradtallet er en månedssum omtrent som vår
(basetemperaturen 17 mot 18 grader er uten praktisk betydning, korrelasjon 0,9999).
Kombinasjonen av gradtall 0,0019, negativ spotkoeffisient av størrelsesorden 0,0005 og R²
i underkant av 94 prosent er forenlig med ingen tids-FE eller år-FE, og er ikke forenlig
med kalendermåned-FE eller år × måned-FE.

## 2 Hva som må til for å treffe hver koeffisient

Tallene under er hentet fra `output/tab_nrk_spes_sok.md`, tabellen «Koeffisientspenn per
tids-FE» og «Beste treff per koeffisient».

**Energigradtall 0,0019.** Treffes med 0,0 prosent avvik, men bare uten sesongkontroll: uten
tids-FE gir rutenettet 0,00184–0,00190, med år-FE 0,00185–0,00191. Med kalendermåned-FE
faller koeffisienten til 0,00106–0,00114 og med år × måned-FE til 0,00068–0,00081, altså
under halvparten av NRKs verdi. Basetemperaturen betyr lite: base 18 grader gir samme
koeffisient til tredje desimal.

**Spotpris −0,0005.** Enheten er identifisert. I øre/kWh ligger vårt spenn på −0,00045 til
−0,00032; i kr/MWh ville de samme modellene gitt om lag −0,00004 og i kr/kWh om lag −0,037,
begge langt fra NRKs tall. Nærmeste treff er −0,00045 (10,1 prosent avvik) med år-FE og
utvalget der kommunen har egen værstasjon. Uten tids-FE kommer vi til −0,00040. Med
kalendermåned-FE (−0,00027 til −0,00019) og år × måned-FE (−0,00012 til +0,00023) kommer vi
ikke i nærheten.

**Norgespris 0,0822.** Denne er lettest å treffe, og treffes på mange måter. Vår M1-linje gir
0,0950. Overgang til log kWh per måler trekker ned 0,0111, vekting med antall målepunkter
0,0091, dummy fra september i stedet for oktober 0,0137 og kalendermåned-FE 0,0234;
andelsvariablene trekker opp 0,062–0,065. Flere kombinasjoner lander på 0,082, for eksempel
log samlet forbruk med dummy fra september (0,0814). Log per måler alene gir 0,0840 og vekting av
log samlet forbruk 0,0859, mens de to kombinert gir 0,0753. At koeffisienten kan gjenskapes er derfor lite informativt i seg selv – spennet i
rutenettet er 0,048 til 0,32.

**Medianinntekt 0,0024.** Ingen enhet gir treff. Med log samlet forbruk får vi 0,0009 per
1 000 kr; da må enheten være 2 670 kr for å gi 0,0024. Med log per måler får vi 0,00032 per
1 000 kr, altså 0,0032 per 10 000 kr, som er nærmeste treff i hele rutenettet med 29,9
prosent avvik. Koeffisienten er samtidig den minst stabile over tid: på 2022-02–2024-12 er
den 0,00078 per 1 000 kr, på 2023-01–2026-04 er den 0,00146, og fra 2024 og framover er den
absorbert av kommune-FE fordi SSB-inntekten vår er framskrevet fra 2024.

**Forklaringskraft 93,76 prosent.** Bare within-R² er i riktig størrelsesorden. Overall-R² er
0,13 og OLS-R² med kommunedummyer er 0,9937 i M1-oppsettet. Blant våre spesifikasjoner ligger
within-R² på 0,9353–0,9610 uten tids-FE og 0,9366–0,9633 med år-FE, mens kalendermåned-FE gir
minst 0,9578 og år × måned-FE bare 0,57–0,65. Nærmest 0,9376 kommer log samlet forbruk med
år-FE på utvalget med entydig prisområde (0,93749).

**Venstresidens form.** Nivåmodellene kan utelukkes for Norgespris-koeffisienten: koeffisienten
blir 817 867 kWh for samlet kommuneforbruk og 85,9 kWh per måler, altså ikke 0,0822 i noen
enhet. Den impliserte relative effekten i nivåmodellene er 6,6 og 7,9 prosent, som er i samme
størrelsesorden som log-modellene. Tallet 0,0822 er derfor med rimelig sikkerhet en
semi-elastisitet fra en log-venstreside, som svarer til 8,6 prosent.

## 3 Treffer noen spesifikasjon alle fire samtidig?

Nei. Antall kjøringer med alle fire relative avvik under 30 prosent er null; det samme
gjelder ved 20, 10 og 5 prosent. Med kravet avvik under 10 prosent på gradtall og
Norgespris og under 30 prosent på spot står 154 kjøringer igjen, og av disse er minste avvik
på inntekt 60 prosent. Etter minimaks-kriteriet (minst mulig største avvik) er det beste
oppsettet log kWh per måler, 0/1 fra oktober 2025, ingen tids-FE, med bruksareal, inntekt i
10 000 kr, spot i øre/kWh, vektet med antall målepunkter, utvalget med egen værstasjon:
gradtall 0,00187, spot −0,00035, Norgespris 0,0753, inntekt 0,00317, within-R² 0,9608. Største
avvik er da 32 prosent, på inntekt.

Nest beste familie – log samlet forbruk, dummy fra september 2025, uten tids-FE – gir
gradtall 0,00190, spot −0,00036, Norgespris 0,0800–0,0815, within-R² 0,9354–0,9402, men
inntekt bare 0,00092–0,00096.

Tre forklaringer på inntektsavviket kan ikke skilles fra hverandre på våre data: NRK har to
ekstra år med inntektsvariasjon (2021 og 2025-tall vi ikke har), NRK kan bruke et annet
inntektsbegrep enn medianinntekt etter skatt for husholdninger (SSB-tabell 06944), eller
NRK kan ha en annen enhet enn de fire vi har testet. Periodefølsomheten vi måler – 0,00078
mot 0,00146 mellom to delperioder – er stor nok til at den første forklaringen alene kan
være tilstrekkelig.

## 4 Hva dette betyr for kritikken

Tolkningen «0/1-dummy uten sesongkontroll» står seg og styrkes. Gradtallskoeffisienten
0,0019 og en negativ spotkoeffisient av størrelsesorden 0,0005 er begge uforenlige med
kalendermåned-FE og med år × måned-FE på våre data: med sesongkontroll halveres gradtallet
og spoteffekten går mot null, fordi sesongvariasjonen da fanges av tidsdummyene. Den
oppgitte forklaringskraften peker samme vei – 93,76 prosent samsvarer med våre 0,935–0,963
uten sesongkontroll, mens en to-veis modell ville gitt 0,57–0,65. Modellen bak NRKs tabell
har derfor med stor sannsynlighet ingen sesongkontroll ut over energigradtallet, og
Norgespris-dummyen identifiseres av at oktober 2025 – juni 2026 sammenlignes med et
gjennomsnitt av alle tidligere måneder etter gradtallsjustering.

Placebo-argumentet berøres ikke. Placebotesten (M5 i `src/s07_estimate_fe.py`) legger
«innføringen» til oktober 2024 på data til og med september 2025 og gir 0,0509, altså 5,2
prosent forbruksøkning på en dato uten tiltak. Den testen er kjørt i nettopp det oppsettet
spesifikasjonssøket nå peker mot som NRKs, og er derfor like relevant etter søket som før.
At Norgespris-koeffisienten 0,0822 kan gjenskapes på flere måter svekker heller ikke
argumentet: den samme koeffisienten faller til 0,0717 med kalendermåned-FE og til 0,0481–
0,0625 i deler av rutenettet, mens andelsvariantene gir opptil 0,32. Størrelsen på tallet
er altså i stor grad et spesifikasjonsvalg, ikke et robust estimat.

To presiseringer i vår disfavør bør stå med. For det første treffer vi ikke NRKs
inntektskoeffisient, og vi kan ikke utelukke at NRKs venstreside eller inntektsvariabel
avviker fra vår på en måte som også påvirker Norgespris-koeffisienten. For det andre er
kalendermåned-FE ikke fullstendig utelukket av Norgespris-koeffisienten alene – 0,0822 er
innenfor rekkevidde også der – det er gradtall, spot og R² sett samlet som utelukker den.

## 5 Hva vi ikke kan avgjøre uten NRKs spesifikasjon eller data

- **Perioden.** Elhubs kommunefil (`data/raw/consumption_per_group_municipality_hour.csv.gz`)
  dekker 01.02.2022–30.04.2026. Rådataene inneholder ikke kommunetall for 2021 eller for mai
  og juni 2026, og panelet kan derfor ikke utvides uten et nytt uttrekk fra Elhub. Prisområde-
  filen dekker januar 2021 – september 2026, men uten kommunefordeling. NRK har dermed om lag
  17 flere måneder enn oss, inkludert en fyringssesong (2021) med ekstreme priser og de to
  månedene rett før artikkelen.
- **Forbruksgruppe.** Elhubs kommunefil har bare gruppen «Privat» (husholdning og hytte samlet).
  Vi kan ikke skille husholdning fra hytte per kommune, og kan derfor ikke etterprøve om NRKs
  «husholdningenes strømforbruk» er husholdning alene.
- **Inntektsvariabelen.** Begrep (etter skatt eller brutto, husholdning eller person), årgang og
  enhet er ikke oppgitt, og avviket på 30–60 prosent kan skyldes hvilken som helst av dem.
- **Kommuneutvalget.** NRK oppgir ikke antall kommuner. Vår kommune-til-prisområde-kobling har
  ingen offisiell kilde (README, forbehold 1), og valget av utvalg flytter
  Norgespris-koeffisienten med opptil 0,0045.
- **Vekting, R²-definisjon og standardfeil.** Vi slutter oss til within-R² fordi det er den
  eneste varianten i riktig størrelsesorden, men NRK oppgir det ikke. Vekting er heller ikke
  oppgitt, og flytter koeffisienten 0,0091.

En forespørsel til NRK om venstresidens form, Norgespris-kodingen, inntektsvariabelen og
antall kommuner ville avgjøre alle punktene over. Utkast til spørsmål ligger i
`notat/SPORSMAL_ELHUB_NRK.md`.
