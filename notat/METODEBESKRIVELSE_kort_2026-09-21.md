# Litt om metoden

*Utkast til metodedel under leserinnlegget, 21.09.2026. Erstatter avsnittet «Litt om metoden» i «260913 utkast notat til NRK.docx». Alle tall til godkjenning. Kode og data: github.com/jakobes1999-boop/NRK.*

---

**NRKs modell, etterprøvd.** NRK oppgir fire koeffisienter og en forklaringskraft, men ikke hele oppsettet. Jeg har satt opp en modell av samme type på åpne data fra Elhub, Meteorologisk institutt og SSB: forbruket i 197 kommuner i Sør-Norge per måned fra februar 2022 til april 2026, forklart med gradtall, spotpris, inntekt, boligstørrelse og en variabel som er null før oktober 2025 og én etter. Den gir om lag 10 prosent, og koeffisientene for temperatur, pris og forklaringskraft ligger nær NRKs. Later jeg som at Norgespris ble innført i oktober 2024, og bruker bare data fra før ordningen fantes, gir samme modell en økning på om lag 5 prosent. En metode som finner en effekt av en ordning som ikke eksisterte, kan ikke tallfeste effekten av en som gjør det. Årsaken er at alle kommuner fikk ordningen samme dag, så modellen har ingen gruppe å sammenligne med.

**Data for min modell.** Elhub publiserer forbruket til husholdninger i NO1, NO2 og NO5 fordelt på om de bestilte Norgespris før 1. oktober 2025, bestilte senere i vinteren, eller ikke hadde bestilt per 30. april 2026, og på tre klasser for årsforbruk. Det gir 27 grupper, fulgt måned for måned fra oktober 2023 til april 2026. Utfallet er forbruk per måler i hver gruppe, målt i logaritmer, slik at koeffisientene kan leses som prosent.

**Modellen.** Forbruket i gruppe g i måned t forklares med fire ledd:

1. En fast effekt per gruppe. Den fjerner nivåforskjellen mellom bestillere og ikke-bestillere. Bestillerne bruker mer strøm fra før, og det skal ikke telle som effekt.
2. En fast effekt per prisområde, forbruksklasse og måned. Den fjerner alt som er felles for bestillere og ikke-bestillere i samme område, klasse og måned: temperatur, spotpris, strømstøtte, ferier og målervekst.
3. Bestillernes eget avvik per kalendermåned og forbruksklasse, estimert på de to årene før ordningen. Bestillerne har et annet vintermønster enn ikke-bestillerne også uten Norgespris, og det skal heller ikke telle som effekt.
4. Bestilt × måned fra og med oktober 2025. Koeffisienten på dette leddet er effekten: hvor mye bestillerne avviker fra sitt eget mønster etter at ordningen kom, ut over det som skjedde med ikke-bestillerne.

**Spesifikasjonen.** Skrevet ut er modellen

log y(g,t) = α(g) + λ(p,k,t) + γ(m,k)·B(g) + β·B(g)·P(t) + e(g,t)

Her er g en av de 27 gruppene (prisområde p × bestillingsstatus × forbruksklasse k), t en måned fra oktober 2023 til april 2026 (31 måneder, 837 observasjoner), og y forbruk per måler i kWh. α(g) er leddet 1, λ(p,k,t) er leddet 2, γ(m,k) er leddet 3 for kalendermåned m, B(g) er 1 for grupper som bestilte Norgespris og 0 ellers, og P(t) er 1 fra og med oktober 2025. β er leddet 4, og effekten i prosent er exp(β) − 1. Modellen er estimert med vektet minste kvadraters metode med antall målere i gruppen som vekt. Standardfeilene er klustret på gruppe, og intervallet er regnet med wild cluster bootstrap (Rademacher-vekter, 999 trekk, invertert test). Sent bestillere har B(g) = 1 fra oktober 2025.

Modellen er estimert med vektet minste kvadraters metode, med antall målere som vekt. Standardfeilene er klustret på gruppe. Med 27 klustre er vanlige intervaller for smale, så intervallet er regnet med wild cluster bootstrap. Resultatet er 3,0 prosent, med intervall 2,5 til 3,7.

**Kontroller.** Flytter jeg innføringen til oktober 2024 og bruker bare data før oktober 2025, gir modellen mellom minus én og pluss én prosent. Månedsvise anslag før oktober 2025 ligger nær null, og effekten bygger seg opp gjennom vinteren fra 1,7 prosent i oktober til 4,8 i februar. Ingen enkelt gruppe driver resultatet. En uavhengig gjennomgang med et annet oppsett på samme data gir 2,8 til 3,3 prosent.

**Mekanismen.** Norgespris gir størst fordel i timene der spotprisen er høyest. Regnet time for time, justert for klokkeslett, kalendermåned og temperatur, er bestillernes merforbruk størst i nettopp de timene: om lag 0,6 prosent per 10 øre større prisfordel. Vinteren før, da ingen hadde Norgespris, finnes ikke den sammenhengen. Det er vanskelig å forklare med at bestillerne bare er annerledes folk.

**Fra bestillere til alle.** Bestillerne står for om lag tre firedeler av husholdningenes forbruk i Sør-Norge. Om ikke-bestillerne er upåvirket, svarer 3 prosent for bestillerne til 2 til 3 prosent for alle husholdninger.

**Forbehold.** Anslaget hviler på at bestillere og ikke-bestillere ellers ville utviklet seg likt. Det kan ikke bevises, men det er testet så langt dataene rekker. Effekten er målt mot strømstøtten ikke-bestillerne beholdt, ikke mot full markedspris. Sent bestillere regnes som bestillere fra oktober selv om de fikk ordningen gradvis, som gjør anslaget forsiktig. Elhubs grupper dekker husholdninger med årsforbruk mellom 1 000 og 50 000 kWh.

**Bestillerne er annerledes.** Elhubs egen analyse fra januar 2026 viser at 77 prosent av husholdningene med høyt årsforbruk valgte Norgespris, mot 42 prosent av dem med lavt, og at bestillerne bruker 4 til 6 kWh mer per døgn også innenfor samme forbruksklasse. Det er en forskjell i nivå, ikke en effekt av ordningen. Det er derfor modellen måler endring, ikke nivå.
