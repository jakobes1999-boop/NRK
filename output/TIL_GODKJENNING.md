# Tall til godkjenning – etterprøving av NRK «Prisen for billig strøm»
Generert 2026-09-06 18:06. Kilder og skript i src/. Ikke ført inn i notatet. Kritikk: notat/KRITIKK_2026-09-05.md.

## Tabell 1: Energiekvivalent (s05, NVE vannkraftdatabase, veid med MidProd_91_20)

|         |   n_kraftverk |   prod_gwh |   enekv_kwh_m3 |   liter_per_kwh |   enekv_uveid |   avvik_fra_nrk_pst |
|:--------|--------------:|-----------:|---------------:|----------------:|--------------:|--------------------:|
| NO1     |           151 |    17621.3 |          0.302 |        3309.23  |         0.255 |             131.577 |
| NO2     |           397 |    46669.5 |          0.813 |        1229.49  |         0.429 |             -13.961 |
| NO1+NO2 |           548 |    64290.8 |          0.673 |        1485.35  |         0.381 |               3.943 |
| NO5     |           247 |    30103.1 |          1.463 |         683.548 |         0.643 |             -52.166 |
| Norge   |          1459 |   138159   |          0.902 |        1108.57  |         0.47  |             -22.424 |

NRK: 1 429 l/kWh. Vårt NO1+NO2: 1485 l/kWh, avvik +3.9 %.
Dusj (vann_dusj.py): 1,4 kWh × 1 429 = 2 001 l. 6 min à 6 l/min ved 38 °C gir 1,4 kWh bare hvis inntaksvannet er 4,6 °C; ved 8 °C er det 1,26 kWh (6,7 min for 1,4 kWh); med virkningsgrad 0,9 på berederen gir 8 °C 1,4 kWh, så NRKs tall holder. Forhold kraftverksvann/dusjvann ≈ 50.

## Panelbeskrivelse (s06)

- Kommuner: 197; måneder: 51 (2022-02–2026-04); rader: 10047
- Per område: {'NO1': 86, 'NO2': 77, 'NO5': 34}
- Prisområde-kilde: {'fylke=nve': 126, 'fylke': 59, 'nve': 10, 'unntak': 2} (overstyringer: output/tab_kommune_prisomrade.csv – TIL VERIFISERING mot Statnett/nettselskap)
- Gradtall-kilde (kommuner): {'kommune': 162, 'fylke': 35}
- Andel husholdningsmålere med Norgespris, 2026-04, målerveid: {'NO1': 0.609, 'NO2': 0.748, 'NO5': 0.588}; Privat inkl. hytter: {'NO1': 0.622, 'NO2': 0.756, 'NO5': 0.612}
- Kommune-måneder i post-perioden med np_andel = 0 (anonymisering < 100 målere): 13 av 1379

## Tabell 2: Faste-effekter-regresjoner, NRK-lik og varianter (s07)

|                     | M1 NRK-lik          | M1b NRK-lik, per målepunkt   | M2 + kalendermåned   | M2b + kalendermåned, per målepunkt   | M3 år×måned-FE, andel Norgespris (Privat)   | M4 som M3, per målepunkt   | M4b som M4, husholdningsandel   | M5 placebo 2024-10 (data ≤ 2025-09)   | M5b placebo, per målepunkt   |
|:--------------------|:--------------------|:-----------------------------|:---------------------|:-------------------------------------|:--------------------------------------------|:---------------------------|:--------------------------------|:--------------------------------------|:-----------------------------|
| egd                 | 0.0019*** (0.0000)  | 0.0019*** (0.0000)           | 0.0011*** (0.0000)   | 0.0011*** (0.0000)                   | 0.0008*** (0.0001)                          | 0.0008*** (0.0001)         | 0.0008*** (0.0001)              | 0.0019*** (0.0000)                    | 0.0019*** (0.0000)           |
| spot_ore_kwh        | -0.0004*** (0.0000) | -0.0004*** (0.0000)          | -0.0002*** (0.0000)  | -0.0002*** (0.0000)                  | 0.0001nan (0.0002)                          | 0.0001nan (0.0002)         | 0.0001nan (0.0002)              | -0.0004*** (0.0000)                   | -0.0004*** (0.0000)          |
| post_np             | 0.0950*** (0.0069)  | 0.0840*** (0.0068)           | 0.0717*** (0.0070)   | 0.0607*** (0.0069)                   | nan                                         | nan                        | nan                             | 0.0509*** (0.0023)                    | 0.0435*** (0.0021)           |
| np_andel            | nan                 | nan                          | nan                  | nan                                  | 0.2408*** (0.0600)                          | 0.2084*** (0.0590)         | nan                             | nan                                   | nan                          |
| np_andel_hh         | nan                 | nan                          | nan                  | nan                                  | nan                                         | nan                        | 0.0829nan (0.0552)              | nan                                   | nan                          |
| innt_1000           | 0.0009*** (0.0000)  | 0.0005*** (0.0000)           | 0.0010*** (0.0000)   | 0.0006*** (0.0000)                   | -0.0001nan (0.0002)                         | -0.0000nan (0.0001)        | -0.0001nan (0.0001)             | 0.0005*** (0.0000)                    | 0.0002*** (0.0000)           |
| snitt_bruksareal_m2 | -0.0009nan (0.0008) | 0.0006nan (0.0009)           | -0.0017* (0.0007)    | -0.0001nan (0.0008)                  | -0.0009nan (0.0007)                         | 0.0004nan (0.0007)         | 0.0004nan (0.0007)              | -0.0010nan (0.0008)                   | 0.0004nan (0.0008)           |

|    | modell                                    |     N |   R2_within |   R2_overall |
|---:|:------------------------------------------|------:|------------:|-------------:|
|  0 | M1 NRK-lik                                | 10047 |       0.941 |        0.132 |
|  1 | M1b NRK-lik, per målepunkt                | 10047 |       0.941 |        0.283 |
|  2 | M2 + kalendermåned                        | 10047 |       0.962 |        0.072 |
|  3 | M2b + kalendermåned, per målepunkt        | 10047 |       0.963 |        0.154 |
|  4 | M3 år×måned-FE, andel Norgespris (Privat) | 10047 |       0.633 |        0.01  |
|  5 | M4 som M3, per målepunkt                  | 10047 |       0.631 |        0.092 |
|  6 | M4b som M4, husholdningsandel             | 10047 |       0.611 |        0.082 |
|  7 | M5 placebo 2024-10 (data ≤ 2025-09)       |  8668 |       0.95  |        0.092 |
|  8 | M5b placebo, per målepunkt                |  8668 |       0.95  |        0.207 |

Prosenteffekt (exp(β)−1) for Norgespris-variablene:
|             | modell                                    |   koef |     se |      p |   pst_effekt |
|:------------|:------------------------------------------|-------:|-------:|-------:|-------------:|
| post_np     | M1 NRK-lik                                | 0.095  | 0.0069 | 0      |       9.9693 |
| post_np     | M1b NRK-lik, per målepunkt                | 0.084  | 0.0068 | 0      |       8.7586 |
| post_np     | M2 + kalendermåned                        | 0.0717 | 0.007  | 0      |       7.4288 |
| post_np     | M2b + kalendermåned, per målepunkt        | 0.0607 | 0.0069 | 0      |       6.2574 |
| np_andel    | M3 år×måned-FE, andel Norgespris (Privat) | 0.2408 | 0.06   | 0.0001 |      27.2307 |
| np_andel    | M4 som M3, per målepunkt                  | 0.2084 | 0.059  | 0.0004 |      23.1678 |
| np_andel_hh | M4b som M4, husholdningsandel             | 0.0829 | 0.0552 | 0.1326 |       8.6483 |
| post_np     | M5 placebo 2024-10 (data ≤ 2025-09)       | 0.0509 | 0.0023 | 0      |       5.2226 |
| post_np     | M5b placebo, per målepunkt                | 0.0435 | 0.0021 | 0      |       4.4457 |

NRK: gradtall 0,0019***, spotpris −0,0005***, Norgespris 0,0822*** (8,6 %), medianinntekt 0,0024***, R² 0,9376.

Standardfeil for post_np: kluster (kommune) mot Driscoll-Kraay. post_np er lik for alle kommuner, så kommune-klustring undervurderer usikkerheten:
|    | modell                              |   koef |   se_kluster |   se_driscoll_kraay |   p_driscoll_kraay |
|---:|:------------------------------------|-------:|-------------:|--------------------:|-------------------:|
|  0 | M1 NRK-lik                          | 0.095  |       0.0069 |              0.0175 |             0      |
|  1 | M1b NRK-lik, per målepunkt          | 0.084  |       0.0068 |              0.0168 |             0      |
|  2 | M2 + kalendermåned                  | 0.0717 |       0.007  |              0.0157 |             0      |
|  3 | M2b + kalendermåned, per målepunkt  | 0.0607 |       0.0069 |              0.0147 |             0      |
|  4 | M5 placebo 2024-10 (data ≤ 2025-09) | 0.0509 |       0.0023 |              0.0168 |             0.0024 |
|  5 | M5b placebo, per målepunkt          | 0.0435 |       0.0021 |              0.0175 |             0.0129 |

## Event-study kommunepanel: Privat-andel × måned (M3-oppsett, uten egd×kommune)

|                     |    koef |     se |      p |
|:--------------------|--------:|-------:|-------:|
| egd                 |  0.0008 | 0.0001 | 0      |
| spot_ore_kwh        |  0.0002 | 0.0002 | 0.285  |
| innt_1000           | -0.0001 | 0.0002 | 0.5494 |
| snitt_bruksareal_m2 | -0.0009 | 0.0007 | 0.1851 |
| np_x_2025-10        |  0.0257 | 0.0189 | 0.1742 |
| np_x_2025-11        |  0.1305 | 0.0245 | 0      |
| np_x_2025-12        |  0.3422 | 0.0867 | 0.0001 |
| np_x_2026-01        |  0.3877 | 0.098  | 0.0001 |
| np_x_2026-02        |  0.4157 | 0.1001 | 0      |
| np_x_2026-03        |  0.2656 | 0.1245 | 0.033  |
| np_x_2026-04        |  0.3072 | 0.1547 | 0.0471 |

## Forbedrede modeller (s10): kommunepanel F1–F7 og DiD D1–D6

|    | modell                                          | term            |    koef |     se |      p |     N |     r2 |   pst_effekt |
|---:|:------------------------------------------------|:----------------|--------:|-------:|-------:|------:|-------:|-------------:|
|  0 | F1 to-veis FE, share×post [log_kwh_mp]          | share_post      |  0.0854 | 0.069  | 0.2161 | 10047 | 0.9756 |       5.6953 |
|  1 | F2 + egd×kommune [log_kwh_mp]                   | share_post      |  0.0864 | 0.069  | 0.2108 | 10047 | 0.9839 |       5.7629 |
|  2 | F3 + share×spot [log_kwh_mp]                    | share_post      |  0.0835 | 0.069  | 0.2264 | 10047 | 0.984  |       5.5622 |
|  3 | F3 + share×spot [log_kwh_mp]                    | share_spot      | -0.0002 | 0.0001 | 0.0148 | 10047 | 0.984  |     nan      |
|  4 | F4 placebo okt. 2024 (≤ sep. 2025) [log_kwh_mp] | share_post      | -0.0018 | 0.0152 | 0.9084 |  8668 | 0.9906 |      -0.1135 |
|  5 | F6 Privat-andel inkl. hytter [log_kwh_mp]       | share_priv_post |  0.1597 | 0.0786 | 0.042  | 10047 | 0.984  |      10.9153 |
|  6 | F1 to-veis FE, share×post [log_kwh]             | share_post      |  0.091  | 0.0697 | 0.1917 | 10047 | 0.9969 |       6.0783 |
|  7 | F2 + egd×kommune [log_kwh]                      | share_post      |  0.0905 | 0.0668 | 0.1757 | 10047 | 0.9979 |       6.0439 |
|  8 | F3 + share×spot [log_kwh]                       | share_post      |  0.0866 | 0.0667 | 0.1943 | 10047 | 0.9979 |       5.7776 |
|  9 | F3 + share×spot [log_kwh]                       | share_spot      | -0.0002 | 0.0001 | 0.0125 | 10047 | 0.9979 |     nan      |
| 10 | F4 placebo okt. 2024 (≤ sep. 2025) [log_kwh]    | share_post      |  0.0106 | 0.019  | 0.5756 |  8668 | 0.9988 |       0.6905 |
| 11 | F6 Privat-andel inkl. hytter [log_kwh]          | share_priv_post |  0.1953 | 0.0789 | 0.0133 | 10047 | 0.998  |      13.5066 |
| 12 | F7 F2 på fylkesregel-panel [log_kwh_mp]         | share_post      |  0.0825 | 0.0266 | 0.0019 | 10812 | 0.984  |       5.4957 |
| 13 | D1 gruppe-FE + område×måned-FE                  | bestilt_post    |  0.0589 | 0.0281 | 0.0357 |   837 | 0.9975 |       6.0687 |
| 14 | D2 + bestilt×kalendermåned                      | bestilt_post    |  0.0433 | 0.0112 | 0.0001 |   837 | 0.9977 |       4.4289 |
| 15 | D3 + bestilt×EGD                                | bestilt_post    |  0.0429 | 0.0133 | 0.0013 |   837 | 0.9977 |       4.3795 |
| 16 | D3 + bestilt×EGD                                | bestilt_egd     |  0.0001 | 0.0001 | 0.3477 |   837 | 0.9977 |     nan      |
| 17 | D4 placebo okt. 2024 på D3 (≤ sep. 2025)        | bestilt_post    |  0.0128 | 0.0103 | 0.2136 |   648 | 0.9977 |       1.288  |
| 18 | D4b placebo okt. 2024 på D2 (≤ sep. 2025)       | bestilt_post    |  0.0081 | 0.0073 | 0.2664 |   648 | 0.9977 |       0.8145 |
| 19 | D5 D3, tidlig/sent                              | tidlig_post     |  0.0454 | 0.0149 | 0.0022 |   837 | 0.9977 |       4.6466 |
| 20 | D5 D3, tidlig/sent                              | sent_post       |  0.0396 | 0.016  | 0.0132 |   837 | 0.9977 |       4.038  |
| 21 | D5b D2, tidlig/sent                             | tidlig_post     |  0.0459 | 0.013  | 0.0004 |   837 | 0.9977 |       4.6969 |
| 22 | D5b D2, tidlig/sent                             | sent_post       |  0.04   | 0.0143 | 0.0053 |   837 | 0.9977 |       4.0862 |
| 23 | D6 D2 kun Husholdning Høy                       | bestilt_post    |  0.0239 | 0.0026 | 0      |   279 | 0.9999 |       2.4196 |
| 24 | D6 D2 kun Husholdning Lav                       | bestilt_post    |  0.0383 | 0.0044 | 0      |   279 | 0.9988 |       3.9052 |
| 25 | D6 D2 kun Husholdning Medium                    | bestilt_post    |  0.0256 | 0.003  | 0      |   279 | 0.9998 |       2.5896 |

share-modeller: β er effekten av å gå fra 0 til 100 % oppslutning; pst_effekt er ved målerveid husholdningsandel. Hovedspesifikasjoner: F2 (kommunepanel) og D2/D3 (DiD).

F5 pre-trendtest: 44 pre-koeffisienter, snitt -0.1483, sd 0.1400, spenn -0.358 til 0.122, 22 signifikante på 5 %. Post: snitt -0.1515, spenn -0.239 til -0.002. Figur: output/fig_event_study_f5.png

DiD event-study, D2-stil (avvik fra egen sesongprofil), prosent per post-måned:
| maned   |   bestilt |   sent |   tidlig |
|:--------|----------:|-------:|---------:|
| 2025-10 |       2.7 |    2.3 |      3.1 |
| 2025-11 |       3.3 |    2.9 |      3.7 |
| 2025-12 |       3.8 |    3.4 |      4.1 |
| 2026-01 |       5.3 |    4.8 |      5.7 |
| 2026-02 |       5.7 |    5.3 |      6   |
| 2026-03 |       5.3 |    5   |      5.6 |
| 2026-04 |       4.9 |    4.7 |      5.1 |
Figur: output/fig_event_study_d2.png

## Tabell 3: Forbruk per målepunkt før okt. 2025, kWh/måned (s08, husholdninger)

| pa   |   Bestilt sent |   Bestilt tidlig |   Ikke bestilt |   bestilt_alle |   forskjell_pst |
|:-----|---------------:|-----------------:|---------------:|---------------:|----------------:|
| NO1  |         1256.3 |           1387.1 |          821.1 |         1329.5 |            61.9 |
| NO2  |         1220.4 |           1347.6 |          927.1 |         1300.7 |            40.3 |
| NO5  |         1279.3 |           1372.4 |          941.5 |         1319.5 |            40.1 |

Innen EAC-gruppe:
|                               |   Bestilt sent |   Bestilt tidlig |   Ikke bestilt |
|:------------------------------|---------------:|-----------------:|---------------:|
| ('NO1', 'Husholdning Høy')    |         2041.1 |           2073.3 |         1985.5 |
| ('NO1', 'Husholdning Lav')    |          411   |            416.1 |          360.2 |
| ('NO1', 'Husholdning Medium') |          993.5 |           1005.6 |          969.7 |
| ('NO2', 'Husholdning Høy')    |         1854.9 |           1887.2 |         1835   |
| ('NO2', 'Husholdning Lav')    |          449.1 |            443.8 |          420.4 |
| ('NO2', 'Husholdning Medium') |          976.4 |            992.5 |          957.3 |
| ('NO5', 'Husholdning Høy')    |         1927.7 |           1951.3 |         1878.4 |
| ('NO5', 'Husholdning Lav')    |          426.1 |            436.1 |          399.7 |
| ('NO5', 'Husholdning Medium') |          976.5 |            984.7 |          953.5 |

Målepunkt per status, siste måned:
| pa   |   Bestilt sent |   Bestilt tidlig |   Ikke bestilt |
|:-----|---------------:|-----------------:|---------------:|
| NO1  |         187147 |           237907 |         243356 |
| NO2  |         123987 |           212890 |          97341 |
| NO5  |          55972 |            42518 |          61717 |

## Tabell 4: Diff-in-diff, ujustert (s08) – erstattes av D2/D3 i notatet

|    | modell                 | term         |   koef |     se |      p |    pst |   N |
|---:|:-----------------------|:-------------|-------:|-------:|-------:|-------:|----:|
|  0 | Bestilt (alle) vs ikke | bestilt:post | 0.0589 | 0.0281 | 0.0357 | 6.0687 | 837 |
|  1 | Tidlig / sent vs ikke  | tidlig:post  | 0.0615 | 0.0289 | 0.0336 | 6.3409 | 837 |
|  2 | Tidlig / sent vs ikke  | sent:post    | 0.0556 | 0.0293 | 0.0577 | 5.7206 | 837 |
|  3 | Bestilt vs ikke, NO1   | bestilt:post | 0.0695 | 0.0461 | 0.1316 | 7.2002 | 279 |
|  4 | Bestilt vs ikke, NO2   | bestilt:post | 0.0447 | 0.0292 | 0.1258 | 4.5736 | 279 |
|  5 | Bestilt vs ikke, NO5   | bestilt:post | 0.0439 | 0.0256 | 0.0861 | 4.4872 | 279 |

Ujustert event-study (ref. sep. 2025): pre snitt 0.0003 (sd 0.0234); des–feb før ordningen +2.6 %, jun–aug -2.9 %. Post snitt 0.0592. Figur: output/fig_event_study_did.png

## NRKs øvrige tallpåstander (s11)

## P1 Forbruk januar–juni, NO1+NO2+NO5 (GWh)
|   aar |   Husholdning |   Hytter |   Hus+hytter |   endring_hus_hytter_gwh |   endring_pst |   dusj_aar |   vann_mrd_liter_1429 |   mnd_dekket |
|------:|--------------:|---------:|-------------:|-------------------------:|--------------:|-----------:|----------------------:|-------------:|
|  2021 |       16868.3 |   1206.3 |      18074.6 |                    nan   |         nan   |      nan   |                 nan   |            6 |
|  2022 |       13748.6 |    917.1 |      14665.7 |                  -3408.9 |         -18.9 |   -27796.2 |               -4871.3 |            6 |
|  2023 |       14050   |    832   |      14882   |                    216.4 |           1.5 |     1764.4 |                 309.2 |            6 |
|  2024 |       15531   |    954.3 |      16485.3 |                   1603.2 |          10.8 |    13072.7 |                2291   |            6 |
|  2025 |       14882.9 |    912.8 |      15795.7 |                   -689.5 |          -4.2 |    -5622.5 |                -985.4 |            6 |
|  2026 |       17005.6 |   1113.2 |      18118.9 |                   2323.1 |          14.7 |    18942.6 |                3319.7 |            6 |

1 dusjår = 122,640 kWh. NRK: økningen 2026 tilsvarer 20 000 dusjår = 2,453 GWh.
- P2 Norgespris 40 øre + mva: 1.4 kWh × 0.50 kr = 0.70 kr
- P2 markedspris 150 øre: 1.4 kWh × 1.50 kr = 2.10 kr

## P3 Inntekt og oppslutning (kommunenivå, apr. 2026, husholdningsmålere)
|            |   np_andel |   np_andel_hh |   innt_1000 |   snitt_bruksareal_m2 |   andel_over_160m2 |   kwh_per_mp |
|:-----------|-----------:|--------------:|------------:|----------------------:|-------------------:|-------------:|
| alle (197) |      0.796 |             1 |       0.172 |                 0.2   |              0.193 |        0.088 |
| NO1 (86)   |      0.619 |             1 |       0.454 |                 0.335 |              0.314 |        0.23  |
| NO2 (77)   |      0.358 |             1 |       0.028 |                -0.021 |             -0.035 |        0.065 |
| NO5 (34)   |      0.79  |             1 |       0.015 |                 0.078 |              0.104 |        0.295 |

Målerveid regresjon andel ~ inntekt (1 000 kr) + område-FE: β = 0.00041 (se 0.00012, p = 0.001); med boligstørrelse: β_innt = 0.00020 (p = 0.002), β_bolig = 0.00146 (p = 0.000). 10 000 kr høyere medianinntekt ⇒ +0.41 prosentpoeng.

Oppslutning per område (målerveid, husholdning): {'NO1': 0.609, 'NO2': 0.748, 'NO5': 0.588}

## Beregninger fra kritikkrunde 2 (s12): fyringssesong, D7, forbruksandel, dekomponering, F7-diagnose

## A Gradtall per fyringssesong (okt–apr), 197 kommuner
| sesong   |   egd_uveid |   egd_veid |   mnd |
|:---------|------------:|-----------:|------:|
| 2021/22  |        1338 |       1250 |     3 |
| 2022/23  |        3309 |       3126 |     7 |
| 2023/24  |        3589 |       3447 |     7 |
| 2024/25  |        3081 |       2910 |     7 |
| 2025/26  |        3324 |       3133 |     7 |
|   aar |   egd_jan_uveid |   egd_jan_veid |
|------:|----------------:|---------------:|
|  2023 |             596 |            559 |
|  2024 |             685 |            668 |
|  2025 |             567 |            554 |
|  2026 |             711 |            676 |

## B DiD med sesongprofil per EAC-gruppe (bestilt × kalendermåned × EAC)
|    | modell                                  | term         |    koef |     se |      p |     pst |   N |   klustre |
|---:|:----------------------------------------|:-------------|--------:|-------:|-------:|--------:|----:|----------:|
|  0 | D2 felles sesongprofil                  | bestilt_post |  0.0433 | 0.0112 | 0.0001 |  4.4289 | 837 |        27 |
|  1 | D2e sesongprofil per EAC                | bestilt_post |  0.0433 | 0.0114 | 0.0001 |  4.4289 | 837 |        27 |
|  2 | D2ep sesongprofil per EAC × område      | bestilt_post |  0.0433 | 0.012  | 0.0003 |  4.4289 | 837 |        27 |
|  3 | D2e tidlig/sent                         | tidlig_post  |  0.0457 | 0.0123 | 0.0002 |  4.6717 | 837 |        27 |
|  4 | D2e tidlig/sent                         | sent_post    |  0.0404 | 0.0128 | 0.0017 |  4.1182 | 837 |        27 |
|  5 | D7 område×måned×EAC-FE + sesong per EAC | bestilt_post |  0.0299 | 0.0028 | 0      |  3.0331 | 837 |        27 |
|  6 | D7 tidlig/sent                          | tidlig_post  |  0.0309 | 0.003  | 0      |  3.1428 | 837 |        27 |
|  7 | D7 tidlig/sent                          | sent_post    |  0.0286 | 0.0032 | 0      |  2.9023 | 837 |        27 |
|  8 | D7 placebo okt 2024                     | bestilt_post | -0.0019 | 0.0012 | 0.1269 | -0.1897 | 648 |        27 |
|  9 | D2e placebo okt 2024                    | bestilt_post |  0.0081 | 0.0075 | 0.2774 |  0.8145 | 648 |        27 |
| 10 | D6 kun Husholdning Høy                  | bestilt_post |  0.0239 | 0.0026 | 0      |  2.4196 | 279 |         9 |
| 11 | D6 kun Husholdning Lav                  | bestilt_post |  0.0383 | 0.0044 | 0      |  3.9052 | 279 |         9 |
| 12 | D6 kun Husholdning Medium               | bestilt_post |  0.0256 | 0.003  | 0      |  2.5896 | 279 |         9 |

Forbruksveid snitt av D6-koeffisientene: 0.0253 → 2.56 % (vekter: {'Husholdning Høy': 0.68, 'Husholdning Lav': 0.064, 'Husholdning Medium': 0.256})

## C Bestillernes andel av husholdningsforbruket (post-periode, bestillingsstatus-uttrekket)
| pa   |           0 |           1 |   forbruksandel_bestilt |   malerandel_bestilt |
|:-----|------------:|------------:|------------------------:|---------------------:|
| NO1  | 1.75297e+09 | 5.16973e+09 |                   0.747 |                0.636 |
| NO2  | 8.00241e+08 | 4.03853e+09 |                   0.835 |                0.776 |
| NO5  | 5.10395e+08 | 1.17824e+09 |                   0.698 |                0.615 |
| Sum  | 3.06361e+09 | 1.03865e+10 |                   0.772 |                0.681 |
  D2 0.0433: bestillereffekt 4.43 % → aggregert med forbruksandel 0.772: 3.42 %; med målerandel 0.681: 3.02 %
  D2e: bestillereffekt 4.43 % → aggregert med forbruksandel 0.772: 3.42 %; med målerandel 0.681: 3.02 %
  D6 forbruksveid: bestillereffekt 2.56 % → aggregert med forbruksandel 0.772: 1.97 %; med målerandel 0.681: 1.74 %

## D Jan–apr: forbruk per måler (Privat, 197 kommuner) og målerveid gradtall
|   aar |   kwh_per_mp |   kwh_gwh |   egd_veid |   spot_snitt |   d_kwh_mp_pst |   d_egd |   vaerforklart_pst [M1 0.0019] |   vaerforklart_pst [M2 0.0011] |   vaerforklart_pst [egd×kommune, målerveid snitt 0.00193] |
|------:|-------------:|----------:|-----------:|-------------:|---------------:|--------:|-------------------------------:|-------------------------------:|----------------------------------------------------------:|
|  2022 |      3739.47 |   8107.17 |    1249.55 |       160.45 |         nan    |  nan    |                         nan    |                         nan    |                                                    nan    |
|  2023 |      5321.31 |  11738.5  |    1876.86 |       116.16 |          42.3  |  156.83 |                          34.71 |                          18.83 |                                                     35.38 |
|  2024 |      5978.99 |  13387.2  |    1979.6  |        71.27 |          12.36 |   25.68 |                           5    |                           2.87 |                                                      5.09 |
|  2025 |      5471.06 |  12354.9  |    1742.72 |        70.69 |          -8.5  |  -59.22 |                         -10.64 |                          -6.31 |                                                    -10.81 |
|  2026 |      6304.69 |  14369.9  |    2008.96 |       118.75 |          15.24 |   66.56 |                          13.48 |                           7.6  |                                                     13.72 |
Lesning: 2026 mot 2025 og 2026 mot 2024. Differansen mellom d_kwh_mp_pst og vaerforklart er det været ikke forklarer, gitt valgt gradtallshelning.

## E Spredning i husholdningsoppslutning: F2-panel (NVE-kobling) mot F7-panel (fylkesregel)
|                |   kommuner |   snitt |    sd |   min |   p10 |   maks |
|:---------------|-----------:|--------:|------:|------:|------:|-------:|
| F2 NVE-kobling |        197 |   0.677 | 0.094 |     0 | 0.583 |  0.924 |
| F7 fylkesregel |        212 |   0.639 | 0.167 |     0 | 0.56  |  0.924 |
Kommuner bare i F7 (15): Dovre (NO1, andel 0.13), Lesja (NO1, andel 0.01), Skjåk (NO1, andel 0.00), Lom (NO1, andel 0.12), Vågå (NO1, andel 0.16), Sel (NO1, andel 0.18), Kinn (NO5, andel 0.16), Hyllestad (NO5, andel 0.18), Askvoll (NO5, andel 0.17), Fjaler (NO5, andel 0.16), Sunnfjord (NO5, andel 0.16), Bremanger (NO5, andel 0.17), Stad (NO5, andel 0.13), Gloppen (NO5, andel 0.20), Stryn (NO5, andel 0.11)

## F Oppslutning husholdning apr. 2026: Norgespris-filen (kommune) mot bestillingsstatus-uttrekket
|     |   norgespris_fil |   status_uttrekk |   diff_pp |
|:----|-----------------:|-----------------:|----------:|
| NO1 |            0.609 |            0.636 |     2.665 |
| NO2 |            0.748 |            0.776 |     2.822 |
| NO5 |            0.588 |            0.615 |     2.651 |
Forskjellen kan skyldes at status-uttrekket teller målere per april 2026 med status «bestilt» uansett når, mens Norgespris-filen teller aktive avtaler den enkelte dag, og at kommuner med < 100 målere er nullet i Norgespris-filen.

## Dose-respons for «Bestilt sent» (s13): skjæringsdato 1./2. oktober 2025 fra Elhubs dokumentasjon, behandlingsandel per måned fra daglige tellinger; versjon 2 etter KRITIKK3: begge sesongspesifikasjoner, nullverdi, bootstrap

## Dose: andel av sent-gruppen med Norgespris, snitt per måned (daglige tellinger, alle husholdningsmålere)
| maned   |   NO1 |   NO2 |   NO5 |
|:--------|------:|------:|------:|
| 2025-10 | 0.23  | 0.259 | 0.175 |
| 2025-11 | 0.481 | 0.522 | 0.407 |
| 2025-12 | 0.646 | 0.686 | 0.595 |
| 2026-01 | 0.784 | 0.811 | 0.763 |
| 2026-02 | 0.891 | 0.907 | 0.882 |
| 2026-03 | 0.953 | 0.96  | 0.946 |
| 2026-04 | 0.987 | 0.99  | 0.986 |
Alle målere 01.10.2025: 2006042, Norgespris 696948; 30.04.2026 Norgespris 1315297. Statuskohorten: tidlig 493 315, sent 367 106 (43 prosent sene); målere utenfor kohorten: 55 prosent sene. Kohortens eget inntredelsesforløp er ikke observert (V1).

## Sent-gruppens sesongprofil ut over tidlig-gruppens i FØRPERIODEN (okt 2023–sep 2025), prosentpoeng relativt til oktober
|    |   01 |   02 |   03 |   04 |   05 |   06 |   07 |   08 |   09 |   10 |   11 |   12 |
|:---|-----:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
| pp | 0.39 | 0.91 | 1.09 | 0.93 | 0.62 | 0.26 | 0.41 | -0.1 | 0.03 |    0 | 0.23 | 0.04 |
Profilen er ikke flat: kohortene har ulik sesongprofil også uten reform. Sesongprofil per kohort er derfor hovedspesifikasjon under.

## Estimater (p fra t(G-1); 95-prosentintervall med t(26); for E6 med 9 klustre er intervallet for smalt)
|                                                                                |    koef |     se |    p_t |   ki95_lav |   ki95_hoy |     pst |   klustre |   n |
|:-------------------------------------------------------------------------------|--------:|-------:|-------:|-----------:|-----------:|--------:|----------:|----:|
| ('E0 felles sesong', 'tidlig_post')                                            |  0.0309 | 0.003  | 0      |     0.0248 |     0.0371 |  3.1428 |        27 | 837 |
| ('E0 felles sesong', 'sent_post')                                              |  0.0286 | 0.0032 | 0      |     0.022  |     0.0352 |  2.9023 |        27 | 837 |
| ('E1 felles sesong', 'tidlig_post')                                            |  0.031  | 0.003  | 0      |     0.0249 |     0.0371 |  3.1485 |        27 | 837 |
| ('E1 felles sesong', 'sent_post')                                              |  0.0091 | 0.0051 | 0.0861 |    -0.0014 |     0.0196 |  0.9133 |        27 | 837 |
| ('E1 felles sesong', 'sent_dose')                                              |  0.0274 | 0.0058 | 0.0001 |     0.0154 |     0.0394 |  2.7759 |        27 | 837 |
| ('E4 felles sesong, sent kun via dose', 'tidlig_post')                         |  0.03   | 0.0028 | 0      |     0.0243 |     0.0356 |  3.0427 |        27 | 837 |
| ('E4 felles sesong, sent kun via dose', 'sent_dose')                           |  0.0376 | 0.0039 | 0      |     0.0295 |     0.0456 |  3.8296 |        27 | 837 |
| ('E0 sesong per kohort', 'tidlig_post')                                        |  0.0314 | 0.0032 | 0      |     0.0248 |     0.0381 |  3.194  |        27 | 837 |
| ('E0 sesong per kohort', 'sent_post')                                          |  0.028  | 0.0028 | 0      |     0.0223 |     0.0337 |  2.8414 |        27 | 837 |
| ('E1 sesong per kohort', 'tidlig_post')                                        |  0.0315 | 0.0032 | 0      |     0.0249 |     0.0381 |  3.1984 |        27 | 837 |
| ('E1 sesong per kohort', 'sent_post')                                          |  0.0131 | 0.0076 | 0.095  |    -0.0024 |     0.0286 |  1.3188 |        27 | 837 |
| ('E1 sesong per kohort', 'sent_dose')                                          |  0.0209 | 0.0092 | 0.0307 |     0.0021 |     0.0397 |  2.1144 |        27 | 837 |
| ('E4 sesong per kohort, sent kun via dose', 'tidlig_post')                     |  0.0304 | 0.0032 | 0      |     0.0239 |     0.037  |  3.0904 |        27 | 837 |
| ('E4 sesong per kohort, sent kun via dose', 'sent_dose')                       |  0.0364 | 0.0034 | 0      |     0.0294 |     0.0435 |  3.7092 |        27 | 837 |
| ('E2 kun sent vs ikke bestilt (sesong implisitt sent-spesifikk)', 'sent_post') | -0.0052 | 0.0034 | 0.1462 |    -0.0123 |     0.0018 | -0.5219 |        18 | 558 |
| ('E2 kun sent vs ikke bestilt (sesong implisitt sent-spesifikk)', 'sent_dose') |  0.0453 | 0.0047 | 0      |     0.0355 |     0.0551 |  4.6346 |        18 | 558 |
| ('E3 kun tidlig vs ikke bestilt', 'tidlig_post')                               |  0.0316 | 0.0039 | 0      |     0.0235 |     0.0397 |  3.2139 |        18 | 558 |
| ('E5 placebo okt 2024–apr 2025, felles sesong', 'tidlig_post')                 | -0.0068 | 0.0023 | 0.0065 |    -0.0115 |    -0.0021 | -0.6765 |        27 | 648 |
| ('E5 placebo okt 2024–apr 2025, felles sesong', 'sent_post')                   | -0.0127 | 0.0028 | 0.0001 |    -0.0184 |    -0.0069 | -1.2572 |        27 | 648 |
| ('E5 placebo okt 2024–apr 2025, felles sesong', 'sent_dose')                   |  0.0145 | 0.0014 | 0      |     0.0115 |     0.0174 |  1.4584 |        27 | 648 |
| ('E5 placebo okt 2024–apr 2025, sesong per kohort', 'tidlig_post')             | -0.0066 | 0.0018 | 0.0011 |    -0.0103 |    -0.0029 | -0.6617 |        27 | 648 |
| ('E5 placebo okt 2024–apr 2025, sesong per kohort', 'sent_post')               | -0.0049 | 0.0029 | 0.0948 |    -0.0108 |     0.0009 | -0.4937 |        27 | 648 |
| ('E5 placebo okt 2024–apr 2025, sesong per kohort', 'sent_dose')               |  0.0034 | 0.0025 | 0.1858 |    -0.0017 |     0.0085 |  0.3391 |        27 | 648 |
| ('E6 Husholdning Høy (9 klustre)', 'tidlig_post')                              |  0.0236 | 0.0028 | 0      |     0.0178 |     0.0293 |  2.3852 |         9 | 279 |
| ('E6 Husholdning Høy (9 klustre)', 'sent_post')                                |  0.0199 | 0.0077 | 0.0318 |     0.0041 |     0.0357 |  2.01   |         9 | 279 |
| ('E6 Husholdning Høy (9 klustre)', 'sent_dose')                                |  0.0064 | 0.0097 | 0.5285 |    -0.0135 |     0.0262 |  0.6386 |         9 | 279 |
| ('E6 Husholdning Lav (9 klustre)', 'tidlig_post')                              |  0.0426 | 0.0053 | 0      |     0.0317 |     0.0534 |  4.3484 |         9 | 279 |
| ('E6 Husholdning Lav (9 klustre)', 'sent_post')                                |  0.0048 | 0.0116 | 0.6906 |    -0.0191 |     0.0287 |  0.4805 |         9 | 279 |
| ('E6 Husholdning Lav (9 klustre)', 'sent_dose')                                |  0.041  | 0.014  | 0.0191 |     0.0122 |     0.0698 |  4.1835 |         9 | 279 |
| ('E6 Husholdning Medium (9 klustre)', 'tidlig_post')                           |  0.0285 | 0.0027 | 0      |     0.0229 |     0.0342 |  2.8945 |         9 | 279 |
| ('E6 Husholdning Medium (9 klustre)', 'sent_post')                             |  0.0062 | 0.0102 | 0.56   |    -0.0147 |     0.0271 |  0.6209 |         9 | 279 |
| ('E6 Husholdning Medium (9 klustre)', 'sent_dose')                             |  0.0223 | 0.0136 | 0.1409 |    -0.0058 |     0.0503 |  2.2544 |         9 | 279 |

## Månedsvise effekter (prosent), målerveid dose og forhold sent/tidlig

### Sesong felles
| maned   |   sent |   tidlig |   dose_v |   forhold |
|:--------|-------:|---------:|---------:|----------:|
| 2025-10 |   0.59 |     1.28 |     0.23 |      0.46 |
| 2025-11 |   1.46 |     2.06 |     0.48 |      0.71 |
| 2025-12 |   1.75 |     2.48 |     0.65 |      0.71 |
| 2026-01 |   3.65 |     4.25 |     0.79 |      0.86 |
| 2026-02 |   4.76 |     4.75 |     0.9  |      1    |
| 2026-03 |   4.21 |     3.71 |     0.95 |      1.13 |
| 2026-04 |   3.97 |     3.51 |     0.99 |      1.13 |

### Sesong kohort
| maned   |   sent |   tidlig |   dose_v |   forhold |
|:--------|-------:|---------:|---------:|----------:|
| 2025-10 |   0.81 |     1.1  |     0.23 |      0.74 |
| 2025-11 |   1.56 |     1.98 |     0.48 |      0.79 |
| 2025-12 |   1.95 |     2.32 |     0.65 |      0.84 |
| 2026-01 |   3.66 |     4.24 |     0.79 |      0.86 |
| 2026-02 |   4.48 |     4.98 |     0.9  |      0.9  |
| 2026-03 |   3.82 |     4.03 |     0.95 |      0.95 |
| 2026-04 |   3.67 |     3.76 |     0.99 |      0.98 |

## Nivå/dose-deling mot simulert nullverdi (K2): utfall konstruert med null seleksjon og samme per-enhets-effekt som tidlig
- felles sesong: sent_post estimert 0.91 pp, nullverdi 0.75 pp (merutslag 0.16); sent_dose estimert 2.74, nullverdi 2.39; tidlig_post 3.10.
- sesong per kohort: sent_post estimert 1.31 pp, nullverdi 0.43 pp (merutslag 0.88); sent_dose estimert 2.09, nullverdi 2.95; tidlig_post 3.15.

## 7-punktstilpasning sent_m = a + b × (dose_m × tidlig_m); nullverdier a = 0, b = 1. Parametrisk bootstrap fra klusterkovariansen, 20 000 trekk
- Sesong felles: a = 0.26 pp [-0.19, 0.76], b = 1.06 [0.89, 1.23]
- Sesong kohort: a = 0.67 pp [0.14, 1.22], b = 0.84 [0.70, 0.99]

## Robusthet for dose-responsen (s13b): dosegrenser for kohorten, gradtall per kohort, leads

NO1: sene bestillere totalt 331154, i kohorten 187147 (0.57)
NO2: sene bestillere totalt 194412, i kohorten 123987 (0.64)
NO5: sene bestillere totalt 92783, i kohorten 55972 (0.60)

## Dosegrenser per måned (snitt over områder)
| maned   |   dose_L |   dose |   dose_U |
|:--------|---------:|-------:|---------:|
| 2025-10 |    0.003 |  0.221 |    0.367 |
| 2025-11 |    0.137 |  0.47  |    0.78  |
| 2025-12 |    0.403 |  0.642 |    0.989 |
| 2026-01 |    0.643 |  0.786 |    1     |
| 2026-02 |    0.822 |  0.893 |    1     |
| 2026-03 |    0.922 |  0.953 |    1     |
| 2026-04 |    0.979 |  0.988 |    1     |

## 1. Dosegrenser (FE_K)

## 2. Gradtall per kohort (FE_K + tidlig×egd + sent×egd; egd i hundre gradtall)

## 3a. Lead: sent × dose neste måned ved siden av sent × dose
|                                                |   koef |     se |    p_t |   ki95_lav |   ki95_hoy |    pst |
|:-----------------------------------------------|-------:|-------:|-------:|-----------:|-----------:|-------:|
| ('E1 K, dose kohort sist', 'tidlig_post')      | 0.0315 | 0.0032 | 0      |     0.0249 |     0.0381 | 3.2002 |
| ('E1 K, dose kohort sist', 'sent_post')        | 0.0194 | 0.0049 | 0.0006 |     0.0092 |     0.0295 | 1.956  |
| ('E1 K, dose kohort sist', 'sent_dose')        | 0.0154 | 0.0064 | 0.0222 |     0.0024 |     0.0285 | 1.5564 |
| ('E4 K, dose kohort sist', 'tidlig_post')      | 0.0278 | 0.0037 | 0      |     0.0203 |     0.0354 | 2.8215 |
| ('E4 K, dose kohort sist', 'sent_dose')        | 0.0372 | 0.0045 | 0      |     0.028  |     0.0465 | 3.794  |
| ('E1 K, dose identisk', 'tidlig_post')         | 0.0315 | 0.0032 | 0      |     0.0249 |     0.0381 | 3.1984 |
| ('E1 K, dose identisk', 'sent_post')           | 0.0131 | 0.0076 | 0.095  |    -0.0024 |     0.0286 | 1.3188 |
| ('E1 K, dose identisk', 'sent_dose')           | 0.0209 | 0.0092 | 0.0307 |     0.0021 |     0.0397 | 2.1144 |
| ('E4 K, dose identisk', 'tidlig_post')         | 0.0304 | 0.0032 | 0      |     0.0239 |     0.037  | 3.0904 |
| ('E4 K, dose identisk', 'sent_dose')           | 0.0364 | 0.0034 | 0      |     0.0294 |     0.0435 | 3.7092 |
| ('E1 K, dose kohort først', 'tidlig_post')     | 0.0315 | 0.0032 | 0      |     0.0248 |     0.0381 | 3.1958 |
| ('E1 K, dose kohort først', 'sent_post')       | 0.0109 | 0.0091 | 0.2434 |    -0.0079 |     0.0296 | 1.0938 |
| ('E1 K, dose kohort først', 'sent_dose')       | 0.0194 | 0.0093 | 0.047  |     0.0003 |     0.0385 | 1.9552 |
| ('E4 K, dose kohort først', 'tidlig_post')     | 0.031  | 0.0032 | 0      |     0.0245 |     0.0375 | 3.1514 |
| ('E4 K, dose kohort først', 'sent_dose')       | 0.0307 | 0.0029 | 0      |     0.0248 |     0.0366 | 3.1181 |
| ('E0 K + egd per kohort', 'tidlig_egd')        | 0.0174 | 0.0036 | 0      |     0.0101 |     0.0247 | 1.7531 |
| ('E0 K + egd per kohort', 'sent_egd')          | 0.0113 | 0.0036 | 0.0045 |     0.0038 |     0.0187 | 1.1352 |
| ('E0 K + egd per kohort', 'tidlig_post')       | 0.0326 | 0.0033 | 0      |     0.0257 |     0.0395 | 3.3146 |
| ('E0 K + egd per kohort', 'sent_post')         | 0.0288 | 0.0029 | 0      |     0.0228 |     0.0348 | 2.9222 |
| ('E1 K + egd per kohort', 'tidlig_egd')        | 0.0174 | 0.0036 | 0      |     0.0101 |     0.0247 | 1.7536 |
| ('E1 K + egd per kohort', 'sent_egd')          | 0.0103 | 0.0037 | 0.0091 |     0.0028 |     0.0179 | 1.0394 |
| ('E1 K + egd per kohort', 'tidlig_post')       | 0.0326 | 0.0033 | 0      |     0.0258 |     0.0395 | 3.3186 |
| ('E1 K + egd per kohort', 'sent_post')         | 0.0143 | 0.006  | 0.024  |     0.002  |     0.0266 | 1.4426 |
| ('E1 K + egd per kohort', 'sent_dose')         | 0.0202 | 0.0058 | 0.0019 |     0.0082 |     0.0322 | 2.0433 |
| ('E4 K + egd per kohort', 'tidlig_egd')        | 0.0173 | 0.0035 | 0      |     0.01   |     0.0246 | 1.7492 |
| ('E4 K + egd per kohort', 'sent_egd')          | 0.0095 | 0.0035 | 0.0113 |     0.0023 |     0.0166 | 0.95   |
| ('E4 K + egd per kohort', 'tidlig_post')       | 0.0316 | 0.0033 | 0      |     0.0249 |     0.0382 | 3.2063 |
| ('E4 K + egd per kohort', 'sent_dose')         | 0.0373 | 0.0032 | 0      |     0.0306 |     0.0439 | 3.7956 |
| ('E1 K + bestilt×egd', 'bestilt_egd')          | 0.0143 | 0.0036 | 0.0005 |     0.0069 |     0.0217 | 1.4373 |
| ('E1 K + bestilt×egd', 'tidlig_post')          | 0.0324 | 0.0033 | 0      |     0.0256 |     0.0393 | 3.2972 |
| ('E1 K + bestilt×egd', 'sent_post')            | 0.0191 | 0.0065 | 0.0069 |     0.0057 |     0.0325 | 1.9294 |
| ('E1 K + bestilt×egd', 'sent_dose')            | 0.0138 | 0.0069 | 0.0556 |    -0.0004 |     0.0281 | 1.3944 |
| ('E1 K + dose_lead', 'tidlig_post')            | 0.0315 | 0.0032 | 0      |     0.0249 |     0.0381 | 3.1984 |
| ('E1 K + dose_lead', 'sent_post')              | 0.0126 | 0.0081 | 0.134  |    -0.0041 |     0.0293 | 1.2676 |
| ('E1 K + dose_lead', 'sent_dose')              | 0.0198 | 0.0096 | 0.049  |     0.0001 |     0.0396 | 2.003  |
| ('E1 K + dose_lead', 'sent_dose_lead')         | 0.0016 | 0.0081 | 0.8495 |    -0.0152 |     0.0183 | 0.1561 |
| ('E4 K + dose_lead', 'tidlig_post')            | 0.0311 | 0.0032 | 0      |     0.0246 |     0.0377 | 3.163  |
| ('E4 K + dose_lead', 'sent_dose')              | 0.0072 | 0.016  | 0.6565 |    -0.0257 |     0.0401 | 0.7227 |
| ('E4 K + dose_lead', 'sent_dose_lead')         | 0.027  | 0.015  | 0.0838 |    -0.0039 |     0.0578 | 2.7349 |
| ('E1 K + sep 2025 per kohort', 'tidlig_sep25') | 0.0049 | 0.0026 | 0.0645 |    -0.0003 |     0.0102 | 0.4935 |
| ('E1 K + sep 2025 per kohort', 'sent_sep25')   | 0.0035 | 0.0022 | 0.1171 |    -0.0009 |     0.008  | 0.3534 |

## 3b. Sent-gruppens avvik fra tidlig-gruppen månedene før ordningen (apr–sep 2025) og etter, FE_K-ramme, prosent
| maned   |   sent |   tidlig |   diff_sent_tidlig |
|:--------|-------:|---------:|-------------------:|
| 2025-04 |  -0.46 |    -0.84 |               0.37 |
| 2025-05 |   0.45 |    -0.03 |               0.48 |
| 2025-06 |   0.22 |    -0.28 |               0.5  |
| 2025-07 |   0.36 |     0.22 |               0.14 |
| 2025-08 |   0.36 |     0.11 |               0.25 |
| 2025-09 |   0.35 |     0.49 |              -0.14 |
| 2025-10 |   0.81 |     1.1  |              -0.29 |
| 2025-11 |   1.56 |     1.98 |              -0.42 |
| 2025-12 |   1.95 |     2.32 |              -0.37 |
| 2026-01 |   3.66 |     4.24 |              -0.58 |
| 2026-02 |   4.48 |     4.98 |              -0.51 |
| 2026-03 |   3.82 |     4.03 |              -0.22 |
| 2026-04 |   3.43 |     3.33 |               0.1  |
Sent apr–sep 2025: snitt 0.21 prosent, maks |t| 1.99

## Wild cluster bootstrap (s14): p-verdier og KI som tåler 27 og 9 klustre

# Wild cluster bootstrap av DiD-estimatene

Restringert wild cluster bootstrap (WCR), B = 999, seed 1, klustre g = område | status | EAC.
Spesifikasjonene er identiske med s12 (D-modellene) og s13 (E-modellene). Kolonnene `koef`,
`se_cluster` og `p_cluster_t` er statsmodels' WLS med CR1 og t(G−1); `p_wcb` og
`ki_wcb_*` kommer fra bootstrappen. p-verdien har oppløsning 1/999, slik at 0,0000
betyr p < 0,001. Konfidensintervallet er funnet ved å invertere testen på et rutenett
med 41 nullverdier over estimat ± 4 standardfeil.

Referanser: Cameron, Gelbach og Miller (2008); MacKinnon og Webb (2018). For modellene
med ni klustre rapporteres både Rademacher- og Webb-vekter, siden Rademacher bare gir
2^9 = 512 distinkte vektvektorer.

| modell                                  | term         |     koef |      pst |   se_cluster |   p_cluster_t |   p_wcb |   ki_wcb_lav |   ki_wcb_hoy |   G | vekttype   |   B |
|:----------------------------------------|:-------------|---------:|---------:|-------------:|--------------:|--------:|-------------:|-------------:|----:|:-----------|----:|
| D7 område×måned×EAC-FE + sesong per EAC | bestilt_post |  0.02988 |  3.03314 |      0.00284 |       0       |   0.001 |      0.02423 |      0.0366  |  27 | rademacher | 999 |
| D7 tidlig/sent                          | tidlig_post  |  0.03094 |  3.14279 |      0.00299 |       0       |   0.001 |      0.02507 |      0.03761 |  27 | rademacher | 999 |
| D7 tidlig/sent                          | sent_post    |  0.02861 |  2.90234 |      0.0032  |       0       |   0.001 |      0.02208 |      0.03548 |  27 | rademacher | 999 |
| D7 placebo okt 2024                     | bestilt_post | -0.0019  | -0.18975 |      0.00124 |       0.139   |   0.14  |     -0.00416 |      0.00104 |  27 | rademacher | 999 |
| E1 sesong per kohort                    | sent_post    |  0.0131  |  1.31884 |      0.00756 |       0.095   |   0.09  |     -0.00186 |      0.02817 |  27 | rademacher | 999 |
| E1 sesong per kohort                    | sent_dose    |  0.02092 |  2.11437 |      0.00915 |       0.03066 |   0.015 |      0.00477 |      0.03923 |  27 | rademacher | 999 |
| E4 sesong per kohort, sent kun via dose | sent_dose    |  0.03642 |  3.70917 |      0.00343 |       0       |   0.001 |      0.03007 |      0.04342 |  27 | rademacher | 999 |
| E6 Husholdning Høy (9 klustre)          | tidlig_post  |  0.02357 |  2.38522 |      0.0028  |       3e-05   |   0.033 |      0.01251 |      0.03464 |   9 | rademacher | 999 |
| E6 Husholdning Høy (9 klustre)          | tidlig_post  |  0.02357 |  2.38522 |      0.0028  |       3e-05   |   0.021 |      0.01251 |      0.03464 |   9 | webb       | 999 |
| E6 Husholdning Høy (9 klustre)          | sent_dose    |  0.00637 |  0.6386  |      0.00966 |       0.52855 |   0.398 |     -0.01594 |      0.04261 |   9 | rademacher | 999 |
| E6 Husholdning Høy (9 klustre)          | sent_dose    |  0.00637 |  0.6386  |      0.00966 |       0.52855 |   0.407 |     -0.01525 |      0.0407  |   9 | webb       | 999 |
| E6 Husholdning Lav (9 klustre)          | tidlig_post  |  0.04256 |  4.34838 |      0.00527 |       4e-05   |   0.022 |      0.02509 |      0.06292 |   9 | rademacher | 999 |
| E6 Husholdning Lav (9 klustre)          | tidlig_post  |  0.04256 |  4.34838 |      0.00527 |       4e-05   |   0.038 |      0.02176 |      0.06337 |   9 | webb       | 999 |
| E6 Husholdning Lav (9 klustre)          | sent_dose    |  0.04098 |  4.18349 |      0.014   |       0.01908 |   0.082 |     -0.0143  |      0.09129 |   9 | rademacher | 999 |
| E6 Husholdning Lav (9 klustre)          | sent_dose    |  0.04098 |  4.18349 |      0.014   |       0.01908 |   0.089 |     -0.0143  |      0.09239 |   9 | webb       | 999 |
| E6 Husholdning Medium (9 klustre)       | tidlig_post  |  0.02853 |  2.8945  |      0.00274 |       1e-05   |   0.003 |      0.02486 |      0.03424 |   9 | rademacher | 999 |
| E6 Husholdning Medium (9 klustre)       | tidlig_post  |  0.02853 |  2.8945  |      0.00274 |       1e-05   |   0.015 |      0.02486 |      0.03423 |   9 | webb       | 999 |
| E6 Husholdning Medium (9 klustre)       | sent_dose    |  0.02229 |  2.25436 |      0.01364 |       0.14093 |   0.115 |     -0.0144  |      0.05846 |   9 | rademacher | 999 |
| E6 Husholdning Medium (9 klustre)       | sent_dose    |  0.02229 |  2.25436 |      0.01364 |       0.14093 |   0.108 |     -0.01426 |      0.06269 |   9 | webb       | 999 |
| D6 Husholdning Høy (9 klustre)          | bestilt_post |  0.02391 |  2.41958 |      0.00265 |       2e-05   |   0.025 |      0.01341 |      0.0344  |   9 | rademacher | 999 |
| D6 Husholdning Høy (9 klustre)          | bestilt_post |  0.02391 |  2.41958 |      0.00265 |       2e-05   |   0.029 |      0.01341 |      0.0344  |   9 | webb       | 999 |
| D6 Husholdning Lav (9 klustre)          | bestilt_post |  0.03831 |  3.90522 |      0.0044  |       2e-05   |   0.001 |      0.02923 |      0.0504  |   9 | rademacher | 999 |
| D6 Husholdning Lav (9 klustre)          | bestilt_post |  0.03831 |  3.90522 |      0.0044  |       2e-05   |   0.003 |      0.02846 |      0.05045 |   9 | webb       | 999 |
| D6 Husholdning Medium (9 klustre)       | bestilt_post |  0.02557 |  2.58962 |      0.00297 |       3e-05   |   0.001 |      0.01486 |      0.03321 |   9 | rademacher | 999 |
| D6 Husholdning Medium (9 klustre)       | bestilt_post |  0.02557 |  2.58962 |      0.00297 |       3e-05   |   0.006 |      0.01498 |      0.0334  |   9 | webb       | 999 |

## Sanity-sjekk: p-fordeling når nullhypotesen er sann
Utfallet konstrueres på nytt i D7-rammen: y = tilpasset verdi uten bestilt_post + støy med
klusterkomponent (klusterspesifikt nivå + AR-fri idiosynkratisk ledd), skalert til samme
residualspredning som i den virkelige modellen. Sann effekt er null. 200 simuleringer,
B = 199 per simulering (av kjøretidshensyn); rapporterer andel p < 0,05 for klusterrobust
t-test og for WCR.
Simuleringer: 200, kjøretid 109.3 s
- Klusterrobust t(G−1): andel p < 0,05 = 0.055; p < 0,10 = 0.085
- WCR (Rademacher, B = 199): andel p < 0,05 = 0.050; p < 0,10 = 0.090
- Kolmogorov–Smirnov mot uniform for WCR-p: D = 0.085, p = 0.105
- Desilfordeling av WCR-p (forventet 0,10 i hver):
|       |   0.0–0.1 |   0.1–0.2 |   0.2–0.3 |   0.3–0.4 |   0.4–0.5 |   0.5–0.6 |   0.6–0.7 |   0.7–0.8 |   0.8–0.9 |   0.9–1.0 |
|:------|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|
| andel |      0.09 |      0.09 |      0.12 |      0.08 |     0.115 |     0.105 |      0.06 |      0.09 |      0.07 |      0.18 |

## Tolkning

- Hovedestimatet i D7 (bestilt_post) er 0,0299 i logaritmer, 3,03 prosent. p fra klusterrobust t er 0,000, p fra WCR 0,001. Konklusjonen om at bestillerne bruker mer strøm etter innføringen overlever bootstrappen.
- I D7 tidlig/sent er tidlig_post 3,14 prosent (p_t 0,000, p_wcb 0,001) og sent_post 2,90 prosent (p_t 0,000, p_wcb 0,001).
- Placeboen (konstruert reform okt. 2024, kun førperioden) gir −0,19 prosent med p_t 0,1390 og p_wcb 0,140. Placeboen er ikke signifikant i noen av testene.
- I E1 (sesong per kohort) er sent_post 1,32 prosent med p_t 0,0950 og p_wcb 0,090; sent_dose er 0,0209 med p_t 0,0307 og p_wcb 0,015. E4, der sent-effekten kun går via dose, gir sent_dose 0,0364 med p_t 0,000 og p_wcb 0,001.
- I per-EAC-modellene (ni klustre) er forskjellen mellom t-testen og bootstrappen størst. Av 12 rader i E6 er 8 signifikante på 5 prosent med klusterrobust t, mot 6 med WCR. For D6 er tallene 6 mot 6 av 6.
- Rademacher- og Webb-vekter gir samme kvalitative bilde i ni-klustermodellene. Webb er å foretrekke her: med ni klustre gir Rademacher bare 512 distinkte vektvektorer, og p-verdien blir grovt diskretisert.
- Sanity-sjekken viser at den klusterrobuste t-testen forkaster i 0,055 av tilfellene når nullhypotesen er sann, mot nominelle 0,050, mens WCR forkaster i 0,050. Kolmogorov–Smirnov-testen mot uniform fordeling for WCR-p gir p = 0,105.
- Bredden på bootstrapintervallet delt på t(G−1)-intervallet: 0.74–1.72; videre i 20 av 25 rader, smalere i 5. Der p_wcb og p_cluster_t havner på hver sin side av 0,05, er det bootstrappen som gjelder.
- se_cluster/p_cluster_t i tabellen er statsmodels-verdier (K = alle kolonner i CR1-korreksjonen); WCB bruker K = antall estimerte parametre (rang), som gir 1 prosent lavere se. Bootstrap-p og -KI er beregnet med sistnevnte.
- Sanity-sjekken er kjørt med homoskedastisk støy og balanserte klustre for G = 27, der også t-testen er riktig dimensjonert. Den viser at WCR er riktig implementert, ikke at den korrigerer noe; tilfellet G = 9 med ubalanserte klustre er ikke simulert.


## Effektiv marginalpris med strømstøtte (s15) og NRK-like modeller på effektiv pris

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


## Verifisering av kommune→prisområde (s16, sekundærkilde VG)

# Verifisering av kommune -> prisområde (oppgave C)

Hentet/sjekket: 2026-09-05. Skript: `src/s16_verifiser_prisomrade.py`. Endrer ikke `src/geo.py` eller panelet – kun rapportering.

## Metode og kilder

Det finnes ingen offisiell, maskinlesbar tabell kommune->prisområde i Norge (prisområder følger overføringsnettets kapasitetsgrenser, ikke administrative kommunegrenser). Tre maskinlesbare kandidater ble undersøkt og forkastet:

1. **Elhub** (data.elhub.no): `consumption_per_group_municipality_hour` har KOMMUNE/KOMMUNENUMMER, `consumption_per_group_mba_hour` har PRISOMRÅDE – men dette er to separate nedbrytninger uten felles rad-nøkkel. Elhub publiserer ikke en egen kommune<->prisområde-koblingstabell (sjekket i datakatalogen, https://dok.elhub.no/data/Datasett.835354661.html, 05.09.2026).
2. **NVE Atlas / GIS3** (`https://gis3.nve.no/map/rest/services/Mapservices/Elspot/MapServer/0`, lag `ElSpot_omraade`): tjenesten svarte `{"error":{"code":500,"message":"Service Mapservices/Elspot/MapServer not started "}}` ved gjentatte forsøk 05.09.2026 – ikke i drift. Domenet `nve.geodataonline.no` som også dukket opp i søk finnes ikke (DNS-oppslag feiler).
3. **Geonorge/Statnett/RME**: ingen ferdig nedlastbart GIS-lag eller CSV med kommune<->prisområde ble funnet innenfor rimelig søkeinnsats.

Kilden som faktisk ble brukt er **VGs «Strømprisen»** (`https://www.vg.no/stromprisen/kommune/<kommune>/`), som for hver norsk kommune oppgir en entydig kobling «Kommune: <navn> (NOx)». Siden oppgir selv kildene **Statnett, Nasdaq, Nord Pool, NVE, Entsoe og Enova**. Dette er en redaksjonell/sekundær kilde, ikke en offisiell forskrift eller et primært register – men den bygger uttalt på de samme primærkildene (Statnett/NVE) som resten av norsk kraftprisjournalistikk, og er uavhengig konstruert av geo.py sin NVE-kraftverk-baserte kobling. VG-siden advarer selv eksplisitt: «Noen områder langs regiongrensene får strøm fra en annen region enn resten av kommunen. Sjekk gjerne med din strømleverandør hvilken region du tilhører.» – dvs. VG bekrefter at prisområde-grensen ikke alltid følger kommunegrensen eksakt (se eget avsnitt under).

Alle 27 overstyrte kommuner (pa_kilde="nve" i `tab_kommune_prisomrade.csv`) og de 2 manuelle unntakene (pa_kilde="unntak": Bømlo, Sveio) ble sjekket enkeltvis i nettleser 05.09.2026 – se URL-liste i `tab_prisomrade_verifisering.csv`. Siden er en client-rendered SvelteKit-app uten stabilt offentlig API; oppslagene ble derfor gjort manuelt (én per kommune), IKKE med et automatisert nedlastingsskript. De 99 kommunene med ren fylkesregel (pa_kilde="fylke") og de 229 der fylke og NVE er enige (pa_kilde="fylke=nve") er IKKE sjekket mot VG i denne runden (for stort omfang for manuell sjekk) – kontrollen er avgrenset til de kommunene der geo.py faktisk overstyrer eller gjør unntak, som er de eneste med reell risiko for feil.

## Resultat

- Sjekket: 29 kommuner (27 NVE-overstyringer + 2 manuelle unntak)
- Samsvar med VG: **28**
- Avvik: **0**
- Ikke verifisert (fant ingen VG-side): **1**
- Herav i panelet (`data/processed/panel.parquet`, 197 kommuner NO1/NO2/NO5): **12**

### Avvik

Ingen avvik funnet: alle 28 kommuner som ble bekreftet mot VG stemmer overens med `tab_kommune_prisomrade.csv`.

### Ikke verifisert

|   knr | kommune   | var_pa   | var_pa_kilde   |
|------:|:----------|:---------|:---------------|
|  3437 | Sel       | NO3      | nve            |

Sel (3437) ga 404 på VGs kommune-URL (både «sel» og «sel-kommune» ble forsøkt 05.09.2026); ikke lykkes å få tak i riktig URL-slug innenfor rimelig innsats. Indirekte støtte: Sel ligger midt i Nord-Gudbrandsdal, og alle de fem nabokommunene i samme NVE-overstyrte gruppe (Dovre, Lesja, Skjåk, Lom, Vågå) er bekreftet NO3 mot VG, og NVEs egen regionbeskrivelse (sitert i søk 05.09.2026) plasserer eksplisitt «Innlandet vest og nord for Vågåmo» i NO3 – som også omfatter Sel. `prisomrade=NO3` for Sel i `tab_kommune_prisomrade.csv` anses derfor som sannsynlig riktig, men er ikke direkte bekreftet mot en uavhengig kilde.

## De 12 overstyrte/unntaks-kommunene som faktisk inngår i panelet

Av de 29 sjekkede kommunene er det disse 12 som har prisområde NO1/NO2/NO5 og dermed faktisk påvirker analysen i `data/processed/panel.parquet` (resten – NO3/NO4 – er utenfor NRK/OEs analyseområde):

|   knr | kommune   | var_pa   | var_pa_kilde   | samsvar   |
|------:|:----------|:---------|:---------------|:----------|
|  3320 | Flå       | NO5      | nve            | samsvar   |
|  3322 | Nesbyen   | NO5      | nve            | samsvar   |
|  3324 | Gol       | NO5      | nve            | samsvar   |
|  3326 | Hemsedal  | NO5      | nve            | samsvar   |
|  3328 | Ål        | NO5      | nve            | samsvar   |
|  3330 | Hol       | NO5      | nve            | samsvar   |
|  4611 | Etne      | NO2      | nve            | samsvar   |
|  4612 | Sveio     | NO2      | unntak         | samsvar   |
|  4613 | Bømlo     | NO2      | unntak         | samsvar   |
|  4614 | Stord     | NO2      | nve            | samsvar   |
|  4615 | Fitjar    | NO2      | nve            | samsvar   |
|  4616 | Tysnes    | NO2      | nve            | samsvar   |

## Kommuner delt mellom prisområder

VGs egen tekst på forsiden av Strømprisen (https://www.vg.no/stromprisen/, hentet 2026-09-05) sier eksplisitt: «Noen områder langs regiongrensene får strøm fra en annen region enn resten av kommunen. Sjekk gjerne med din strømleverandør hvilken region du tilhører.» Dette bekrefter at prisområde-grensen ikke alltid følger kommunegrensen eksakt – men VG oppgir ingen liste over hvilke kommuner dette gjelder, og det ble ikke funnet noen slik liste hos NVE/Statnett/RME innenfor søkeinnsatsen i denne runden. `src/geo.py` sin egen NVE-kraftverk-kobling har samme svakhet innebygd: når et kraftverk-datasett gir `n_omrader > 1` for en kommune (flere kraftverk i forskjellige prisområder), faller koblingen tilbake til fylkesregelen i stedet for å velge riktig område for forbrukssiden – se `nve_area_by_name()` i geo.py (`pa_nve == "flere"` behandles ikke som entydig). Ingen av de 197 kommunene i panelet er identifisert som delt i denne runden, men muligheten er ikke uttømmende utelukket.

## Hva som IKKE ble verifisert

- De 99 kommunene med ren fylkesregel og de 229 der fylke og NVE-kobling er enige (`pa_kilde` i {"fylke", "fylke=nve"}) – ikke sjekket mot en uavhengig kilde i denne runden.
- Sel (3437), se over.
- Om noen av de 197 panelkommunene er reelt delt mellom to prisområder (VGs grenseadvarsel over) – ingen autoritativ liste funnet.
- VGs egen kobling er ikke en offisiell/forskriftsmessig kilde; den er inkludert fordi den er den eneste kommune-for-kommune-kilden som faktisk ble funnet, og fordi den er uavhengig av NVE-kraftverk-metoden i geo.py. Den bør behandles som en sterk, men ikke endelig, bekreftelse.


## Nettoeksport fra SSB elektrisitetsbalanse (s17), NRK P4

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


## Åpne punkter før tallene kan brukes

- Skjæringsdato tidlig/sent: LØST (Elhub-wiki: tidlig = bestilt t.o.m. 01.10.2025, sent = 02.10.2025–30.04.2026; Norgespris gjelder fra bestillingsdagen). Dose-respons i s13; forenlig med behandlingseffekt, ikke avgjort (KRITIKK3). Gjenstår: kohortens inntredelsesforløp fra Elhub.
- Prisområde: 28 av 29 overstyrte kommuner bekreftet mot VG (sekundærkilde); Sel ikke slått opp; ingen offisiell liste funnet. Delte kommuner ikke utelukket.
- Effektiv marginalpris: gjort (s15). Parameter april–mai 2023 (80 prosent) svakere belagt, se kilder/stromstotte_parametre.md.
- Wild cluster bootstrap: gjort (s14). E6 Lav sent_dose overlever ikke (p 0,08–0,09); øvrige hovedtermer overlever.
- Nettoeksport: gjort (s17, SSB 14091, hele landet). Fall 10 168 GWh mot forbruksøkning 2 323 GWh i Sør-Norge; produksjonsfall 6 379 GWh.
- Må bestilles eksternt: kohortens inntredelsesforløp og døgnstart 1. oktober (Elhub), NRKs spesifikasjon (NRK). Se notat/SPORSMAL_ELHUB_NRK.md.
- Panelet mangler 2021 (Elhubs kommunefil starter feb. 2022) og slutter apr. 2026 (NRK: juni 2026).
## 20.09.2026 – timebasert test av prismekanismen (s20, Codex' design på fulle data)

Gap = log kWh per måler tidlig bestilt minus ikke bestilt, per time og stratum (9). Førperiodemodell per stratum: time i uken, kalendermåned, kubisk oppvarmingsgrad (Open-Meteo, base 17), kubisk log last hos ikke-bestillere. Prediksjonsavvik i vinteren regressert på prisfordel = effektiv marginalpris med strømstøtte (terskel 73/75/77 øre eks. mva 2024/25/26, 90 prosent dekning) minus 40 øre.

| Størrelse | Verdi |
|---|---:|
| Helning, vinter 2025/26, log-pp per kr/kWh | 5,09 |
| Helning, placebovinter 2024/25 | −1,32 |
| Differanse (uke-blokkbootstrap 95 %) | 6,41 (5,26–7,82) |
| Differanse uten kontroll for ikke-bestillernes last | 7,10 |
| Nivåeffekt, justert, minus placebo, prosent | 2,81 (2,35–3,26) |
| Dosekomponent ved snittfordel 34,9 øre, prosent | 2,26 |
| Observasjoner (time × stratum) | 45 792 / 45 786 |
| Andel i intervallet 25–50 øre, vinter 2025/26 | 39 651 av 45 792 |

Identisk med Codex' tall (verifisering/codex_ekstern/norgespris_hourly_results.json). Filer: output/tab_timetest_resultater.json, tab_timetest_prisfordel_bin.csv, fig_timetest_dose_respons.png, log_s20.txt.

## 21.09.2026 – magasin og utveksling (s21)

Uke 37 2026: fyllingsgrad hele landet 64,3 prosent (median 82,5), NO2 46,9 (median 83,0, NVE-min 50,9), NO5 64,9, NO1 72,5. Avvik fra median: −16,0 TWh landet, −16,8 TWh Sør-Norge. Fall uke 37 2025→2026: −12,2 TWh landet, −9,1 Sør.
Elbalanse jan–jul 2026 mot snitt 2021–2025 (SSB 14091, TWh): produksjon −3,0; import +4,0; eksport −3,7; nettoeksport −7,7 (2,7 mot 10,4); bruttoforbruk +4,7; husholdninger +2,4. Nettoimport feb–apr 2026. Statnett jan–aug: forbruk +6,2, produksjon −2,5.
Husholdninger kalenderår: 42,8 TWh 2021, 40,4 TWh 2025 (SSB); Elhub okt 25–sep 26 under 2021 i alle områder.
Kilder og filer: notat/MAGASIN_EKSPORT_2026-09-21.md, output/tab_magasin_eksport.md.

## 21.09.2026 – tilsig (NVE Kraftsituasjonen veke 37, tabell 4 og 5)

Tilsig uke 1–37 2026 (TWh, avvik fra snitt 2006–2025): Norge 84,2 (−21,6); Sør-Norge NO1+NO2+NO5 55,7 (−12,7); NO1 11,1 (−1,3); NO2 25,1 (−6,2); NO5 19,5 (−5,2). 2025: Norge 100,3 (−6,2); Sør 66,0 (−3,0). Nedbør Sør 2026 41,4 (−12,4). Hydrologisk balanse 2026: Norge −14,7 (magasin −13,9, snø/grunn/markvann −0,8); Sør −15,4 (magasin −14,4, snø/grunn/markvann −1,0); 2025 Sør −3,8. Tall lest manuelt fra pdf-tabeller (tekstuttrekk i .txt ved siden av). Fil: output/tab_tilsig_uke37.csv.

## 22.09.2026 – ettergåing av Moxnes' Facebook-innlegg etter Helgemorgen

SSB 14091 årssummer 2010–2026 (TWh): output/tab_elbalanse_aar_2010_2026.csv (2026 = jan–aug). Husholdninger (7.4, finnes fra 2020): 2020 40,5; 2021 42,8; 2022 37,8; 2023 40,4; 2024 40,9; 2025 40,4 (−1,1 prosent mot 2024). Nettoeksport: 2020 20,5; 2021 17,6; 2022 12,5; 2023 17,7; 2024 18,4; 2025 22,8; 2026 jan–aug 3,2. Eksport 2021 25,8 mot 25,0 i 2020.
SSB 09387 kraftpris husholdninger ekskl. mva (øre/kWh), uveid snitt av kvartaler: 2012–2020 33,4; 2012–2017 30,7; 2018–2020 38,8; 2021 72,2; 2022 156,3; 2023 80,5; 2024 56,1; 2025 64,1; 2026K1–K2 109,9. Tabellen starter 2012, så 2010–2011 er ikke kontrollert.
Ikke kontrollert: Enova 15 mrd, produksjonskost 12 øre, kabelkapasitet +50 prosent.

## 23.09.2026 – NRKs svar: fritidsboliger (Elhub cons_mba, NO1+NO2+NO5)

Kommunefilen fra Elhub har bare gruppen «Privat» (husholdning + hytte); NRK-lik modell M1 (10 prosent) og placebo M5 (5 prosent) er derfor kjørt på samme populasjon som NRK. Statusdataene (D7, 3,0 prosent) gjelder husholdninger 1 000–50 000 kWh, uten hytter.
GWh jan–jun: Husholdning 2025 14 883, 2026 17 006 (+14,3 prosent); Hytter 913 → 1 113 (+22,0). Vinter okt–apr 24/25 → 25/26: Husholdning 19 832 → 21 775 (+9,8); Hytter 1 242 → 1 439 (+15,9). Hytter er 5,8–6,2 prosent av Privat-volumet. Bidrag fra hytter til Privat-veksten jan–jun: om lag 0,5 prosentpoeng (0,06 × 22 mot 0,06 × 14,3).
Norgespris-andel 02.09.2026: Husholdning 68,9 prosent (1 388 366 av 2 013 777), Hytter 79,7 prosent (212 639 av 266 765).

## 23.09.2026 – hytter i NRK-lik modell (kommunepanel, M1-oppsett, uveid over kommuner)

Hytteandel av private målere per kommune (Elhub målerfil 02.09.2026): median 20,2 prosent, kvartiler 9,4 og 34,6, maks 84,2. Hytter er 6 prosent av volumet, men 20 prosent av målerne.
M1 + post×(hytteandel − median): post_np 0,0892, post×hytteandel 0,1184 (se 0,0285). Delutvalg: alle 197 kommuner 10,0 prosent (placebo 5,2); lav hytteandel (99 kommuner) 8,7 (5,0); høy hytteandel (98) 11,2 (5,4); hytteandel under 5 prosent (36 kommuner) 8,8 (5,4).
Tolkning: hytter trekker NRK-lik post-effekt opp med 1–2 prosentpoeng på kommunenivå; placeboen er om lag 5 prosent i alle delutvalg og er uavhengig av hyttene.

## 23.09.2026 – tverrsnitt: vinterendring i privatforbruk mot hytteandel (197 kommuner, OLS, HC1)

Utfall: 100 × log-endring i kWh (Privat) okt–apr. Hytteandel = hytter av private målere 02.09.2026, i prosent (median 21,3).
Etter norgespris (25/26 mot 24/25): helning 0,076 (se 0,029, p 0,010), konstant 8,73, R2 0,02; med gradtallsendring uendret. Placebo (24/25 mot 23/24): helning −0,008 (se 0,006, p 0,22); med gradtall −0,014 (p 0,02). Snitt endring: +10,7 etter, −8,8 før.
Kvartiler (median hytteandel → endring etter / før): 2,7 → 8,9 / −9,0; 13,9 → 9,8 / −9,0; 27,8 → 9,9 / −7,6; 57,6 → 14,2 / −9,6. Fil: output/tab_hytteandel_kommune_vinter.csv.

## 23.09.2026 – s22: robust panelregresjon, post × hytteandel (197 kommuner, 2022-02–2026-04, klustret på kommune)

Prosent høyere privatforbruk etter okt. 2025 per 10 prosentpoeng høyere hytteandel (placebo med falsk start okt. 2024 i parentes):
H1 kommune + år×måned-FE 1,37 (0,01); H2 + prisområde×måned 1,42 (0,00); H3 + kommune×kalendermåned 0,41, p 0,10 (−0,15); H4 + gradtall×kommune 0,43, p 0,09 (−0,08); H5 + post×kommunekjennetegn 0,63, p 0,02 (−0,17); H6 + kommunetrend 0,84, p 0,005 (0,06); H7 H5 vektet med målere 0,38, p 0,12 (−0,21).
Forløp (H4, ref. sesong 2024/25, per 10 pp): 2021/22 (feb–sep 2022) 0,28; 22/23 −0,03; 23/24 0,07; 25/26 (okt–apr) 0,47.
NRK-lik M1 med post × hytteandel: 6,6 prosent ved 0 hytter (lineær ekstrapolasjon), 9,9 prosent ved snitt hytteandel 26,0 pp. Faktiske kommuner med under 5 prosent hytter: 8,8 prosent (tidligere kjøring).
Filer: output/tab_hytteandel_robust.csv, tab_hytteandel_forlop.csv, tab_hytteandel_nrk_m1.csv.

Forklaringskraft s22 (R2 / justert R2 / R2 for regressorene etter at faste effekter er fjernet; antall absorberte parametre): H1 0,9970 / 0,9969 / 0,247 (247); H2 0,9972 / 0,9971 / 0,157 (349); H3 0,9988 / 0,9984 / 0,018 (2 712); H4 0,9988 / 0,9984 / 0,005 (2 909); H5 0,9989 / 0,9984 / 0,021 (2 909); H6 0,9992 / 0,9988 / 0,026 (3 106); H7 (vektet) 0,9997 / 0,9996 / 0,036 (2 909). N 10 047. NRK-lik M1: R2 innen kommune 0,9416 (NRK oppgir 93,76 prosent), R2 med kommune-FE 0,9938, justert 0,9936, R2 mellom kommuner 0,130.

Målervektet (23.09.2026): hytteandel i panelet uvektet 26,0 prosent, vektet med målere 11,6 prosent. H7 (vektet): 0,38 prosent per 10 pp, bidrag 0,44 pp (95 prosent: −0,12 til 0,99), placebo −0,21 (p 0,03). H7 + egen trend per kommune: 0,60 prosent per 10 pp (p 0,015), bidrag 0,70 pp (0,14 til 1,26), placebo 0,00 (p 0,97). Retter tidligere tabell i chat: vektet bidrag er 0,4–0,7 pp, ikke 1,0.
