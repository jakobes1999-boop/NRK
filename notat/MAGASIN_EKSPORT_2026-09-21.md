# Lave magasiner: eksport eller forbruk? Datagrunnlag og vurdering

Dato: 21.09.2026. Skript: `src/s21_magasin_eksport.py`. Tabeller: `output/tab_magasin_uke37.csv`, `tab_magasin_avvik_2026.csv`, `tab_elbalanse_aar.csv`, `tab_statnett_maned.csv`, sammenstilling i `tab_magasin_eksport.md`. Alle tall til godkjenning.

Bakgrunn: Bjørnar Moxnes hevder i en Facebook-video at de lave magasinene i Sør-Norge skyldes eksport, ikke forbruk, og at nordmenn ikke bruker mer strøm enn i 2021. Dette notatet legger fram tallene og vurderer påstandene. Norgespris-spørsmålet behandles ikke her.

## Kilder

| Kilde | Innhold | Dekning |
|---|---|---|
| NVE magasinstatistikk, åpent API | Fyllingsgrad og fylling i TWh per uke, hele landet og per prisområde, med NVEs median, min og maks per uke | 1995–uke 37 2026 |
| SSB tabell 14091 Elektrisitetsbalanse | Produksjon, import, eksport, bruttoforbruk, husholdningsforbruk per måned, hele landet | 2021–juli 2026 (hentet i s17) |
| Statnett driftsdata, nedlasting | Produksjon og forbruk per time; fysisk utveksling per time | 2021–sep. 2026; utveksling bare fra 2025 (2021–2024 er nullrader i kilden) |
| Elhub | Forbruk per kundegruppe og prisområde per måned | 2021–sep. 2026 (hentet i s01) |

Kontroll: Statnetts utveksling og SSBs nettoeksport avviker i snitt 6 GWh per måned i 2025–2026. Statnetts produksjon minus forbruk korrelerer 0,73 med SSBs nettoeksport over 67 måneder (forskjellen er nettap og pumpekraft).

## Magasinene

Fyllingsgrad uke 37, prosent av kapasitet:

| Område | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 | NVE-median | NVE-min |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Hele landet | 63,2 | 68,2 | 78,9 | 84,1 | 78,2 | 64,3 | 82,5 | 61,3 |
| NO1 | 72,1 | 68,5 | 92,2 | 99,0 | 80,6 | 72,5 | 88,9 | 68,5 |
| NO2 | 53,1 | 50,9 | 74,7 | 84,5 | 64,4 | 46,9 | 83,0 | 50,9 |
| NO5 | 55,6 | 70,2 | 89,5 | 91,4 | 80,2 | 64,9 | 84,9 | 55,6 |

I uke 37 2026 ligger hele landet 16,0 TWh under median og Sør-Norge (NO1, NO2, NO5) 16,8 TWh under. NO2 ligger under NVEs laveste registrerte verdi for uken. Sør-Norge har ligget under median hele 2026; hele landet lå over median i januar og falt under fra uke 18. Fra uke 37 2025 til uke 37 2026 falt fyllingen med 12,2 TWh i hele landet og 9,1 TWh i Sør-Norge. Bare 1996, 2006 og 2021 har hatt større fall i serien fra 1995.

## Elektrisitetsbalansen

TWh, hele landet, januar–juli:

| | Produksjon | Import | Eksport | Nettoeksport | Bruttoforbruk | Husholdninger |
|---|---:|---:|---:|---:|---:|---:|
| Snitt 2021–2025 | 90,7 | 6,9 | 17,3 | 10,4 | 80,4 | 24,0 |
| 2025 | 95,2 | 6,1 | 20,3 | 14,2 | 81,0 | 23,8 |
| 2026 | 87,7 | 11,0 | 13,7 | 2,7 | 85,0 | 26,4 |
| 2026 minus snitt | −3,0 | +4,0 | −3,7 | −7,7 | +4,7 | +2,4 |

Norge var nettoimportør i februar, mars og april 2026. Nettoeksporten januar–juli 2026 er den laveste i perioden 2021–2026, og en firedel av snittet. Statnetts timedata for januar–august gir samme bilde: forbruk 6,2 TWh over snittet for 2021–2025, produksjon 2,5 TWh under, produksjon minus forbruk 8,7 TWh under.

## Vurdering

**Påstand: nordmenn bruker ikke mer strøm enn i 2021.** Riktig for husholdningene målt per kalenderår: 42,8 TWh i 2021 (SSB) mot 40,4 TWh i 2025, og Elhubs tall for oktober 2025 til september 2026 ligger under 2021 i alle prisområder. 2021 var kaldt og lå før prissjokket. Påstanden er samtidig uten betydning for vinteren 2025/26, der husholdningsforbruket januar–juli var 2,4 TWh høyere enn snittet for 2021–2025 og 2,6 TWh høyere enn i 2025. Begge tall er sanne; de svarer på ulike spørsmål.

**Påstand: lave magasiner skyldes eksport, ikke forbruk.** Tallene går motsatt vei. Nettoeksporten i 2026 er den laveste på seks år, og landet importerte netto gjennom tre vintermåneder. Utvekslingen har dempet magasinfallet, ikke forsterket det. Det som avviker fra tidligere år, er høyere innenlandsk forbruk (4,7 TWh over snittet januar–juli) og lavere produksjon (3,0 TWh under) med fortsatt fallende magasiner, som innebærer lavt tilsig. NVEs tall for tilsiget bekrefter dette: tilsiget til Sør-Norge uke 1–37 2026 er 12,7 TWh under normalen, mot 3,0 TWh under i 2025 (avsnittet Tilsig nedenfor). Konklusjonen om eksporten avhenger ikke av tilsiget: eksporten er lavere enn normalt, ikke høyere.

To presiseringer i Moxnes' favør. Eksporten i 2025 var høy (nettoeksport 22,8 TWh for året, høyest i perioden), og magasinene gikk inn i 2026 lavere enn normalt i Sør-Norge. Noe av utgangspunktet for 2026 kan derfor tilskrives 2025. Og en analyse av hva eksporten ville vært uten utenlandskablene er et annet spørsmål enn hva som skjedde i 2026.

## Tilsig

Kilde: NVE, Kraftsituasjonen veke 37 2026 og veke 37 2025 (ukesrapport, pdf), tabell 4 (nedbør og tilsig uke 1–37 mot snitt 2006–2025, for 2025 snitt 2005–2024) og tabell 5 (hydrologisk balanse = avvik magasin + avvik snø, grunn- og markvann). Filer: data/raw/nve_kraftsituasjonen/, tabell i output/tab_tilsig_uke37.csv. Sør-Norge er summen av NO1, NO2 og NO5. NVE publiserer ikke tilsigsserien i API.

| Uke 1–37 | Tilsig 2026 (TWh) | Avvik fra snitt 2026 | Tilsig 2025 | Avvik 2025 | Hydrologisk balanse 2026 | 2025 |
|---|---|---|---|---|---|---|
| Norge | 84,2 | −21,6 | 100,3 | −6,2 | −14,7 | −0,9 |
| Sør-Norge (NO1+NO2+NO5) | 55,7 | −12,7 | 66,0 | −3,0 | −15,4 | −3,8 |
| NO2 | 25,1 | −6,2 | 30,1 | −1,6 | −10,8 | −3,7 |

Tilsiget til Sør-Norge er 10,3 TWh lavere enn i fjor og 12,7 TWh under normalen. Nedbøren i Sør-Norge uke 1–37 er 12,4 TWh under normalen (NO2 alene 7,6 under). Den hydrologiske balansen i Sør-Norge er 15,4 TWh under normalen, nesten alt i magasinene (avvik snø, grunn- og markvann 1,0 TWh). Bokføringen magasinendring = tilsig − produksjon − nettoeksport ut av området går dermed opp: magasinene i Sør-Norge ligger 16,8 TWh under median (avsnittet Magasinene), tilsiget forklarer om lag 13 av dem, og resten er høyere forbruk med lavere nettoeksport.

Vurdering: hovedforklaringen på de lave magasinene i 2026 er lite tilsig, dernest høyere forbruk. Eksporten trekker i motsatt retning.

## Ikke hentet

Statnetts utveksling per kabel. Tilgjengelig og kan legges til om spørsmålet skal forfølges.
