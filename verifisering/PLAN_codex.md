# Uavhengig sluttverifisering – arbeidsplan

**Mål:** Reprodusere og faglig revidere modellene fra lokale parquet-filer med uavhengig kode, kontrollsummer og en samlet norsk rapport.

**Arkitektur:** Små Python-skript under `verifisering/` deler felles data- og regresjonsfunksjoner, men importerer ingen prosjektkode fra `src/`. Maskinlesbare resultater skrives ved siden av skriptene og er tallgrunnlag for rapporten.

**Teknologi:** `py -3`, pandas, numpy, statsmodels, linearmodels, pyarrow og standardbiblioteket. Ingen nettverk, Office eller COM.

**Spesifikasjon:** Brukeroppgaven i denne samtalen og de uttrykkelig angitte lokale grunnlagsfilene.

## Globale krav

- Bare les eksisterende filer; alle nye filer skrives under `verifisering/`.
- Ikke kjør `s01`–`s05` eller andre prosjektskript.
- Rapporter norske desimalkomma i tekst og rene tall i datafiler.
- Dokumenter SHA-256, radtall, metode, avvik og kontrollsummer.
- Bruk `[fylles inn]` der lokale data ikke identifiserer en størrelse.

## Oppgaver

1. Opprett `felles.py` og `01_reproduksjon.py`: kontroller parquet-skjema, nøkler, datoer og SHA-256; reproduser D7, placebo, tidlig/sent, M1 og M5; skriv CSV-resultater. Kjør med `py -3 verifisering/01_reproduksjon.py` og kontroller N = 837/648/10 047/8 668.
2. Opprett `02_identifikasjon.py`: beregn Patsy-kolonner, rang, nullitet, frihetsgrader, eksakt FWL-koeffisient, førperiodebasert manuell kontrast, uvektet D7 og alternativ klustring. Krev FWL-avvik under `1e-10`.
3. Opprett `03_placebo_robusthet.py`: kjør en 12-måneders pre-event-study med felles Wald-test og leave-one-cluster-out for D7 og placebo; skriv CSV/JSON.
4. Opprett `04_wcb_revisjon.py`: implementer WLS-transformasjon, restringert WCR, Rademacher/Webb, CR1, Monte Carlo-p og fin testinversjon uavhengig; reproduser B = 999/seed 1 og kjør eksakt 512-mønsters kontroll med ni område × klasse-klustre.
5. Opprett `05_dose_sensitivitet.py`: beregn enkel og målerveid sent-dose, mekanisk full-dose-korreksjon, SUTVA-identiteten og sensitiviteter for seleksjon/spillover.
6. Opprett `RAPPORT_codex.md` og `kjor_alle.py`: besvar seksjon 1–7, bekreft/avkreft vedlegget og ranger alle feil og udekkede formuleringer.
7. Kjør `py -3 verifisering/kjor_alle.py`, syntakskontroll og ferske SHA-256-kontroller; sammenhold alle leveranser punkt for punkt med brukerkravene.
