# Uavhengig sluttverifisering av modellen, 06.09.2026

*Tallgrunnlaget er regnet av OpenAI Codex (gpt-5.6-sol, effort max) med egen kode i `verifisering/` (01–05, `felles.py`), uten import fra prosjektets `src/`. Codex' kvote gikk tom før rapporten ble skrevet; skript 04 stoppet på en skrivefeil som Codex rettet, og ble kjørt ferdig lokalt (`verifisering/log_04.txt`). Syntesen under er skrevet av Claude på grunnlag av resultatfilene. Alle tall er til godkjenning. Codex' første, statiske gjennomlesning uten kjøretilgang ligger i `verifisering/codex_logg/codex_verifisering_svar.md`.*

## 1. Reproduksjon

Alle seks modeller reprodusert fra parquet med uavhengig kode (`resultater_reproduksjon.csv`). Største avvik mot TIL_GODKJENNING.md er 3,1 × 10⁻⁵ på koeffisient og 2,3 × 10⁻⁵ på standardfeil, altså avrunding.

| Modell | Koef. | SE | Prosent | N | Klustre |
|---|---|---|---|---|---|
| D7 bestilt_post | 0,02988 | 0,00284 | 3,03 | 837 | 27 |
| D7 tidlig_post | 0,03094 | 0,00299 | 3,14 | 837 | 27 |
| D7 sent_post | 0,02861 | 0,00320 | 2,90 | 837 | 27 |
| D7 placebo | −0,00190 | 0,00124 | −0,19 | 648 | 27 |
| M1 post_np | 0,09503 | 0,00692 | 9,97 | 10 047 | 197 |
| M5 post_np | 0,05091 | 0,00232 | 5,22 | 8 668 | 197 |

Kontrollsummer for inndata i `kontrollsummer_reproduksjon.json` (27 grupper × 31 måneder = 837; 197 kommuner × 51 måneder = 10 047).

## 2. Identifikasjon i D7

- **Rang.** Designmatrisen har 342 kolonner og rang 331 (`rang_d7.csv`). Åtte redundanser er mellom gruppe- og område×måned×klasse-effektene, tre mellom sesongprofilen og gruppeeffektene. `bestilt_post` er identifisert. 33 av 36 profilkontraster er uavhengige. Residualfrihetsgrader 506. Ingen praktisk betydning for hovedkoeffisienten; notatets «36 parametre» bør presiseres til 33 uavhengige.
- **Tolkningen «snitt av sju avvik fra eget førgjennomsnitt».** Bekreftet eksakt for den *uvektede* modellen: enkelt snitt av de 7 × 18 månedskontrastene er 0,029651, identisk med uvektet D7 (avvik 10⁻¹⁴). Med målervekter er koeffisienten 0,029880, altså 0,0002 logpoeng høyere. Forskjellen er uten betydning, men den pedagogiske forklaringen er strengt tatt den uvektede.
- **FWL-dekomponering** (`fwl_manedsbidrag.csv`): postmånedene bærer to tredeler av informasjonen om `bestilt_post`, førperioden en tredel. Profilen er dermed ikke *utelukkende* førperiodebestemt; postobservasjonene påvirker den også, men bare gjennom den felles `bestilt_post`.
- **Vekting og klustring** (`vekting_og_klustring.csv`):

| Variant | Koef. | SE | t-KI, prosent |
|---|---|---|---|
| WLS, kluster g (27) | 0,02988 | 0,00284 | 2,4–3,6 |
| OLS uvektet, kluster g | 0,02965 | 0,00296 | 2,4–3,6 |
| WLS, kluster område×klasse (9) | 0,02988 | 0,00391 | 2,1–4,0 |
| WLS, kluster område (3) | 0,02988 | 0,00417 | 1,2–4,9 (p 0,019) |

Målervektene spenner fra 7 322 til 128 708 målere per gruppe (forhold 17,6). Vektet og uvektet gir samme svar.

## 3. Trusler mot identifikasjon (sensitiviteter)

- **Seleksjon** (`seleksjon_sensitivitet.csv`): et seleksjonssjokk som løfter bestillernes forbruk med 1 prosentpoeng relativt til ikke-bestillere vinteren 2025/26, uavhengig av fastprisen, reduserer effekten til 2,0 prosent; 2 pp gir 1,0; 3,0 pp fjerner hele effekten. Historiske placeboer avgrenser ikke et sjokk som bare traff 2025/26. Retning: gjør 3,0 til et for høyt tall.
- **Strømstøtte som kontrast** (`dose_sensitivitet.json`): prisgapet fastpris mot faktisk møtt pris (spot med støtte) er 0,62 logpoeng målerveid; mot ren spot 0,90. Mekanisk elastisitet −0,048. Skalert til spot ville effekten vært om lag 4,4 prosent. Ikke identifisert, bare mekanikk. Retning: 3,0 er et for lavt tall for «mot markedspris», men riktig estimand for «mot faktisk alternativ».
- **SUTVA** (`sutva_sensitivitet.csv`): aggregert effekt ≈ 0,77 × kontrast + effekt på kontrollgruppen. Ett prosentpoeng effekt på ikke-bestillerne (f.eks. via høyere spotpris når bestillerne bruker mer) flytter aggregatet med om lag ett prosentpoeng: 1,3 til 3,3 for ±1 pp.
- **Delvis behandlet sent-kohort**: målerveid gjennomsnittsdose for sent i postperioden er 0,71. Under homogen lineær effekt tilsvarer sent 2,90 om lag 4,1 prosent ved full dose, bestillere samlet 3,5, aggregert 2,7 (mot 2,3). Retning: 3,0 er i underkant for full behandling. Illustrasjon; prosjektets dosemodeller spenner 1,6–4,6.

## 4. Placeboens beviskraft

- **D7-placebo** −0,19 prosent, WCB-KI −0,42 til +0,11. Presis, men tester ett årsskifte.
- **Event-study på førperioden** (`pre_event_study.csv`): de tolv månedene okt. 2024–sep. 2025 mot året før gir avvik fra −1,14 (okt. 2024) til +0,43 prosent (sep. 2025); 5 av 12 er signifikante på 5 prosent, felles F-test forkaster «alle null» (F(12, 26) = 62). Snittet er −0,19. Tolkning: forskjellen bestillere/ikke-bestillere er ikke stabil måned for måned, men svinger ±1 prosentpoeng rundt null. Effekten på 3,0 er tre ganger største førperiodeavvik. Innleggets «mellom minus én og pluss én prosent» er dekkende for dette.
- **E5-placebo med dose** (`e5_placebo.csv`): i placeboåret får sent-kohorten et signifikant «dose»-mønster (+1,46 prosent, p < 0,001) med felles sesongprofil, som forsvinner med kohortspesifikk profil (0,34, p 0,19). Bekrefter at doseresponsen er konfundert med sent-kohortens egen sesongprofil, som notatet allerede sier.
- **Leave-one-cluster-out** (`loco_d7.csv`): D7 varierer 0,0277–0,0316 når én av 27 grupper utelates; placeboen −0,0030 til −0,0013, 2 av 27 varianter p < 0,05. Ingen enkeltgruppe driver resultatet.
- Ikke kjørt: permutasjon av behandlingsstatus over gruppene (kvoten gikk tom).

## 5. Inferens: wild cluster bootstrap

Uavhengig implementasjon (`04_wcb_revisjon.py`, `wcb_revisjon.json`) reproduserer prosjektets tall: B = 999, seed 1, restringerte residualer, Rademacher, CR1, p = (1 + #)/(B + 1). Grov 41-punkts testinversjon gir samme grenser som prosjektet (avvik 0). Fin inversjon (steg 7 × 10⁻⁶) gir 0,02423–0,03647 logpoeng. p-kurven er monoton på begge sider for D7 (0 brudd), 2 brudd venstre for placebo.

**Rettelse:** grensene er logpoeng. I prosent er intervallet **2,5–3,7** (2,45–3,71), ikke 2,4–3,7. 2,4 stammer fra t-intervallet (2,43–3,64). Oppløsningen med B = 999 er 1/1 000.

Ni klustre (område×klasse) med eksakt enumerering av alle 512 fortegnsmønstre: D7 p 0,0039, KI 2,3–3,8 prosent. E6-modellenes Monte Carlo-p avviker høyst 0,002 fra eksakt p (`wcb_ni_klustre_eksakt.csv`); Lav sent_dose eksakt p 0,082. Ni-klustermodellene er upålitelige som mål på signifikans, men de eksakte p-verdiene bekrefter prosjektets konklusjoner om hva som holder og ikke.

## 6. NRK-modellen (vurdering, ikke beregning)

Codex' statiske vurdering: hvis NRK brukte kommunevis oppslutningsandel, er «ingen kontrollgruppe» feil, og M5-placeboen (0/1-variabel) tester feil modelltype. Prosjektets egen andelsplacebo F4 gir −0,11 prosent (p 0,91), altså ingen falsk effekt for andelsdesignet. Indisiene for 0/1-koding (R² 94 prosent uten tidsfaste effekter, koeffisienten lest som «over 8 prosent» for alle, gradtall 0,0019 identisk) står, men er indisier. Konklusjon: den betingede formuleringen i innlegget er nødvendig, og NRKs spesifikasjon bør innhentes før hovedkritikken fremsettes som faktum.

## 7. Samlet dom og rangert liste

Analysen er faglig forsvarlig som grunnlag for innlegget, med rettelsene under. Hovedtallet 3,0 prosent reproduseres eksakt, er robust for vekting, klusternivå og utelatte grupper, og placeboen holder i tre varianter. Den svakeste antagelsen er at ingen bestillerspesifikk endring traff vinteren 2025/26; 3 prosentpoeng slik endring ville fjerne effekten, og det kan ikke testes med historiske placeboer.

**Kritisk (må rettes i innlegget):**
1. «2,4 til 3,7 prosent» → 2,5 til 3,7 (logpoeng feil omregnet).
2. «Husholdningenes forbruk … 15 prosent» → serien inkluderer hytter (14,7 prosent); husholdninger alene 14,3. Skriv «husholdninger og hytter» eller «om lag 14 prosent».
3. «alt fra null til seksten» for F2 → intervallet er om lag minus tre til seksten.

**Vesentlig:**
4. «husholdninger som møtte samme vær» → område×måned-effekten fjerner felles vær innen område, men bestillere og ikke-bestillere kan ha ulik geografisk fordeling innen området. Skriv «i samme prisområde og samme måned».
5. «og er derfor i underkant» → gjelder bare for estimanden «mot markedspris»; mot faktisk alternativ er 3,0 riktig tall. Skriv «målt mot strømstøtte, ikke mot full markedspris».
6. DiD dekker okt. 2025–apr. 2026; forbruksøkningen på 15 prosent er jan.–jun. Andelen «en femdel» blander perioder. Si «første kvartal» eller «vinteren».
7. Notatets «36 profilparametre» → 33 uavhengige. Pedagogisk forklaring av `bestilt_post` som snitt er eksakt kun uvektet.

**Mindre:**
8. Innlegget bør ikke antyde at NRKs konklusjon er *bevist* riktig; effekten er identifisert for bestillere under parallelle trender, ikke for «billig strøm» generelt.
9. Permutasjonstest ikke kjørt; LOCO og event-study dekker det meste av samme spørsmål.
