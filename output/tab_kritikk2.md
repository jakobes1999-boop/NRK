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