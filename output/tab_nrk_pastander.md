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