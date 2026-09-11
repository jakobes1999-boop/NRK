# Spørsmål som må avklares eksternt før analysen kan kalles avsluttet

Utarbeidet 05.09.2026. Punktene under kan ikke løses med data som er tilgjengelige i prosjektet.

## Til Elhub (datasett `consumption_per_norgespris_order_status_eac_group_mba_hour_20231001_20260430`)

1. **Kohortens inntredelsesforløp.** Antall målepunkter per bestillingsstatus er konstant gjennom hele serien (sent 367 106, tidlig 493 315, ikke bestilt 402 414). Kan Elhub levere daglige tellinger av hvor mange i gruppen «Bestilt sent» som hadde aktiv Norgespris per dag fra 2. oktober 2025 til 30. april 2026, per prisområde og forbruksgruppe? Vi bruker i dag adopsjonskurven for alle husholdningsmålere som tilnærming; sammensetningen avviker (43 prosent sene i kohorten mot 55 prosent utenfor).
2. **Kohortdefinisjon.** Består gruppene av de samme målepunktene hele veien (målepunkter med kontinuerlig historikk okt. 2023–apr. 2026), eller er antallet et snitt? Hvilke målepunkter er utelatt (flytting, nye anlegg, bytte av forbruksgruppe)?
3. **Tellingen 1. oktober** i `norgespris_count_per_mba_consumption_group`: er antallet målt ved døgnstart eller døgnslutt? 26 824 nye Norgespris-målere kom 2. oktober, og valget forskyver hele dosekurven.
4. **Forbruksgruppe (EAC).** Er gruppene Lav/Medium/Høy fastsatt én gang (når?) eller oppdatert løpende? Løpende oppdatering gir seleksjon på utfallet.
5. **Anonymisering.** Bekreft at ingen celler i statusuttrekket er nullet (terskel 100 målere), og hvordan «ANTALL» og «ANTALL_MÅLEPUNKT» skiller seg.

## Til NRK (artikkelen «Prisen for billig strøm», 27.08.2026)

1. **Spesifikasjon.** Er «Norgespris» i regresjonen en 0/1-dummy for perioden fra oktober 2025, eller en andel bestillere per kommune? Er utfallet totalt kWh per kommune eller kWh per målepunkt? Nivå eller logaritme?
2. **Faste effekter.** Kun kommune, eller også kalendermåned/år? Hvilken R² oppgis (within, overall)?
3. **Standardfeil.** Klustret (på hva), robuste eller vanlige? Signifikansnivåene for en ren tidsvariabel er ikke tolkbare uten dette.
4. **Data.** Hvilken Elhub-fil (kommune × time × gruppe?), hvilke forbruksgrupper (husholdning alene eller med hytter), og hvordan er 2021 dekket når den åpne kommunefilen starter i februar 2022?
5. **Inntekt.** Hvilken inntektskilde og hvilket år for 2025 og 2026, siden SSB-tallene stopper i 2024?
6. **Boligstørrelse.** Er den regressor eller bare datakilde? Kommunefaste effekter absorberer en tidsinvariant boligstørrelse.
7. **Prisområde per kommune.** Hvilken kilde brukte NRK for å tilordne kommuner til NO1/NO2/NO5?
8. **Nettoeksport.** Statnett-tallet for nettoeksport 1.1.–31.7.2026 som ligger bak «årets nettoeksport tilsvarer det økte forbruket blant husholdningene i Sør-Norge»: hvilket tall er brukt for forbruksøkningen, for hvilken periode og hvilke kundegrupper? SSB 14091 gir 2 682 GWh jan–jul 2026 for hele landet.
