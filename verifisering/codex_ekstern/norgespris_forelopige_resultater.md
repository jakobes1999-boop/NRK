# Foreløpig kausal beregning av Norgespris

## Hovedresultat

Med Elhubs kohortdata estimeres Norgespris å ha økt strømforbruket blant tidlige bestillere med omtrent **2,8 prosent** fra 1. oktober 2025 til 30. april 2026.

Det foretrukne estimatet justerer fleksibelt for:

- prisområde og forhåndsbestemt årsforbruksgruppe;
- permanente forskjeller mellom tidlige bestillere og ikke-bestillere;
- måned og ukedag innen hvert stratum;
- ulik oppvarmings-/kuldefølsomhet, modellert med kontrollkohortens faktiske døgnlast;
- avviket som samme modell produserer i placeboåret 2024/25.

| Spesifikasjon | Effekt | Bootstrapintervall (95 %) |
|---|---:|---:|
| Sesongmatchet DiD | 3,28 % | 2,57–4,13 % |
| Lineær differansetrendjustering | 3,79 % | 2,96–4,74 % |
| Fleksibel last-/kuldejustering | 3,01 % | 2,35–3,94 % |
| Fleksibel justering, placeboår | 0,22 % | −0,13–0,58 % |
| **Foretrukket: fleksibel justering minus placebo** | **2,79 %** | **2,00–3,79 %** |

Intervallene er følsomhetsintervaller fra en toveis bootstrap over ni strata og kalenderukeblokker. Med bare ni aggregerte strata bør de ikke tolkes som eksakte individuelle standardfeil.

## Datagrunnlag

Elhubs spesialuttrekk inneholder aggregert timeforbruk for husholdninger i NO1, NO2 og NO5 fra 1. oktober 2023 til 30. april 2026. Husholdningene er klassifisert etter:

- lavt, middels eller høyt estimert årsforbruk;
- bestilt Norgespris tidlig;
- bestilt Norgespris sent;
- ikke bestilt Norgespris.

Primærutvalget sammenligner tidlige bestillere med ikke-bestillere. Sent bestilte utelates fordi offentlig data ikke viser nøyaktig behandlingsdato. Primærutvalget består av 407 376 timeceller og 493 315 tidlig behandlede målepunkter i de inkluderte forbruksgruppene.

Kilde og variabeldefinisjoner: [Elhub](https://elhub.atlassian.net/wiki/spaces/Data/pages/2816081922/Forbruk%2Bper%2BNorgespris-status%2Bforbruksgruppe%2Bprisomr%2Bde%2Bog%2Bantall%2Bm%2Blepunker%2Bper%2Btime).

## Estimeringsstrategi

La kohortgapet innen prisområde og årsforbruksgruppe være

\[
Gap_{sdt}=\log(kWh^{early}_{sdt}/N^{early}_{sdt})
-\log(kWh^{control}_{sdt}/N^{control}_{sdt}).
\]

Den sesongmatchede DiD-en sammenligner dette gapet etter innføringen med gapet på samme kalenderdato året før:

\[
\widehat\beta_{DiD}=E_w[Gap_{sd,2025/26}-Gap_{sd,2024/25}].
\]

Placeboestimatet anvender identisk beregning ett år tidligere. Den lineært trendjusterte DDD-en er differansen mellom hovedestimatet og placeboestimatet.

I den foretrukne spesifikasjonen predikeres kohortgapet etter oktober 2025 fra en modell estimert utelukkende på førdata. Modellen tillater stratumspesifikke måneds- og ukedagseffekter og en kubisk sammenheng med ikke-bestillernes faktiske døgnlast. Dette fanger at de to kohortene kan reagere ulikt på kulde selv innen samme årsforbruksgruppe. Den samme prosedyren gjennomføres med en falsk intervensjon i oktober 2024, og dette placeboavviket trekkes fra.

## Dynamikk

Den sesongmatchede effekten bygger seg gradvis opp:

| Måned | Endring relativt til samme måned året før |
|---|---:|
| Oktober 2025 | 1,65 % |
| November 2025 | 2,09 % |
| Desember 2025 | 2,88 % |
| Januar 2026 | 4,30 % |
| Februar 2026 | 4,75 % |
| Mars 2026 | 3,76 % |
| April 2026 | 3,85 % |

Før innføringen ligger de tilsvarende års-differansene stort sett nær null. Alle ni prisområde–forbruksgruppe-strata har positiv trendjustert effekt, fra omtrent 2,5 til 5,4 prosent.

Se `norgespris_event_study.png` og `norgespris_monthly_event_study.csv`.

## Volumvirkning

De tidlige bestillerne i utvalget brukte 6 200 GWh fra oktober 2025 til april 2026. Med foretrukket koeffisient beregnes kontrafaktisk forbruk som

\[
\widehat{Y^0}=\frac{Y^1}{e^{\hat\beta}}.
\]

Dette gir:

- estimert merforbruk: **168 GWh**;
- bootstrapintervall: omtrent **122–226 GWh**;
- merforbruk per behandlet målepunkt: **341 kWh**;
- intervall per målepunkt: omtrent **247–459 kWh**.

Dette er effekten i den observerte utvalgspopulasjonen. Den er ikke oppskalert til alle Norgespriskunder, fritidsboliger, forbruk under 1 000 kWh eller over 50 000 kWh.

## Tolkning og begrensninger

Resultatet er vesentlig nærmere en kausal effekt enn en nasjonal før–etter-regresjon fordi samme framtidige bestillingskohorter observeres i to år før behandlingen og sammenlignes innen samme prisområde, forbruksgruppe og dato.

Det gjenstår likevel seleksjonsrisiko:

1. Tidlige bestillere kan ha endret andre forbruksrelevante forhold samtidig med Norgespris.
2. Aggregerte data tillater ikke husholdningsfaste effekter eller eksakt klynging på kunde.
3. «Ikke bestilt» er definert ved utgangen av april 2026 og kan inneholde senere bestillere.
4. Den fleksible lastjusteringen bruker kontrollgruppens last som vær-/oppvarmingsproxy; direkte temperaturdata bør inngå i neste versjon.
5. Effekten bør kobles til det timevise marginalprisgapet for å teste prisresponsmekanismen direkte.

Den foreløpige konklusjonen er derfor:

> Offentlige Elhub-data gir konsistent evidens for at Norgespris økte strømforbruket blant tidlige bestillere med rundt 3 prosent vinteren 2025/26. Et forsiktig hovedanslag er 2,8 prosent, tilsvarende rundt 168 GWh i den analyserte behandlingspopulasjonen. Resultatet er robust på tvers av spesifikasjoner og strata, men bør fortsatt betegnes som et kvasi-eksperimentelt estimat, ikke et fullstendig randomisert kausalestimat.

