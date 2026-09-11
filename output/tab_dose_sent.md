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