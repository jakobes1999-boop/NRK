# Spesifikasjonssøk mot NRKs koeffisienter

Alle tall er **til godkjenning**. Kilde for målene: NRKs metodeboks (`kilder/nrk_prisen_for_billig_strom.md`, linje 251–285): energigradtall 0,0019, spotpris −0,0005, Norgespris 0,0822, medianinntekt 0,0024, R² 93,76 prosent.

Panel: 197 kommuner, 2022-02–2026-04. 784 kjernemodeller × enhetsvalg = 6384 kjøringer.

Avstand = sum av relative avvik på de fire koeffisientene + relativt avvik i beste R²-variant.

## Topp 15 nærmeste spesifikasjoner

| # | y | Norgespris | tids-FE | areal | inntekt | spot | vekting | utvalg | egd | spot | np | innt | R² (variant) | avstand |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | log_kwh_per_maler | post_okt2025 | ingen | med | lineaer/10000_kr | ore_per_kwh | n_mp | egd_kommunestasjon | 0,00187 | −0,00035 | 0,0753 | 0,00317 | 0,9608 (r2_within) | 0,745 |
| 2 | log_kwh_per_maler | post_okt2025 | ingen | uten | lineaer/10000_kr | ore_per_kwh | n_mp | egd_kommunestasjon | 0,00187 | −0,00035 | 0,0755 | 0,00320 | 0,9608 (r2_within) | 0,756 |
| 3 | log_kwh_per_maler | post_okt2025 | ingen | med | lineaer/10000_kr | ore_per_kwh | n_mp | pa_entydig | 0,00186 | −0,00035 | 0,0743 | 0,00338 | 0,9593 (r2_within) | 0,854 |
| 4 | log_kwh_per_maler | post_okt2025 | ingen | uten | lineaer/10000_kr | ore_per_kwh | n_mp | pa_entydig | 0,00186 | −0,00035 | 0,0746 | 0,00340 | 0,9593 (r2_within) | 0,859 |
| 5 | log_kwh | post_sep2025 | ingen | uten | lineaer/1000_kr | ore_per_kwh | uvektet | pa_entydig | 0,00190 | −0,00036 | 0,0800 | 0,00096 | 0,9354 (r2_within) | 0,907 |
| 6 | log_kwh | post_sep2025 | ingen | med | lineaer/1000_kr | ore_per_kwh | uvektet | pa_entydig | 0,00190 | −0,00036 | 0,0799 | 0,00096 | 0,9354 (r2_within) | 0,908 |
| 7 | log_kwh | post_sep2025 | ingen | uten | lineaer/1000_kr | ore_per_kwh | uvektet | alle | 0,00190 | −0,00035 | 0,0815 | 0,00092 | 0,9402 (r2_within) | 0,923 |
| 8 | log_kwh | post_sep2025 | ingen | med | lineaer/1000_kr | ore_per_kwh | uvektet | alle | 0,00190 | −0,00035 | 0,0814 | 0,00092 | 0,9402 (r2_within) | 0,926 |
| 9 | log_kwh_per_maler | post_sep2025 | ingen | med | lineaer/10000_kr | ore_per_kwh | n_mp | egd_kommunestasjon | 0,00188 | −0,00034 | 0,0649 | 0,00332 | 0,9603 (r2_within) | 0,952 |
| 10 | log_kwh | post_sep2025 | ingen | med | lineaer/1000_kr | ore_per_kwh | uvektet | egd_kommunestasjon | 0,00190 | −0,00037 | 0,0852 | 0,00083 | 0,9380 (r2_within) | 0,957 |
| 11 | log_kwh | post_sep2025 | ingen | uten | lineaer/1000_kr | ore_per_kwh | uvektet | egd_kommunestasjon | 0,00190 | −0,00037 | 0,0854 | 0,00083 | 0,9380 (r2_within) | 0,958 |
| 12 | log_kwh_per_maler | post_sep2025 | ingen | uten | lineaer/10000_kr | ore_per_kwh | n_mp | egd_kommunestasjon | 0,00188 | −0,00034 | 0,0651 | 0,00336 | 0,9602 (r2_within) | 0,968 |
| 13 | log_kwh | post_sep2025 | ingen | uten | lineaer/1000_kr | ore_per_kwh | uvektet | alle | 0,00188 | −0,00034 | 0,0789 | 0,00096 | 0,9391 (r2_within) | 0,977 |
| 14 | log_kwh | post_sep2025 | ingen | med | lineaer/1000_kr | ore_per_kwh | uvektet | alle | 0,00188 | −0,00034 | 0,0788 | 0,00096 | 0,9391 (r2_within) | 0,979 |
| 15 | log_kwh | post_okt2025 | ingen | med | lineaer/1000_kr | ore_per_kwh | uvektet | pa_entydig | 0,00189 | −0,00038 | 0,0938 | 0,00093 | 0,9363 (r2_within) | 1,004 |

## Beste treff per koeffisient (uansett øvrig spesifikasjon)

| Koeffisient | NRK | beste verdi | avvik | spesifikasjon |
|---|---|---|---|---|
| energigradtall | 0,00190 | 0,00190 | 0,0 prosent | log_kwh_per_maler, andel_husholdning, tids-FE aar, areal uten, inntekt log/log, spot ore_per_kwh, uvektet, pa_entydig, base17 |
| spotpris | −0,00050 | −0,00045 | 10,1 prosent | log_kwh, post_okt2025, tids-FE aar, areal uten, inntekt lineaer/kr, spot ore_per_kwh, uvektet, egd_kommunestasjon, base17 |
| Norgespris | 0,08220 | 0,08247 | 0,3 prosent | log_kwh_per_maler, andel_husholdning, tids-FE aar_x_mnd, areal med, inntekt log/log, spot kr_per_mwh, uvektet, alle, base17 |
| medianinntekt | 0,00240 | 0,00312 | 29,9 prosent | log_kwh_per_maler, andel_privat, tids-FE ingen, areal med, inntekt lineaer/10000_kr, spot ore_per_kwh, n_mp, egd_kommunestasjon, base17 |

## Hva hver dimensjon gjør med Norgespris-koeffisienten isolert

Basislinjen er M1-oppsettet; én dimensjon endres om gangen.

| Dimensjon | Verdi | koeffisient | endring vs. basis | R² within | R² OLS m/dummyer |
|---|---|---|---|---|---|
| (basislinje) | log kWh, 0/1 fra okt 2025, med bruksareal, inntekt lineær, ingen tids-FE, uvektet, alle kommuner | 0,0950 | 0,0000 | 0,9410 | 0,9937 |
| Venstreside | log_kwh_per_maler | 0,0840 | −0,0111 | 0,9408 | 0,9497 |
| Venstreside | kwh_nivaa | 817867,1929 | 817867,0978 | 0,1639 | 0,8825 |
| Venstreside | kwh_per_maler_nivaa | 85,9145 | 85,8195 | 0,8705 | 0,8878 |
| Norgespris-variabel | post_sep2025 | 0,0814 | −0,0137 | 0,9402 | 0,9936 |
| Norgespris-variabel | andel_privat | 0,1573 | 0,0623 | 0,9415 | 0,9938 |
| Norgespris-variabel | andel_husholdning | 0,1604 | 0,0654 | 0,9411 | 0,9937 |
| Tids-FE | mnd | 0,0717 | −0,0234 | 0,9623 | 0,9960 |
| Tids-FE | aar | 0,0923 | −0,0027 | 0,9424 | 0,9939 |
| Tids-FE (andel) | aar_x_mnd + andel_privat | 0,2408 | 0,1458 | 0,6331 | 0,9970 |
| Bruksareal | uten | 0,0952 | 0,0001 | 0,9410 | 0,9937 |
| Inntektsform | log | 0,0950 | −0,0001 | 0,9410 | 0,9937 |
| Vekting | n_mp | 0,0859 | −0,0091 | 0,9591 | 0,9973 |
| Utvalg | pa_entydig | 0,0938 | −0,0013 | 0,9363 | 0,9930 |
| Utvalg | egd_kommunestasjon | 0,0996 | 0,0045 | 0,9390 | 0,9937 |
| Gradtall | base18 | 0,0932 | −0,0019 | 0,9400 | 0,9936 |

## Koeffisientspenn per tids-FE (log-venstresider, spot i øre/kWh)

Viser hvilke tids-FE-valg som i det hele tatt kan gi NRKs nivåer.

| Tids-FE | egd | spot | Norgespris | R² within |
|---|---|---|---|---|
| aar | 0,00185 til 0,00191 | −0,00045 til −0,00040 | 0,0565 til 0,2142 | 0,9366 til 0,9633 |
| aar_x_mnd | 0,00068 til 0,00081 | −0,00012 til 0,00023 | 0,0683 til 0,3227 | 0,5684 til 0,6516 |
| ingen | 0,00184 til 0,00190 | −0,00040 til −0,00032 | 0,0642 til 0,1678 | 0,9353 til 0,9610 |
| mnd | 0,00106 til 0,00114 | −0,00027 til −0,00019 | 0,0481 til 0,1275 | 0,9578 til 0,9798 |

NRKs verdier: egd 0,0019, spot −0,0005, Norgespris 0,0822, R² 0,9376.

## Periodefølsomhet (M1-oppsettet, ulike delperioder)

NRK har 2021 og mai–juni 2026 i sitt datasett; vi har ikke kommunetall for disse månedene.

| Periode | N | egd | spot | inntekt (1 000 kr) | Norgespris | R² within |
|---|---|---|---|---|---|---|
| hele panelet | 10047 | 0,00188 | −0,00037 | 0,00090 | 0,0950 | 0,9410 |
| 2022-02–2024-12 (før Norgespris, ingen framskrevet inntekt) | 6895 | 0,00192 | −0,00037 | 0,00078 | ikke identifisert | 0,9481 |
| 2023-01–2026-04 | 7880 | 0,00189 | −0,00040 | 0,00146 | 0,0898 | 0,9417 |
| 2024-01–2026-04 | 5516 | 0,00186 | −0,00020 | absorbert | 0,0842 | 0,9391 |
| 2022-02–2025-09 (før Norgespris) | 8668 | 0,00191 | −0,00035 | 0,00093 | ikke identifisert | 0,9482 |

## Datadekning

- Elhubs kommunefil dekker 2022-02–2026-04. NRK oppgir 2021–juni 2026.
- Rådataene i `data/raw/` inneholder ikke kommunetall for 2021 eller mai–juni 2026, så perioden kan ikke utvides uten et nytt uttrekk.
