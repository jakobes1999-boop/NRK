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
