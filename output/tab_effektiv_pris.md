# Effektiv marginalpris med strømstøtte – tabell og tolkning

Parametre og kilder: `kilder/stromstotte_parametre.md`. Tallformat: punktum som desimaltegn (som øvrige output-filer i prosjektet).

## Vintermåneder (des-feb), snitt over NO1/NO2/NO5, øre/kWh eks. mva

| vinter   |    spot |   p_eff |   diff |   diff_pst |   n_omrade_maneder |
|:---------|--------:|--------:|-------:|-----------:|-------------------:|
| 2021/22  | 145.402 |  93.955 | 51.446 |     35.382 |                  9 |
| 2022/23  | 169.773 |  79.977 | 89.796 |     52.892 |                  9 |
| 2023/24  |  83.125 |  67.475 | 15.649 |     18.827 |                  9 |
| 2024/25  |  76.102 |  56.908 | 19.194 |     25.222 |                  9 |
| 2025/26  | 108.988 |  78.55  | 30.438 |     27.928 |                  9 |

`diff` = spot - p_eff (hvor mye strømstøtten trekker prisen ned i snitt over vintermånedene); `diff_pst` = diff i prosent av spotprisen.

## Modeller: post_np-koeffisient, spot vs. effektiv pris (log-log, samme spesifikasjon ellers)

- M1 (log spot): post_np = 0.0872 (se 0.0071, p 0.0000) -> 9.11 prosent
- M1e (log p_eff): post_np = 0.0831 (se 0.0070, p 0.0000) -> 8.67 prosent
- M2 (log spot, + kalendermåned): post_np = 0.0667 (se 0.0070, p 0.0000) -> 6.90 prosent
- M2e (log p_eff, + kalendermåned): post_np = 0.0640 (se 0.0069, p 0.0000) -> 6.61 prosent
- F2e: share_post = 0.0842 (p 0.2210); log_p_eff = -0.0119 (p 0.0000) - identifisert av kun tre prisområder, se merknad i loggen.
- Prisgap: koeffisient på np_andel_hh × (log p_eff − log 40) = 0.1014 (se 0.0791, p 0.1998); implisert egenpriselastisitet -0.101. Identifisert av samme tverrsnittsvariasjon i oppslutning som F2, ikke av prisvariasjon. Snittgap i postperioden 0.62 logpoeng (marginalprisen om lag halveres); D7-estimatet 0,0299 delt på snittgapet gir -0.048.

## Tolkning

Strømstøtten trekker vintermånedenes gjennomsnittlige spotpris ned med 41.3 øre/kWh i snitt over de fem vintrene (32.1 prosent av spotprisen), med størst nivåforskjell i vintrene med høyest spotpris (2022/23: 89.8 øre). post_np-koeffisienten endres når effektiv pris (p_eff) erstatter spotpris i samme spesifikasjon: M1 gir 0.0872 med log(spot) mot 0.0831 med log(p_eff); M2 gir 0.0667 mot 0.0640. Retningen er konsistent med at p_eff er en mindre volatil og lavere pris enn spot i høyprisperioder, slik at prisvariabelen fanger opp noe mindre av forbruksvariasjonen og post_np-dummyen dermed kan ta opp noe av det spotprisen ellers ville forklart. F2e-spesifikasjonen identifiserer log(p_eff) fra kun tre prisområder innad i hver kalendermåned, som er et svakt identifisert grunnlag - koeffisienten rapporteres, men bør ikke tillegges selvstendig vekt. Prisgap-modellen gir en implisert egenpriselastisitet på -0.10 (p 0.20); den er identifisert av tverrsnittsvariasjon i oppslutning, ikke av prisvariasjon, og D7-estimatet tilsvarer -0.05. Korttids husholdningselastisiteter i litteraturen ligger typisk i −0,05 til −0,2 ([fylles inn] referanse).
