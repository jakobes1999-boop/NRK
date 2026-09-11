# Strømstøtte og Norgespris – parametre og kilder

Verifisert 05.09.2026 mot regjeringen.no, lovdata.no og hvakosterstrommen.no. Kildedekningen varierer per rad:
2021–2023 har primærkilde (regjeringen.no); 2024 har bransjeside pluss lovhenvisning; 2025 og 2026 har én
sekundærkilde (hvakosterstrommen.no); april–mai 2023 er ikke bekreftet i forskriftstekst (se merknad). Alle terskler og priser er eks. mva.

## Strømstønad (strømstøtte) for husholdninger

| periode          | terskel (øre/kWh eks. mva) | dekningsgrad | basis   | tak            | kilde-URL |
|------------------|------------------------------|--------------|---------|----------------|-----------|
| 2021-12          | 70                            | 55 %         | måned   | 5000 kWh/mnd/målepunkt | https://www.regjeringen.no/no/aktuelt/endret-stonadsordning-for-husholdninger-som-folge-av-ekstraordinare-stromutgifter/id2893331/ |
| 2022-01–2022-08  | 70                            | 80 %         | måned   | 5000 kWh/mnd   | https://www.regjeringen.no/no/tema/energi/strom/regjeringens-stromtiltak/id2900232/ |
| 2022-09–2023-03  | 70                            | 90 %         | måned   | 5000 kWh/mnd   | https://www.regjeringen.no/no/tema/energi/strom/regjeringens-stromtiltak/id2900232/ |
| 2023-04–2023-05  | 70                            | 80 %         | måned   | 5000 kWh/mnd   | regjeringen.no id2963350 (omtaler endringen, ikke bekreftet i forskriftstekst); sekundærkilder smartenergi.com, energiaktuelt.no – lavere sikkerhet |
| 2023-06–2023-08  | 70                            | 90 %         | måned   | 5000 kWh/mnd   | https://www.regjeringen.no/no/aktuelt/regjeringen-gjor-endringer-i-stromstotteordningen/id2963350/ |
| 2023-09–2023-12  | 70                            | 90 %         | **time**| 5000 kWh/mnd   | https://www.regjeringen.no/no/tema/energi/strom/regjeringens-stromtiltak/id2900232/ |
| 2024-01–2024-12  | 73                            | 90 %         | time    | 5000 kWh/mnd   | https://www.griug.no/nyhetsarkiv/justering-av-terskelverdi-i-stroemstoetteloven-fra-01012024/ ; lov: https://lovdata.no/dokument/NLO/lov/2021-12-22-170 |
| 2025-01–2025-09  | 75                            | 90 %         | time    | 5000 kWh/mnd   | https://www.hvakosterstrommen.no/artikler/slik-fungerer-stromstotten (én sekundærkilde; forskrift [fylles inn]) |
| 2025-10–2025-12  | 75                            | 90 %         | time    | 5000 kWh/mnd (gjelder husholdninger UTEN Norgespris) | https://www.hvakosterstrommen.no/artikler/slik-fungerer-stromstotten (én sekundærkilde; forskrift [fylles inn]) |
| 2026-01–         | 77                            | 90 %         | time    | 5000 kWh/mnd   | https://www.hvakosterstrommen.no/artikler/slik-fungerer-stromstotten (én sekundærkilde; forskrift [fylles inn]) |

Rettslig grunnlag: midlertidig lov om stønad til husholdninger som følge av ekstraordinære
strømutgifter (strømstønadsloven), https://lovdata.no/dokument/NLO/lov/2021-12-22-170.

**Merknad om avvik fra bestillingens forenklede skjema:** Bestillingen la til grunn en flat
terskel på 70 øre for hele timebasis-perioden (fra sep. 2023) og ingen reduksjon i april–mai 2023.
Verifiseringen viser to presiseringer:
1. Terskelen ble prisjustert årlig fra 2024: 73 øre (2024), 75 øre (2025), 77 øre (2026) – ikke
   fast 70 øre. Dette er tatt inn i `src/s15_effektiv_pris.py`.
2. I april–mai 2023 ble dekningsgraden midlertidig satt ned til 80 prosent (fra 90 prosent i
   perioden okt. 2022–mars 2023, tilbake til 90 prosent fra juni 2023). Kilde: regjeringen.no
   (id2963350) sammenholdt med bransjeartikler (smartenergi.com, energiaktuelt.no – sekundærkilder,
   ikke sitert direkte over). Effekten på panelet er liten (to måneder, moderat spotpris), men tatt
   inn for fullstendighet.

Måned/time-skillet (2023-09) og satsen 90 prosent er krysssjekket mellom regjeringen.no og
hvakosterstrommen.no og er robuste. April–mai 2023-presiseringen er svakere sporbar (ingen direkte
lovdata-forskriftstekst funnet for akkurat denne perioden i dette søket) – flagges som lavere
sikkerhet enn resten av tabellen.

## Norgespris (fra 1. oktober 2025)

| parameter | verdi | kilde-URL |
|---|---|---|
| Fastpris, inkl. mva | 50 øre/kWh | https://elhub.no/artikler/vilkar-norgespris |
| Fastpris, eks. mva (sørlige prisområder, 25 % mva) | 40 øre/kWh | https://elhub.no/artikler/vilkar-norgespris |
| Fastpris, Nordland/Troms/Finnmark (fritatt mva) | 40 øre/kWh | https://elhub.no/artikler/vilkar-norgespris |
| Forbrukstak husholdning | 5000 kWh/måned/målepunkt | https://elhub.no/artikler/vilkar-norgespris |
| Forbrukstak fritidsbolig | 1000 kWh/måned | https://elhub.no/artikler/vilkar-norgespris |
| Samtidig strømstøtte og Norgespris på samme målepunkt | Nei – «Du kan ikke få Norgespris og strømstøtte samtidig på samme målepunkt» | https://elhub.no/artikler/vilkar-norgespris |
| Ikrafttredelse | 1. oktober 2025 | https://elhub.no/artikler/vilkar-norgespris |
| Rettslig grunnlag | Lov om Norgespris og strømstønad til husholdninger, 20.06.2025 | https://lovdata.no/dokument/NL/lov/2025-06-20-44 |
| Forskrift (bl.a. terskeljustering strømstønad) | Forskrift om Norgespris, 08.09.2025 | https://lovdata.no/dokument/SF/forskrift/2025-09-08-1790 |

Analysen bruker 40 øre/kWh eks. mva for prisområdene NO1/NO2/NO5 (alle sør for Nord-Norge, 25 %
mva-sats), i tråd med bestillingens spesifikasjon.
