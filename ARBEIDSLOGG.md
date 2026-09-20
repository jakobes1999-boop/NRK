# Arbeidslogg – etterprøving av NRK «Prisen for billig strøm»

Eget arbeid (ikke OE-oppdrag). Mappe: `C:\Users\JakobEiksundSæthre\Desktop\NRK`. Nøkkel i `.env` (FROST_CLIENT_ID), aldri i chat eller kode.

## Bestilling (ordrett)
- 05.09.2026: «Cowork har begynt på dette, men Code må overta. Jeg skal ettergå NRKs beregninger. Hva er neste steg»
- 05.09.2026: «Dette er eget arbeid, mappe: C:\Users\JakobEiksundSæthre\Desktop\NRK det ligger en .env der med frost id. Kjør på. ALt klart?»
- 05.09.2026: «Når beregningene er ferdig verifisert, og eventuelt kritisert, sett opp en modell som tar høyde for de feilene NRK har gjort og kjør denne.»

## 05.09.2026 – første fullstendige kjøring

**Utgangspunkt:** Cowork-pakke (zip) med 9 skript + notatmal, kun røyktestet på syntetiske data.

**Rettelser mot ekte kilder:**
- Elhub: 4 av 5 filer gzip bak .csv-URL, `;` og desimalkomma, kolonner med Å (`ANTALL_MÅLEPUNKT`). Kommunefil feb 2022–apr 2026. STARTTID er lokal tid → måned fra strengslice (tz-parsing tok 5 min per 3 mill. rader).
- SSB PxWebApi v2: `valueCodes[...]`, ikke `selection[...]`; ContentsCode må angis; 06944 og 06513 er IKKE omkodet til gjeldende inndeling → omkoding via Klass 131 (2020→2024); 06513 må hentes per år.
- NVE: `KommuneNr` er intern ID (1–80), ikke kommunenummer → geo-kobling på (fylkesnr, navn). Fylkesregelen bommer for 27 kommuner (Hallingdal→NO5, Nord-Gudbrandsdal→NO3, Sunnfjord/Nordfjord→NO3, Sunnhordland→NO2). Uverifisert mot autoritativ kilde.
- Frost: ett kall per stasjon for hele perioden; 923 stasjoner i sørlige fylker; 184 kommuner med egen stasjon (162 i panelet), resten fylkessnitt.
- hvakosterstrommen.no: tilbakestilte forbindelser → sesjon + retry + mellomlagring hver 200. dag.
- Bestillingsstatus-filen har tre statuser (Ikke bestilt / Bestilt tidlig / Bestilt sent) og tre EAC-grupper (Husholdning Lav/Medium/Høy).

**Resultater første kjøring (før kritikk):** se `output/log_s07.txt`, `log_s08.txt`, `log_s10.txt`. M1 NRK-lik: post_np 0,095, gradtall 0,00188, R² within 0,94. Placebo M5: 0,051***. DiD ujustert 0,059; sesongjustert D2 0,043.

**Kritikk:** kritiker-agent (Opus), 26 punkter → `notat/KRITIKK_2026-09-05.md`. Tatt inn samme dag: regex-feil i geo._norm, husholdningsandel som primær behandlingsvariabel, M1/M2/M5 per målepunkt, Driscoll-Kraay-SE for post_np, event-study tidlig/sent, fylkesregel-robusthet (F7), eksplisitt mnd_fe-parameter. Ikke gjort: effektiv marginalpris med strømstøtte, wild cluster bootstrap, verifisering av prisområder, Statnett nettoeksport.

**Andre kjøring** (`py run_all.py --skip-download`): logg i `output/log_run_all.txt`. Tall til godkjenning: `output/TIL_GODKJENNING.md`.

## 05.09.2026 – faglig vurdering og kritikkrunde 2

Bestilling: «Gå igang med full faglig vurdering og kritikk, og foreslå eventuelle utbedringer». Skrevet `notat/FAGLIG_VURDERING_2026-09-05.md`; kritiker (Opus) på utkastet → `notat/KRITIKK2_2026-09-05.md` (6 kritiske, 9 vesentlige, 12 mindre). Utløste `src/s12_kritikk2_beregninger.py` → `output/tab_kritikk2.md`:
- Fyringssesong 2025/26 er IKKE kaldest (3 324 mot 3 589 i 2023/24); januar 2026 er kaldeste enkeltmåned.
- Ny D7 (område×måned×EAC-FE + sesongprofil per gruppe): 3,0 prosent, placebo −0,2. Nytt sentralanslag. D2 4,4 skyldes delte tidseffekter på tvers av grupper.
- Forbruksandel bestillere 0,77 (ikke målerandel 0,65–0,68) → aggregert 2,0–3,4 prosent.
- F7s lave se skyldes 15 tilførte NO3-kommuner med oppslutning 0–0,20.
- To Elhub-uttrekk gir 2,7 pp ulik oppslutning.
Vurderingen er skrevet om i tråd med alle punkter. Konklusjonsforslag: 2–4 prosent for bestillere (3 sentralt), 2–3 prosent aggregert, om lag en femdel av økningen 2025→2026.

## 05.09.2026 – skjæringsdato tidlig/sent og dose-respons (s13)

Bestilling: «Finn skjæringsdatoen for bestilt sent hos Elhub. Kan vi bruke dette til å finne enda mer begrunnede resultater?»
- Elhub-wiki for datasettet (tinyurl AgDapw → side 2816081922, REST API): tidlig = bestilt før eller på 2025-10-01, sent = 2025-10-02 t.o.m. 2026-04-30. Lagret i `kilder/elhub_wiki_norgespris_status.txt`. Vilkår: Norgespris gjelder fra bestillingsdagen.
- Sent-gruppens behandlingsandel per måned fra daglige tellinger (NO1/NO2/NO5 husholdning): 0,22 / 0,47 / 0,64 / 0,79 / 0,89 / 0,95 / 0,99 okt–apr.
- `src/s13_dose_sent.py` → `output/tab_dose_sent.md|csv`, `tab_event_study_dose.csv`, `fig_dose_sent.png`, `log_s13.txt`. E1: nivå 0,9 (p 0,07), dose 2,7 (p < 0,001), tidlig 3,1; placebo dose 0,5 (p 0,47). Månedsvis D7: sent 0,6 → 4,8, tidlig 1,3 → 4,8; forhold sent/tidlig 0,46 → 1,13 følger dosen. 7-punkts tilpasning sent = 0,3 + 1,05 × (dose × tidlig).
- Første tolkning («DiD måler i hovedsak behandlingseffekt, gruppeforskjell høyst 1–1,5 pp») ble TRUKKET etter kritikkrunde 3, se under.
- Uavklart: statusuttrekket er en fast kohort (1 262 835 målere) mot 2,0 mill. i daglige tellinger; dosen antas ha samme forløp.

## 05.09.2026 – kritikkrunde 3 på s13 (kritiker, Opus) → `notat/KRITIKK3_2026-09-05.md`

- K1: sent-kohorten har egen sesongprofil i førperioden (0,9–1,1 pp over tidlig i feb–apr); med sesongprofil per kohort faller forhold sent/tidlig til 0,74 → 0,98 og stigningen til 0,84 [0,70, 0,99]. Placebo med felles sesong feiler (1,5 prosent, p < 0,001), med per kohort 0,3 (p 0,19).
- K2/K3: nullverdi for nivåskiftet er 0,4–0,8 pp, ikke 0; E7-regresjonen fjernet. K4: t(G−1), klusterkolonne, KI.
- s13 versjon 2: begge sesongspesifikasjoner, simulert nullverdi (tab_dose_sent_nullverdi.csv), bootstrap på 7-punkts, placebovindu okt–apr, målerveid dose, figur med to paneler.
- Ny formulering: forenlig med behandlingseffekt, ikke avgjort; per fullt behandlet 2,1–4,6 prosent etter spesifikasjon; s13 rokker ikke ved 3,0 (tidlig_post 3,0–3,2 overalt) men bekrefter det ikke.
- Gjenstår: kohortens inntredelsesforløp (Elhub), leads-test, wild cluster bootstrap, døgnstart/døgnslutt 1. oktober.

## Status og neste steg
- [ ] Jakob godkjenner tall i `output/TIL_GODKJENNING.md`
- [ ] Skrive om notatets avsnitt 3–6 rundt D2/D3 og F2 (husholdningsandel); M1 omtales som «NRK-likt design», ikke replikasjon
- [x] Verifisere prisområde for de 27 overstyrte kommunene (VG som sekundærkilde, s16)
- [x] Strømstøtteparametre per år → effektiv marginalpris (s15)
- [x] Wild cluster bootstrap for DiD (s14)
- [x] Skjæringsdato tidlig/sent (Elhub-wiki) og dose-respons, s13 (v2 etter kritikk 3)
- [ ] Be Elhub om daglige Norgespris-tellinger per bestillingsstatus for kohorten, og om tellingen 1. oktober er ved døgnstart eller døgnslutt
- [x] Rette notatets påstand om at NRK ikke oppgir dusjlengde

## 05.09.2026 – bestilling: «Verfiser og utbedr alle utfordringer, slik at analysen blir vanntett»

Kravliste (åpne punkter fra KRITIKK 1–3), med hva som er mulig med dagens data:
- [x] A. Wild cluster bootstrap (Rademacher/Webb, restriktert) for D7, tidlig/sent, E1/E4, E6, placebo → `src/wcb.py`, `src/s14_wild_bootstrap.py`, `output/tab_wcb.*` (agent, opus). Funn: D7 0,0299 p_wcb < 0,001, KI [0,024, 0,037]; placebo p 0,14; E1 K sent_dose p 0,014, sent_post p 0,09; E6 Lav sent_dose p 0,019 → 0,08–0,09 (overlever ikke); 9-kluster tidlig_post p 0,002–0,037. Sanity: WCR andel p<0,05 = 0,055. SE-avvik 1 prosent mot statsmodels (pinv vs. reparametrisering).
- [x] B. Effektiv marginalpris med strømstøtte per område og måned fra timespot; NRK-like og F-modeller med effektiv pris → `src/s15_effektiv_pris.py`, `kilder/stromstotte_parametre.md` (agent, sonnet). Funn: strømstøtten trakk vinterprisen ned 19–53 prosent; M1 0,0872 → M1e 0,0831 (log-log), M2 0,0667 → M2e 0,0640; F2e share_post 0,084 p 0,22; prisgap 0,10 p 0,20. Terskel prisjustert 73/75/77 øre 2024–26; april–mai 2023 80 prosent svakere belagt.
- [x] C. Verifisere kommune→prisområde mot autoritativ kilde; sammenligne med `output/tab_kommune_prisomrade.csv` (agent, sonnet) → `src/s16_verifiser_prisomrade.py`, `output/tab_prisomrade_verifisering.csv|.md`. Ingen offisiell maskinlesbar kilde funnet (Elhub, NVE GIS3 og Geonorge forsøkt og forkastet, se md-rapport); brukte VGs «Strømprisen» til å sjekke enkeltvis alle 27 NVE-overstyrte kommuner + 2 manuelle unntak i geo.py. 28/29 samsvar, 0 avvik, 1 ikke verifisert (Sel – 404 hos VG, indirekte støttet av naboene). 12 av de 29 ligger i panelet. VG bekrefter selv at prisområdegrenser ikke alltid følger kommunegrenser; ingen delte kommuner identifisert i panelet, men ingen autoritativ liste funnet for å utelukke det. geo.py og panelet uendret.
- [x] D. Nettoeksport (NRK P4) fra SSB elektrisitetsbalanse → `output/tab_nettoeksport.*` (agent, sonnet). Funn: SSB 14091 (12824 avsluttet 2023); jan–jun 2026 mot 2025: nettoeksport −10 168 GWh, produksjon −6 379, bruttoforbruk +3 789 (hele landet); husholdning Sør-Norge +2 323. NRK P4 stemmer ikke tallmessig.
- [x] E. s13b: leads-test for dose, gradtall per kohort i D7-rammen, dosegrenser for kohorten (0,22–0,37 i oktober) (selv) → `src/s13b_dose_robusthet.py`, `output/tab_dose_robusthet.*`, `tab_dose_grenser.csv`, `tab_event_study_pre_kohort.csv`. Funn: dosegrenser gir E1-dose 1,6–2,1 og nivå 1,1–1,9 pp, E4-dose 3,1–3,8; tidlig mer temperaturfølsom (1,75 mot 1,0–1,1 prosent per 100 gradtall) men tidlig_post uendret 3,2–3,3 med gradtall; lead 0,16 (p 0,85); sent apr–sep 2025 snitt 0,2 prosent, maks |t| 2,0.
- [x] F. Spørsmålsliste til Elhub (kohortens inntreden, døgnstart/døgnslutt) og NRK (spesifikasjon) → `notat/SPORSMAL_ELHUB_NRK.md` (selv)
- [x] G. Rette notatmalens påstand om dusjlengde (selv)
- [x] H. Kritikkrunde 4 (kritiker, Opus) → `notat/KRITIKK4_2026-09-05.md`: 7 kritiske (feillesning av NRKs eksportpåstand – nivå, ikke fall; aritmetikk 63/37; WCB-bredde; selektiv lead/september-sitering; avsnitt 6/7/9 utdatert; egd_pa_maned uten kode), 10 vesentlige, 10 mindre. Alle rettet unntatt V6 (5 000 kWh-tak, ikke mulig med gruppesnitt) og M5 (kosmetikk). s15 med eksakt s07-spesifikasjon: M1 0,0950 → 0,0940. VG-oppslag kjørt på nytt med lagrede svar (28/28, Sel 404). Målervekst til tab_malervekst_oppslutning.csv. run_all --skip-download kjørt ende-til-ende etter rettelsene (log_run_all.txt).
Ikke mulig med dagens data (må bestilles): kohortens faktiske inntredelsesforløp (Elhub), NRKs spesifikasjon (NRK), 2021 i kommunepanelet (Elhub-filen starter feb 2022).


## 06.09.2026 – sluttverifisering og litteratur

- Pedagogisk notat utvidet: 2b (NRK-spesifikasjon, hva som er kjent/ukjent), 3b (D7-formel), 3c (sesongprofil, tidlig/sent), 3d (doseberegning, datarekkevidde).
- Litteratursøk (sonnet-agent) → notat/LITTERATUR_seleksjon_norgespris_2026-09-06.md, 20 kilder. Elhubs eget notat viser nivåseleksjon innen forbruksklasse (4,0–5,8 kWh/døgn).
- Codex gpt-5.6-sol/max sluttverifisering på kopi uten .env: kode og resultater i verifisering/ (01–05, JSON/CSV). Kvote tom før rapport; skript 04 kjørt ferdig lokalt. Syntese: notat/VERIFISERING_codex_2026-09-06.md. Alle seks modeller reprodusert (avvik ≤ 3e-5). Rettelser: WCB-KI 2,5–3,7 prosent (ikke 2,4), forbruksserie inkluderer hytter, F2-KI −3..16, «samme vær» → «samme område og måned». Første Codex-kjøring med --ignore-user-config falt til read-only sandbox; flagget skal ikke brukes.
- Debattinnlegg v3: notat/DEBATTINNLEGG_utkast_v3_2026-09-06.md.
- Åpent: tall til godkjenning; permutasjonstest ikke kjørt; NRKs spesifikasjon.
- Spesifikasjonssøk mot NRKs koeffisienter (opus-agent): src/s18_nrk_spesifikasjonssok.py, output/tab_nrk_spes_sok.*, notat/NRK_SPESIFIKASJONSSOK_2026-09-06.md. 6 384 kjøringer; tre av fire koeffisienter + R² (within) treffes uten tids-FE; inntekt ikke (0,0031 vs 0,0024). Elhub-rådata dekker kun 2022-02–2026-04. Debattinnlegg v5 (OE-stil, kort): notat/DEBATTINNLEGG_utkast_v5_2026-09-06.md.
- Spesifikasjonssøk-notatet skrevet om pedagogisk (fingeravtrykk-metafor, funn 1–5, 30-sekunders versjon); teknisk versjon arkivert som notat/NRK_SPESIFIKASJONSSOK_2026-09-06_v1_teknisk.md.

## 11.09.2026 – metodenotat til NRK og Elhub-referanse

- Jakobs utkast (utkast notat jas.docx) konvertert til notat/utkast_notat_jas_2026-09-07.md; 13 småretttelser som spor endringer i utkast notat jas_claude-rettelser.docx (08.09), + Elhub-referansesetning i _v2.docx (11.09; v1 var låst av Word).
- Elhubs analyse «Hvor mye av strømforbruket er knyttet til Norgespris?» (23.01.2026) hentet og lagret: kilder/elhub_analyse_forbruk_norgespris_2026-01.pdf/.txt + artikkel-HTML. Bekrefter 77/62/42 prosent oppslutning og 4,0–5,8 kWh/døgn nivåforskjell innen forbruksgruppe; ikke temperaturkorrigert, nivå ikke endring.
- notat/METODENOTAT_til_NRK_2026-09-11.md: data (tabell 1), M1/M5, spesifikasjonssøk, D7 med forklaring av hvert ledd, robusthet, aggregering, forbehold, 9 spørsmål til NRK, Elhub-referanser, reproduserbarhet. Alle tall til godkjenning.
- Repo publisert: https://github.com/jakobes1999-boop/NRK (main, 160 filer, 37 MB). Ekskludert via .gitignore: .env, store rådata (kommunefil 509 MB, statusuttrekk 61 MB, SSB/Klass-json, Frost-cache), NRK-artikkel (pdf/md), Elhub-PDF, VG- og Elhub-HTML, docx, debattinnlegg-utkast. Kontroll: ingen .env-verdier i noen fil (søkt på verdi). .gitattributes eol=lf. run_all.py inkluderer nå s18. Git-identitet lokalt: noreply-adresse for GitHub-brukeren.
- Metodenotat til NRK som Word: notat/METODENOTAT_til_NRK_2026-09-11.docx (kortversjon, 1 500 ord, 7 avsnitt, 3 tabeller; docx-js, validert). Lang md-versjon uendret.

## 13.09.2026 – Excel for ettergåing

- src/s19_excel_ettergaaing.py → output/NRK_etterproving_beregninger.xlsx (12 ark, levende formler). M1/M5 som within-transformasjon + LINEST (koeffisienter identiske med PanelOLS: 0,095031 / 0,050908; LINEST-SE er ikke klustret). D7 som gjennomsiktig kontrast: uvektet snitt 0,029651 = uvektet OLS-D7 (avvik 1e-14); n_mp-vektet snitt 0,02848 mot WLS 0,02988 (forventet avvik, FWL); placebo-kontrast −0,0010. Dose, forbruk jan.–jun. (18 119 GWh 2026), forbruksandel 0,772. Excel ikke rekalkulert lokalt (ingen Excel/LibreOffice headless; COM forbudt) – kontroll via Python-kolonner i arket. Tall til godkjenning.

## 20.09.2026 – vurdering av Codex' egne beregninger

- Mottatt norgespris_analyse_komplett.zip (Codex, uavhengig av repoet). Filer lagt i verifisering/codex_ekstern/ (uten avkortet 12 MB kohort-CSV som bare dekker 2023-10–2024-04, og uten pris-/temperaturserier som skriptet henter selv). Vurdering: notat/VURDERING_codex_zip_2026-09-20.md.
- Codex: matchet DiD 3,28, fleksibel 3,01, foretrukket 2,79 (fleksibel minus placebo), timebasert prisfordel-test (helning 6,4 pp per kr/kWh mot placebo). Gjenregnet fra did_month: DiD 0,0327 (Codex 0,0323), placebo −0,0053 (−0,0049), månedlig event-study, 493 315 målere og 6 200 GWh identisk. Anbefaling: behold D7 3,0; kjør timetesten selv på fulle data; ikke bruk trendjustert 3,8.
- Timetesten kjørt på fulle data: src/s20_timetest_prisfordel.py (Codex-skriptet med våre datastier, sklearn erstattet av numpy-WLS, terskler 73/75/77 øre bekreftet mot regjeringen.no id2900232 og nve.no). Open-Meteo-temperatur lagret i data/raw/openmeteo_hourly_temp_pa.csv (3 MB). Resultat identisk med Codex: helning 5,09 mot −1,32, differanse 6,41 (5,26–7,82), nivå 2,81 (2,35–3,26). Ført til output/TIL_GODKJENNING.md. s20 lagt i run_all.py.
- Leserinnlegg: 42 spor endringer (forfatter Claude) lagt direkte inn i «260913 utkast notat til NRK.docx», bare i det nederste utkastet («NRK bommer om Norgespris» + metodedel). Nytt: mekanismetest-avsnitt, intervall 2,5–3,7 og placebo −1..+1, 2–3 prosent for alle husholdninger, «NRK bør oppgi hele modellen». Rettet: «samme kilder som NRK», «faktiske effekten», «Resten – som NRK tilskriver», «omtrent samme resultater» → 10 prosent, nordmenn → Sør-Norge, Siviløkonom → samfunnsøkonom. Validert med pack.py; 0 lang tankestrek. Tallene står fortsatt til godkjenning.
