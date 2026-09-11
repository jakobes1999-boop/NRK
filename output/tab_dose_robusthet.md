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