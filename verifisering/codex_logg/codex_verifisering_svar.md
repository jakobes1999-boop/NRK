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

## HVA SOM ER GJORT

- Lest alle påkrevde grunnlagsdokumenter, fire kritikkrunder, NRKs metodeboks, debattinnlegget og relevant modell-/bootstrapkode.
- Gjennomført statisk algebra-, rang-, inferens- og formuleringrevisjon.
- Avstemt prosjektets CSV-resultater mot `TIL_GODKJENNING.md`. Dette er intern konsistenskontroll, ikke uavhengig reproduksjon.

## FILER SKREVET (fullstendige stier)

Ingen filer ble skrevet. Oppretting av følgende mappe ble avvist av skrivebeskyttet sandkasse:

`C:\Users\JAKOBE~1\AppData\Local\Temp\claude\C--Users-JakobEiksundS-thre\02b6430c-fd42-4a2d-9c9e-d489beb9a238\scratchpad\codex_verifisering\verifisering\`

Dermed ble verken `RAPPORT_codex.md` eller kontrollskriptene opprettet.

## KONTROLLER KJØRT (med faktiske tall)

- Filstørrelser: `did_month.parquet` 34 743 byte; `panel.parquet` 687 819 byte; `elhub_np_mba_daily.parquet` 38 225 byte.
- Dimensjonsavstemming fra dokumenterte data: 27 × 31 = 837 rader; førperiode 27 × 24 = 648; kommunepanel 197 × 51 = 10 047.
- Kohortkontroll: 493 315 tidlige + 367 106 sene + 402 414 ikke-bestillere = 1 262 835 målere.
- Prosjektets eksakte CSV-tall avrunder uten avvik til `TIL_GODKJENNING.md`:

| Modell | Koeffisient | SE | Avvik ved rapportert presisjon |
|---|---:|---:|---:|
| D7 | 0,02988049 | 0,00283965 | 0 |
| D7 placebo | −0,00189929 | 0,00124434 | 0 |
| D7 tidlig | 0,03094415 | 0,00298661 | 0 |
| D7 sent | 0,02861018 | 0,00320150 | 0 |
| M1 | 0,09503148 | 0,00691951 | 0 |
| M5 | 0,05090808 | 0,00232333 | 0 |

## IKKE GJORT + HVORFOR

- Ingen modell ble reestimert fra parquet.
- Uvektet D7, event-study, permutasjon og leave-one-cluster-out ble ikke kjørt.
- SHA-256-kontrollsummer kunne ikke beregnes.
- Kontrollskript og sluttrapport kunne ikke skrives.

Årsaken er at både `py -3`, `Get-FileHash` og all filskriving ble avvist av øktens tillatelsesprofil. Ingen nettverkskall eller Office-automatisering ble forsøkt.

## USIKKERHET

Tallene ovenfor er avlest og kryssavstemt fra prosjektets egne artefakter, ikke uavhengig reprodusert. En reell sluttverifisering krever en ny økt med skrivetilgang til arbeidsmappen og tillatelse til å kjøre `py -3`.