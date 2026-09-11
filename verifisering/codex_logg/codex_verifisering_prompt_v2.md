Du er en grundig, utførende arbeidsagent. Gjør oppgaven under komplett og etterprøvbart.
Ufravikelige regler:

- Arbeid KUN i arbeidsmappen. Ikke slett eller omorganiser eksisterende filer; nye filer skrives ved siden av, ikke oppå. Skriv egne kontrollskript til undermappen `verifisering/`.
- Ingen nettverkskall. Bruk aldri COM-automatisering mot Office-programmer og drep aldri Office-prosesser.
- Python på denne maskinen heter `py -3` (ikke `python`). pandas, numpy, statsmodels, linearmodels og pyarrow er installert. Finnes ikke et bibliotek: løs det med det som finnes og si det – ikke installer pakker.
- Kjør IKKE nedlastingsskriptene s01–s05 (nettverk). Data ligger ferdig i data/processed/.
- Norsk tallformat i tekst (desimalkomma); celleverdier i datafiler er rene tall.
- Vis regnestykkene: dokumenter input, metode og kontrollsum; avviksrapport for alt du reproduserer («0 avvik» eller tallfestet differanse). Ikke dikt: mangler noe, skriv [fylles inn].
- Avslutt svaret med seksjonene: HVA SOM ER GJORT / FILER SKREVET (fullstendige stier) / KONTROLLER KJØRT (med faktiske tall) / IKKE GJORT + HVORFOR / USIKKERHET.
- Svar på norsk.

## OPPGAVE

Dette er en uavhengig sluttverifisering av en økonometrisk etterprøving. Bakgrunn: NRK publiserte 27.08.2026 artikkelen «Prisen for billig strøm» (kilder/nrk_prisen_for_billig_strom.md, metodeboksen står linje 251–285) med påstanden at Norgespris (fastpris 50 øre/kWh inkl. mva fra 1. oktober 2025) økte husholdningenes strømforbruk i NO1/NO2/NO5 med over 8 prosent, basert på en kommune-FE-regresjon. Prosjektet i denne mappen etterprøver dette. Les først README.md, notat/FAGLIG_VURDERING_2026-09-05.md, notat/GJENNOMGANG_pedagogisk_2026-09-05.md og output/TIL_GODKJENNING.md. Kritikkrundene ligger i notat/KRITIKK*_2026-09-05.md.

Hovedmodellen (D7) i src/s12_kritikk2_beregninger.py linje 49:
  log_y ~ C(g) + C(pa_t_eac) + bestilt:C(mnd):C(eac) + bestilt_post
WLS med vekt n_mp, kluster på g (27 klustre), data data/processed/did_month.parquet (okt 2023–apr 2026, 837 rader). Påstått resultat: bestilt_post 0,0299 (3,0 prosent), placebo (innføring okt 2024, data før okt 2025) −0,0019. Wild cluster bootstrap i src/s14_wild_bootstrap.py gir KI 2,4–3,7 prosent. NRK-lik modell M1 i src/s07_estimate_fe.py gir post_np 0,0950, placebo M5 0,0509.

Gjør følgende, i denne rekkefølgen:

1. **Reproduksjon.** Reproduser D7, D7 placebo, D7 tidlig/sent, M1 og M5 med egen kode (ikke ved å kjøre prosjektets skript), fra parquet-filene. Rapporter koeffisient, SE og avvik mot tallene i output/TIL_GODKJENNING.md.

2. **Identifikasjon i D7.** Vurder om spesifikasjonen faktisk gjør det notatet påstår: (a) at C(pa_t_eac) fjerner alt som er felles for bestillere og ikke-bestillere innen område × måned × forbruksklasse; (b) at bestilt:C(mnd):C(eac) er identifisert av førperioden og at bestilt_post er snittet over de sju postmånedene av avviket fra eget førgjennomsnitt (vis det algebraisk eller numerisk, f.eks. ved å regne effekten manuelt som gjennomsnitt av differanser); (c) om det er kollinearitet eller for få frihetsgrader i førperioden (36 profilparametre, 27 grupper × 24 førmåneder); (d) om vektingen med n_mp er forsvarlig, og hva uvektet gir.

3. **Trusler mot identifikasjon.** Vurder konkret: seleksjon inn i bestilling som korrelerer med forbruksendring 2025/26 (f.eks. bestillere kjøpte elbil/varmepumpe samme vinter); at kontrollgruppen (ikke bestilt) møter strømstøtte med 90 prosent dekning over 75–77 øre, slik at kontrasten er fastpris mot strømstøtte, ikke mot spot; SUTVA; at sent-kohorten er delvis behandlet gjennom vinteren (se dose i src/s13_dose_sent.py). Si for hver trussel om den gjør 3,0 prosent til et for høyt eller for lavt anslag på effekten, og hvor mye den kan bety.

4. **Placeboens beviskraft.** Placeboen estimerer sesongprofilen på ett år og tester på det neste. Vurder om −0,19 prosent (p 0,13) er en sterk eller svak test, og om du kan konstruere en alternativ placebo eller pre-trend-test som er strengere (f.eks. event-study på førperioden, permutasjon av behandlingsstatus over de 27 gruppene, leave-one-cluster-out). Kjør minst én.

5. **Inferens.** Kontroller wild cluster bootstrap-implementasjonen i src/wcb.py: Rademacher-vekter, CR1, p = (1 + #)/(B + 1), testinversjon for KI. Er det korrekt implementert, og er 27 klustre nok for at WCR er pålitelig? Kommenter at ni-kluster-modellene (E6 per EAC) er upålitelige.

6. **NRK-modellen.** Vurder påstanden i notatet om at NRKs modell mest sannsynlig har en felles 0/1-variabel uten tidsfaste effekter, og at en slik modell ikke har kontrollgruppe. Er kritikken riktig hvis NRK i stedet brukte oppslutningsandel per kommune? Er placeboen på M1 (M5, 5,2 prosent) et gyldig argument mot NRKs modelltype?

7. **Samlet dom.** Er analysen faglig forsvarlig som grunnlag for et debattinnlegg (notat/DEBATTINNLEGG_utkast_v2_2026-09-05.md) som sier: NRKs modelltype mangler kontrollgruppe og finner 5 prosent i et placeboår; DiD på bestillingsstatus gir om lag 3 prosent for bestillere (KI 2,4–3,7), 2–3 prosent aggregert, placebo mellom −1 og +1? List hver formulering i innlegget som ikke er dekket av tallene, og hver feil du finner, rangert etter alvor.

## LEVERANSE

- `verifisering/RAPPORT_codex.md`: seksjonene 1–7 over, med tall, avviksrapport og rangert liste av feil/svakheter (kritisk / vesentlig / mindre).
- `verifisering/*.py`: koden du brukte, kjørbar med `py -3`.
- Endre ingen eksisterende filer.


## VEDLEGG: statisk revisjon fra en tidligere økt uten kjøretilgang

En tidligere økt uten skrive- og kjøretilgang leverte funnene under. Bruk dem som hypoteser: bekreft eller avkreft hvert punkt numerisk der det lar seg gjøre (rang/kollinearitet i D7, FWL-tolkningen av bestilt_post, uvektet D7, E5-placebo, WCB-intervall i prosent, dosesnitt for sent). Ikke gjenta dem ukritisk.

Oppgaven kan ikke fullføres etterprøvbart i denne økten: arbeidsmappen er skrivebeskyttet, og sandkassen avviser også `py -3`. Jeg har derfor ikke fremstilt en uavhengig reproduksjon som om den var kjørt.

Den statiske revisjonen avdekker likevel flere vesentlige forhold:

- `C(pa_t_eac)` absorberer vilkårlige felles sjokk innen prisområde × årsmåned × forbruksklasse, men ikke statusspesifikt vær, geografi, sammensetning eller prisrespons. Påstanden om at gruppene møtte «samme vær» er ikke dokumentert.
- D7 har 342 Patsy-kolonner, men rang 331: åtte redundanser mellom gruppe- og tids-FE og tre mellom sesongprofiler og gruppe-FE. `bestilt_post` er identifisert; bare 33 av de 36 profilkontrastene er uavhengige. Residualfrihetsgrad er 506.
- Sesongprofilen estimeres på hele utvalget, ikke bare førperioden. Tolkningen som et enkelt gjennomsnitt av sju avvik fra førgjennomsnittet er eksakt bare i en balansert, uvektet spesialmodell. Med `n_mp`-vekter er estimatet en implisitt FWL-vektet kontrast.
- Placeboen er presis, men smal i beviskraft: WCB-intervallet tilsvarer omtrent −0,42 til +0,10 prosent. Den tester bare ett historisk årsskifte. Den mer sammenlignbare sju-måneders E5-placeboen gir −0,66 prosent for tidliggruppen, p = 0,001.
- Wild-bootstrap-kjernen er i hovedsak korrekt: restringerte residualer, Rademacher/Webb, CR1 og `(1 + #)/(B + 1)`. Testinversjonen er derimot en omtrentlig 41-punkts prosedyre; felles trekninger garanterer ikke at p-kurven er monoton. Med B = 999 er oppløsningen 1/1 000, ikke 1/999.
- 27 klustre gjør WCR informativ, men ikke automatisk pålitelig. Uavhengighet mellom statusgrupper og valget av `g` som klusterenhet er utestet. Ni-klustermodellene er klart upålitelige; Rademacher-resultatene burde minst bruke eksakt enumerering av de 512 fortegnsmønstrene.
- Hvis NRK brukte kommunevis oppslutningsandel, er påstanden «ingen kontrollgruppe» feil, og M5-placeboen tester feil modelltype. Prosjektets relevante andel-placebo F4 er −0,11 prosent ved gjennomsnittsoppslutning, p = 0,91. NRKs spesifikasjon må innhentes før hovedkritikken kan fremsettes som faktum.
- Selvseleksjon kan trekke 3-prosentanslaget opp og kan i prinsippet forklare hele estimatet. Historiske placeboer avgrenser ikke et særskilt elbil-, varmepumpe- eller flyttesjokk i 2025/26.
- Strømstøtte er ikke identifikasjonsbias dersom ønsket estimand er Norgespris mot faktisk alternativ. Mot full spotpris vil effekten normalt være større, men størrelsen er ikke identifisert.
- Ved SUTVA-brudd gjelder omtrent `aggregert effekt = 0,77 × estimert kontrast + effekt på kontrollgruppen`. Ett prosentpoeng effekt på kontrollgruppen endrer derfor aggregatet med omtrent ett prosentpoeng.
- Sentgruppen hadde en enkel gjennomsnittsdose på om lag 0,71. Under homogen, lineær effekt tilsvarer 2,90 prosent omtrent 4,1 prosent ved full behandling og løfter samlet bestillereffekt fra 3,03 til rundt 3,5 prosent. Dette er bare en mekanisk illustrasjon; prosjektets dosemodeller spenner fra 1,6 til 4,6 prosent.
- Debattinnlegget har flere udekkede formuleringer: «samme vær», «derfor i underkant», placebo mellom −1 og +1, F2-intervall null–16 i stedet for omtrent −3–16, «husholdningenes» 15 prosent når serien inkluderer hytter, ekstrapolering fra april til juni, «resten er vær», og den kausale konklusjonen om at billig strøm beviselig økte forbruket.
- WCB-grensene 0,02423–0,03660 er i loggpoeng. Transformert med `exp(x)−1` blir intervallet 2,45–3,73 prosent, altså 2,5–3,7 med én desimal, ikke 2,4–3,7.

