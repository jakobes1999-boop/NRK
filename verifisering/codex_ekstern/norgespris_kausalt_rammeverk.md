# Rammeverk for å estimere den kausale effekten av Norgespris

## 1. Forskningsspørsmål og estimander

Hovedspørsmålet er om Norgespris endret husholdningenes strømforbruk, sammenlignet med hva de samme husholdningene ville brukt uten ordningen.

Analysen bør skille mellom tre estimander:

1. **ATT for tidlige bestillere:** Gjennomsnittlig effekt på forbruk per målepunkt blant husholdninger som bestilte Norgespris senest 1. oktober 2025.
2. **Samlet energieffekt:** Ekstra eller redusert energibruk blant behandlede husholdninger, målt i GWh/TWh.
3. **Effekt på lastprofilen:** Endring i forbruk i høylasttimer, lavlasttimer og timer med høy spotpris.

En nasjonal postindikator estimerer ingen av disse kausalt. Den fanger alle samtidige endringer etter oktober 2025.

## 2. Hoveddesign: kohortbasert difference-in-differences

Elhubs spesialuttrekk følger tre grupper tilbake til 1. oktober 2023:

- bestilt tidlig: bestilte senest 1. oktober 2025;
- bestilt sent: bestilte mellom 2. oktober 2025 og 30. april 2026;
- ikke bestilt: hadde ikke bestilt innen 30. april 2026.

Dataene inneholder timeforbruk og antall målepunkter for NO1, NO2 og NO5, separat for lavt, middels og høyt estimert årsforbruk. Dermed kan de samme framtidige behandlingskohortene sammenlignes i to år før ordningen.

Primærutvalget bør være **tidlige bestillere mot ikke-bestillere**. Sent bestilte utelates fra hovedmodellen fordi offentlig data ikke viser den eksakte behandlingsdatoen for hver undergruppe.

Definer utfallet som

\[
y_{agct}=\log\left(\frac{KWh_{agct}}{N_{agct}}\right),
\]

der \(a\) er prisområde, \(g\) er forhåndsbestemt årsforbruksgruppe, \(c\) er bestillingskohort og \(t\) er time eller dag.

Event-study-modellen er

\[
y_{agct}=\alpha_{agc}+\lambda_{agt}
+\sum_{k\neq -1}\beta_k
\left(Early_c\times 1[EventMonth_t=k]\right)+\varepsilon_{agct}.
\]

- \(\alpha_{agc}\): faste forskjeller mellom kohortene innen prisområde og forbruksgruppe.
- \(\lambda_{agt}\): prisområde × forbruksgruppe × tidspunkt-faste effekter.
- Referanseperiode: september 2025.
- \(\beta_k\): forskjellen mellom tidlige bestillere og ikke-bestillere relativt til forskjellen før Norgespris.

De mettede tidspunktseffektene absorberer temperatur, spotpris, ukedag, ferie, dagslys og alle andre sjokk som er felles for de to kohortene innen samme prisområde, forbruksgruppe og tidspunkt. Separate værkontroller er derfor ikke nødvendige i hovedmodellen.

Hovedestimatet kan også uttrykkes som én gjennomsnittlig posteffekt:

\[
y_{agct}=\alpha_{agc}+\lambda_{agt}
+\beta(Early_c\times Post_t)+\varepsilon_{agct}.
\]

Den eksakte prosentvise effekten er \(100(e^{\beta}-1)\), ikke \(100\beta\), når utfallet er logaritmisk.

## 3. Identifikasjonsantakelse

Den nødvendige antakelsen er at tidlige bestillere og ikke-bestillere ville hatt parallelle forbrukstrender etter oktober 2025 uten Norgespris, betinget på prisområde og forhåndsbestemt forbruksgruppe.

Antakelsen skal undersøkes med:

- månedlige pre-koeffisienter fra oktober 2023 til august 2025;
- samlet test av at alle pre-koeffisienter er null;
- lineære og fleksible kohortspesifikke pretrender;
- placebointervensjon 1. oktober 2024;
- separat analyse for NO1, NO2 og NO5;
- separat analyse for lavt, middels og høyt årsforbruk;
- leave-one-price-area-out-estimater.

Pretrender kan svekke eller støtte designet, men beviser ikke parallelle kontrafaktiske trender.

## 4. Pris-mekanismen

Norgespris påvirker den marginale strømprisen, ikke bare nivået på strømregningen. For hver time beregnes prisen uten Norgespris som

\[
p^{SS}_{at}=
\begin{cases}
p^{spot}_{at}, & p^{spot}_{at}\leq \tau_t,\\
\tau_t+0.10(p^{spot}_{at}-\tau_t), & p^{spot}_{at}>\tau_t,
\end{cases}
\]

der \(\tau_t\) er den til enhver tid gjeldende terskelen for strømstøtte. Norgespris settes til 0,40 kroner/kWh eksklusive merverdiavgift. Avgifter og nettleie holdes utenfor hvis de er like på tvers av kohortene.

Prisgapet er

\[
Wedge_{at}=p^{SS}_{at}-0.40.
\]

En mekanismemodell er

\[
y_{agct}=\alpha_{agc}+\lambda_{agt}
+\theta(Early_c\times Post_t\times Wedge_{at})
+\delta(Early_c\times Post_t)+\varepsilon_{agct}.
\]

\(\theta\) måler om behandlingsgruppen reagerer mer når forskjellen mellom alternativ marginalpris og Norgespris er stor. Dette er mer informativt enn å kontrollere lineært for samtidig spotpris.

## 5. Fra prosent til GWh

For et log-estimat \(\hat\beta\) beregnes kontrafaktisk forbruk for behandlingsgruppen som

\[
\widehat{Y^0_t}=\frac{Y^1_t}{e^{\hat\beta}},
\]

og energieffekten som

\[
\widehat{\Delta GWh}
=\sum_{t\in post}\left(Y^1_t-\widehat{Y^0_t}\right)/10^6.
\]

Oppskaleringen skal bare gjøres for målepunkter som faktisk er i behandlingskohorten. Koeffisienten skal ikke multipliseres med alt husholdningsforbruk i Sør-Norge.

Rapporter både:

- prosentvis ATT per målepunkt;
- kWh per behandlet målepunkt;
- samlet GWh/TWh;
- effekt i de 10 prosent høyeste lasttimene;
- effekt i timer der prisgapet er positivt, null og negativt.

## 6. Robusthetsdesign med eldre data

### Kommuneintensitet 2021–2026

Koble kommunalt timeforbruk fra Elhub til daglig andel med Norgespris. Bruk forbruk per målepunkt, ikke samlet kommuneforbruk. Estimer en kontinuerlig treatment-intensity-modell med kommuneeffekter og prisområde × tidspunkt-effekter.

Kommunal bestillingsandel er endogen. Den må derfor ikke tolkes kausalt uten instrument eller sterk seleksjonsmodell.

Et mulig instrument er forhåndsberegnet økonomisk gevinst basert utelukkende på:

- kommunens forbruksmønster før ordningen;
- historisk prisområdeeksponering før kunngjøringen;
- forwardpriser som var observerbare før bestillingsvalget.

Instrumentet må valideres mot pretrender og kan fortsatt bryte eksklusjonsrestriksjonen. Det bør være robusthet, ikke hovedresultat.

### Syntetisk kontroll

Bygg en syntetisk kontroll for NO1/NO2/NO5 av NO3, NO4 og sammenlignbare nordiske prisområder. Match 2021–2025 på:

- temperaturkorrigert forbruk per målepunkt;
- oppvarmingsgraddager;
- spot- og sluttbrukerpris;
- boligmasse, varmepumper og elbiler;
- sesong- og kalenderprofil.

Dette gir en makrosjekk av samlet effekt, men er svakere enn kohortdesignet fordi nordlige og utenlandske områder kan ha andre sjokk og oppvarmingsteknologier.

## 7. Datakilder

| Data | Frekvens | Bruk |
|---|---:|---|
| Elhub: forbruk etter Norgespris-status | Time, 2023-10–2026-04 | Hoveddesign og event study |
| Elhub: forbruk per prisområde/kommune | Time, fra 2021 | Lang historikk og kommune-robusthet |
| Elhub: Norgesprisandel per kommune | Dag, fra 2025-10 | Behandlingsintensitet |
| MET/Frost | Time/dag | Temperatur, vind og oppvarmingsgraddager |
| Nord Pool/ENTSO-E | Time | Spotpris og beregnet marginalpris |
| NVE/Regjeringen | Regelendringer | Korrekt strømstøtteterskel og sats per dato |
| SSB | År/kvartal | Boligmasse, befolkning, inntekt og oppvarmingsteknologi |

## 8. Inferens

Det finnes få aggregerte kohortceller. Vanlige heteroskedastisitetsrobuste standardfeil vil derfor være for optimistiske.

Bruk minst tre inferensmetoder:

1. blokk-bootstrap over uker for tidsserieavhengighet;
2. wild-cluster bootstrap på prisområde × årsforbruksgruppe × kohort;
3. placebofordeling fra falske intervensjonsdatoer i preperioden.

Effekten bør bare omtales som robust dersom fortegn og størrelsesorden overlever alle tre.

## 9. Beslutningsregel

En kausal konklusjon krever samtidig:

- flate og små pretrender;
- ingen tilsvarende effekt ved placebointervensjonen i 2024;
- konsistente estimater på tvers av prisområder og forbruksgrupper;
- sterkere respons når den marginale prisreduksjonen faktisk er større;
- resultater som ikke drives av én prisregion eller noen få ekstremdager.

Hvis disse kravene ikke oppfylles, skal resultatet omtales som en betinget sammenheng, ikke som effekten av Norgespris.

