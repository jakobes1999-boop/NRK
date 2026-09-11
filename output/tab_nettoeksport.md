# Etterprøving av NRKs påstand P4 – nettoeksport av strøm

## 1. NRKs ordrette påstand

Kilde: `kilder/nrk_prisen_for_billig_strom.md`, avsnittet «Tjener stort».

> «Nettoeksporten, altså hvor mye mer strøm vi selger til utlandet sammenlignet med hva vi kjøper tilbake, har stupt.»

> «Årets nettoeksport tilsvarer det økte forbruket blant husholdningene i Sør-Norge.»

> Figurens periodeangivelse (kilde: Statnett): «Perioden 1.1. til 31.7».

NRKs graf gjelder perioden 1.1.-31.7. per år (ikke jan-jun). Denne rapporten bruker jan-jun for å kunne sammenligne direkte med prosjektets eget forbrukstall (`tab_p1_forbruk_jan_jun.csv`), som også er jan-jun. Tallene under er derfor ikke identiske med avlesning fra NRKs 1.1.-31.7.-graf.


## 2. Nettoeksport og bruttoforbruk, jan-jun per år (GWh)

Kilde: SSB tabell 14091 «Elektrisitetsbalanse (MWh)» (videreføring av avsluttede 12824), månedlig, hele Norge. Nettoeksport = eksport minus import.

| År | Produksjon | Nettoeksport | Bruttoforbruk | Husholdningsforbruk |
|---|---|---|---|---|
| 2021 | 81 587 | 7 473 | 74 114 | 24 457 |
| 2022 | 76 048 | 6 723 | 69 325 | 20 707 |
| 2023 | 76 680 | 7 776 | 68 904 | 20 951 |
| 2024 | 79 908 | 7 653 | 72 255 | 22 519 |
| 2025 | 83 716 | 11 931 | 71 785 | 21 995 |
| 2026 | 77 337 | 1 763 | 75 574 | 24 370 |

(Alle tall i GWh, sum januar-juni. Full månedstabell: `tab_nettoeksport.csv`.)


## 3. Endring jan-jun 2026 mot jan-jun 2025 (hele Norge, SSB)

- Nettoeksport: 11 931 → 1 763 GWh (-10168 GWh, -85.2 prosent)
- Produksjon: 83 716 → 77 337 GWh (-6379 GWh, -7.6 prosent)
- Bruttoforbruk: 71 785 → 75 574 GWh (+3789 GWh, +5.3 prosent)
- Til sammenligning, prosjektets eget tall (Elhub, husholdning+hytter, NO1+NO2+NO5, jan-jun): endring 2026 mot 2025 = +2323 GWh.

## 4. Vurdering (tall og logikk)

Nettoeksporten falt 10168 GWh fra jan-jun 2025 til jan-jun 2026 (hele Norge, SSB), en nedgang på 85.2 prosent.

Bruttoforbruket i hele Norge (SSB) endret seg +3789 GWh i samme periode (+5.3 prosent).

Elhub-tallet for husholdning+hytter i NO1+NO2+NO5 (prosjektets eget datasett) økte +2323 GWh i samme periode.

NRK skriver at årets nettoeksport «tilsvarer det økte forbruket blant husholdningene i Sør-Norge». Det er nivået på nettoeksporten i 2026 som sammenlignes, ikke fallet. Nivået jan-jun 2026 er 1 763 GWh og jan-jul 2026 (NRKs periode) 2 682 GWh, mot en forbruksøkning for husholdning+hytter i NO1+NO2+NO5 jan-jun på +2323 GWh. Størrelsene er i samme størrelsesorden (forhold 1.15 for jan-jul). NRKs påstand holder tallmessig i SSB-tallene.

Fallet i nettoeksport fra 2025 til 2026 (-10168 GWh) følger regnskapsmessig av identiteten nettoeksport = produksjon - bruttoforbruk, som holder eksakt begge år i SSB-tallene. Produksjonsfallet (-6379 GWh) utgjør 63 prosent av fallet og økningen i bruttoforbruk (+3789 GWh) 37 prosent. Dette er en regnskapsdekomponering; den årsaksmessige attribusjonen kan ikke avgjøres fra balansen alene.


## 5. Usikkerhet og forbehold

- SSB-tabellen (14091/12824) dekker hele Norge (alle prisområder NO1-NO5), mens prosjektets eget forbrukstall og NRKs påstand om «husholdningene i Sør-Norge» gjelder NO1+NO2+NO5. Nettoeksporten er ikke brutt ned på prisområde i denne SSB-tabellen. Sammenligningen i pkt. 3-4 er derfor mellom et landstall (nettoeksport, produksjon, bruttoforbruk) og et Sør-Norge-tall (husholdning+hytter).
- NRKs graf viser perioden 1.1.-31.7. med kilde Statnett; denne rapporten bruker SSBs månedlige elektrisitetsbalanse og jan-jun for sammenlignbarhet med `tab_p1_forbruk_jan_jun.csv`. Tallene i pkt. 2-4 er derfor ikke direkte avlesninger fra NRKs figur, og kan avvike noe fra den fordi juli er utelatt og fordi kilden (Statnett vs. SSB) er ulik.
- Nettoeksport er her definert som eksport minus import (SSBs Produk2-kategorier 3 og 2). Dette er standarddefinisjonen og bør svare til det NRK/Statnett kaller nettoeksport, men er ikke verifisert direkte mot Statnetts egne driftsdata (driftsdata.statnett.no) i denne kjøringen.
- SSBs tall for 2026 kan være delvis foreløpige (siste publiserte måned i tabell 14091 er 2026-07); revisjoner kan forekomme.
- Husholdningsforbruk i SSB-tabellen (Produk2=7.4) er et landstall og er IKKE det samme som Elhub-tallet i `tab_p1_forbruk_jan_jun.csv` (NO1+NO2+NO5, husholdning+hytter) – de to rapporteres hver for seg i pkt. 2-3, ikke summert eller avstemt mot hverandre.
