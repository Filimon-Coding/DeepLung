# Møtereferat med internveileder

## Møte med Trym / internveileder - 21.01.2026

- Vi diskuterte MVP og at vi bør avklare med ekstern veileder hva de faktisk ønsker at systemet skal løse.
- Det ble snakket om at prosjektet bør ha fokus på å lage noe som er nyttig for klienten, ikke bare en teknisk demo.
- Vi bør vurdere intervjuer med brukere for å forstå hva de trenger og hva de forventer av systemet.
- Vi skal gjøre et bredt søk etter datasett i starten og bruke ChatGPT/Deep Research som støtte for å finne relevante kilder.
- Alle datasett og modeller som blir funnet må verifiseres etterpå, slik at vi vet at de faktisk passer prosjektet.
- Vi må lage tydelige punkter for hva vi ser etter i datasettet, for eksempel labels, kvalitet, lisens og relevans.
- Det kan være nyttig å spørre ekstern veileder om de har data vi kan teste på, og om de har ressurser til å trene modellene våre.
- Dersom datasettet inneholder mer enn bare lungesvulst, kan det fortsatt være relevant hvis modellen lærer å skille lungekreft fra andre funn.
- Vi må sjekke hvor mange labels som gjelder lungekreft, og om datasettet er balansert.
- Lisenser på datasett må sjekkes nøye, spesielt hvis data ligger på GitHub eller lignende.
- Problemer med å finne og bruke data bør tas med i risikoanalysen.
- Tips til datasøk: bruke logiske operatorer som `AND`, filtrere på Kaggle, og se på PhD-avhandlinger om automatisk deteksjon og klassifisering av lungekreft.
- Neste møte ble satt til onsdag 04.02.2026 kl. 15:30.

---

## Møte med Trym / internveileder - 28.01.2026

- Vi gikk videre med å avklare prosjektretningen og hva som er realistisk å få til i bachelorperioden.
- Det ble anbefalt å holde fokus på en fungerende helhet, heller enn å legge til for mange ekstra funksjoner tidlig.
- MVP-en bør vise sammenhengen mellom databehandling, modellprediksjon og webapplikasjonen.
- Vi bør fortsette å lete etter datasett med tydelige labels og god dokumentasjon.
- Begrensninger i datasettet bør skrives ned tidlig, fordi det kan påvirke både modellresultater og rapporten.
- Rapporten bør forklare hvorfor vi tar valg, ikke bare hva vi ender opp med å implementere.
- Vi bør føre løpende logg over beslutninger, problemer og endringer i prosjektet.
- Til neste gang bør vi fortsette datasøk, skissere teknisk pipeline og forberede spørsmål om modelltracking og systemstruktur.

---

## Møte med Trym / internveileder - 29.01.2026

- Vi snakket om MLOps og at MLflow kan brukes til tracking av parametere, eksperimenter og resultater.
- Klassifisering kan støttes gjennom heatmaps, slik at man kan se hvor modellen fokuserer.
- Heatmaps kan også brukes når vi skriver om trustworthiness i AI, fordi de kan vise om modellen faktisk ser på lungene og ikke irrelevante områder rundt.
- Forprosjektrapporten bør utdype hvordan frontend skal se ut og hvordan brukeren skal møte systemet.
- Risikoanalyse bør være med i forprosjektrapporten, med sannsynlighet, konsekvens og håndtering.
- Vi bør ha noen brukerhistorier som viser hva brukerne trenger, hvilke metrikker de er ute etter, og hva som gjør at de kan stole på systemet.
- Vi må tenke på hva som kan gjøres parallelt for å komme i mål.
- Frontend og applikasjonsframework kan utvikles samtidig som vi jobber med datasett og litteraturstudie.
- Vi bør begynne å tenke på pipeline-design allerede nå.
- Prosjektet bør knyttes tilbake til systemutvikling og planlegging fra tidligere emner.
- Prosjektdokumentasjon kan og bør skrives fortløpende.
- Vi bør unngå å bruke ordet "startup" om prosjektet.
- Zotero kan brukes for å samle, lagre og organisere litteratur, og kan eventuelt deles som felles bibliotek i gruppa.
- Neste møte ble satt til onsdag 04.02.2026 kl. 15:30.

---

## Møte med Trym / internveileder - 04.02.2026

- Vi gikk videre på MLOps-oppsettet og diskuterte hvordan MLflow kan brukes til å tracke parametere og resultater.
- Klassifisering og heatmaps ble igjen diskutert som en viktig del av forklarbarheten i systemet.
- Forprosjektrapporten bør utdype frontend, risikoanalyse og hvordan systemet skal planlegges.
- Risikoanalysen bør inneholde sannsynlighet, konsekvens og håndtering.
- Vi bør lage brukerhistorier og finne ut hvilke metrikker brukerne faktisk er interessert i.
- Det ble diskutert hva som gjør at brukere stoler på systemet, og at heatmaps kan være nyttig for dette.
- Vi bør jobbe parallelt med frontend, datasett, litteraturstudie og pipeline.
- Dokumentasjon bør skje underveis, ikke bare mot slutten.
- Zotero ble nevnt som et mulig verktøy for litteraturhåndtering.
- Neste møte ble satt til onsdag 11.02.2026 kl. 15:30.

---

## Møte med Trym / internveileder - 11.02.2026

- Vi diskuterte hvordan pipelinen skal gå fra medisinske bildedata til input som modellen kan bruke.
- Hvert steg i pipelinen bør dokumenteres, for eksempel konvertering, preprocessing, trening og evaluering.
- Det kan være lurt å starte med et mindre datasett eller et utvalg først, for å sjekke at pipelinen fungerer før vi skalerer opp.
- Vi bør skille tydelig mellom trening, validering og endelig testing.
- Evalueringen bør ikke bare handle om accuracy, spesielt siden dette er et medisinsk klassifiseringsprosjekt.
- Rapporten bør forklare hvilke metrikker vi velger og hvorfor de passer til prosjektet.
- Frontend og backend kan utvikles parallelt med modellarbeidet.
- Vi må tenke på hvordan prediksjoner og visualisering skal vises for brukeren.
- Tekniske problemer bør dokumenteres når de skjer, inkludert hvordan de ble løst eller hvorfor de ble utsatt.

---

## Møte med Trym / internveileder - 18.02.2026

- Vi diskuterte datasett og databehandling.
- Datasettet er lite, så data augmentation bør vurderes for å øke datamengden.
- Eksempler på augmentation er resizing og rotasjon av bilder.
- Noen bruker også generativ AI for å lage nye bilder basert på eksisterende bilder, men dette må vurderes kritisk.
- Hvis datasettet er ubalansert, kan det ha stor effekt på modellens ytelse.
- Vi bør lese om class imbalance og metoder for å håndtere dette i machine learning.
- Målet er å skille mellom benigne og maligne tilfeller.
- Det handler ikke bare om å gjenkjenne malignitet isolert, men å kunne skille benign fra malign.
- Det kan også vurderes om modellen bør skille mellom knute og ikke-knute.
- Det viktigste er ikke nødvendigvis om modellen blir "bra" eller "ikke bra", men prosessen og metodikken bak arbeidet.
- Frontend-prosessen bør dokumenteres før utvikling, for eksempel med diagrammer og skisser.
- Før neste møte bør vi avklare om møtet skal være digitalt eller fysisk, sende e-post til Trym, sjekke GitLab-begrensninger og eventuelt spørre Hedda om mer lagringsplass eller data.
- Videre bør vi etablere faste ukentlige møter og dokumentere arbeidet fortløpende på GitHub.

---

## Møte med Trym / internveileder - 25.02.2026

- Vi bør ha notater om hva vi gjør og hvorfor vi gjør det.
- Disse notatene blir nyttige som logg når vi begynner å skrive bachelorrapporten for fullt.
- Fokuset bør være å fullføre prosjektet og samtidig få med prosessen og loggføringen.
- Det ble presisert at bachelorrapporten er det som gir grunnlaget for karakteren i bacheloremnet.
- Vi må vise at ting er gjort riktig ved å bruke utviklingsmetodikk.
- Det vi sier at vi gjør i rapporten, må også stemme med det vi faktisk gjør i prosjektet.
- Vi bør lese mer om hvordan hele systemet skal interagere.
- Det må avklares hvordan AI-modellen skal kobles mot frontend og backend gjennom inference.
- Når alle delene kobles sammen, brukes skolens server.
- I rapporten bør vi skrive at brukeren i et reelt perspektiv bør ha egen GPU for å bevare privacy.
- Hver person i gruppa har 50 timer tilgang på GitLab i måneden.
- Hvis dette ikke er nok, kan vi spørre Hedda om mer tilgang.

---

## Møte med Trym / internveileder - 04.03.2026

- Vi gikk gjennom status på applikasjon, datasettarbeid og modellpipeline.
- Veileder anbefalte å holde fokus på hovedfunksjonaliteten før vi legger til ekstra features.
- Uferdige deler bør dokumenteres tydelig, slik at de kan diskuteres ærlig i rapporten.
- Rapporten bør forklare hvordan frontend, backend, modell og lagring henger sammen.
- Det bør komme tydelig frem hvor inference skjer, og hvordan resultatet sendes tilbake til brukergrensesnittet.
- Hvis systemet bruker skolens infrastruktur, bør dette forklares i teknisk dokumentasjon.
- Risikoer som datasettstørrelse, lagring, hardware, privacy og sikkerhet bør tas med.
- Metodekapittelet bør forklare utviklingsprosessen, verktøyene og de tekniske valgene.
- Diskusjonsdelen kan brukes til å skrive om begrensninger, kompromisser og mulig videre arbeid.

---

## Møte med Trym / internveileder - 11.03.2026

- Vi diskuterte mulige stretch goals for prosjektet.
- Ekstra features kan legges til hvis det blir tid, men hovedprosjektet bør prioriteres først.
- Eventuelle ekstra features kan utvikles på egen branch mens hovedfunksjonaliteten holdes stabil.
- Vi snakket om hvordan pipelinen bør være bygget dersom deler av den skal byttes ut i fremtiden.
- Systemet bør derfor designes slik at fremtidige endringer i pipeline er mulig.
- MLOps ble forklart som en machine learning-versjon av DevOps.
- Vi bør tenke på hvordan MLOps-prinsipper passer inn i arbeidsflyten og modellutviklingen vår.

---

## Møte med Trym / internveileder - 18.03.2026

- Vi etterspurte tilbakemelding på problemstillingen.
- Veileder mente at vi ikke trenger å fokusere for mye på problemstillingen akkurat nå, og hadde ikke rukket å se grundig på den.
- Gjennomgikk endringer i webapplikasjonen på møtet:
    - Admin kan nå lage nye brukere med mer informasjon.
    - Applikasjonen har funksjonalitet for å requeste access til innlogging.
    - 3D-volum blir laget direkte i mappen til koden.
    - Vi må tenke på lagring av sensitive data i databasen med tanke på sikkerhet.
    - Hvis vi ikke rekker å løse alt rundt sikkerhet, må dette nevnes i rapporten.
    - En mulig videreutvikling er at brukernavn genereres basert på personalia, men samtidig på en måte som unngår like brukernavn.
- Rapporten bør struktureres etter kravene som ligger på Canvas.
- Vi kan bruke Sona og ChatGPT til å finne kilder.
- Til neste gang bør vi strukturere rapporten etter dokumentasjonsstandarden, se på sikkerhet i applikasjonen og fikse visualisering/heatmap.

---

## Møte med Trym / internveileder - 25.03.2026

- Vi gikk gjennom status på webapplikasjonen, modellpipelinen og rapportstrukturen.
- Veileder anbefalte å holde fokus på MVP og ikke bruke for mye tid på valgfrie funksjoner.
- Funksjoner som ikke blir ferdige bør dokumenteres som begrensninger eller videre arbeid.
- Vi diskuterte hvordan AI-modellen skal kobles til backend og frontend gjennom inference service.
- Rapporten bør forklare flyten fra opplastet scan til prediksjon og visualisering.
- Det bør være tydelig forskjell på preprocessing, inference og presentasjon av resultat.
- Prosessdokumentasjonen bør forklare utviklingsmetodikken og hvordan vi brukte Scrumban/Kanban.
- Tekniske valg bør begrunnes, spesielt datasett, modellarkitektur, Grad-CAM og teknologistack.
- Utfordringer med trening, data og infrastruktur bør tas med i diskusjonen.

---

## Møte med Trym / internveileder - 08.04.2026

- Vi gikk gjennom strukturen på frontend, backend og inference service.
- Rapporten bør forklare hvordan tilgangskontroll, analyse, resultatside og historikk henger sammen.
- Skjermbilder og diagrammer kan gjøre applikasjonsflyten lettere å forstå.
- Modellkapittelet bør forklare både klassifiseringsresultatet og hvorfor Grad-CAM brukes.
- Grad-CAM bør presenteres som støtte for forklarbarhet, ikke som en garanti for at modellen er medisinsk pålitelig.
- Vi bør være forsiktige med formuleringer rundt medisinsk bruk og klinisk tillit.
- Testing bør inkludere både tekniske tester og brukerrettet feedback der det er mulig.
- Rapporten bør skille mellom det som faktisk er testet og det som er begrenset av tid, data eller infrastruktur.

---

## Møte med Trym / internveileder - 15.04.2026

- Rapporten bør ha et tydelig skille mellom prosessdokumentasjon og produktdokumentasjon.
- Prosessdelen bør forklare planlegging, metodikk, risiko, krav og brukerfeedback.
- Produktdelen bør forklare systemet som er implementert, teknologistack, modellpipeline, testing og resultater.
- Kravene bør kobles til det som faktisk er implementert.
- Hvis krav har endret seg underveis, bør rapporten forklare hvorfor.
- Tilbakemeldinger fra klinikere eller brukere bør brukes til å begrunne forbedringer i prototype og grensesnitt.
- Begrensninger bør skrives tydelig og ærlig.
- Viktige begrensninger er datasettstørrelse, class imbalance, privacy, hardwaretilgang og medisinsk validitet.

---

## Møte med Trym / internveileder - 22.04.2026

- Webapplikasjonskapittelet bør forklare arkitekturen før det går inn på enkeltkomponenter.
- Modellkapittelet bør koble dataset preprocessing, trening, evaluering og Grad-CAM sammen til én tydelig pipeline.
- Rapporten bør forklare evalueringsmetrikker og hvorfor de er relevante.
- Accuracy alene gir ikke nok kontekst i et medisinsk klassifiseringsprosjekt.
- Error analysis og usikkerhet bør diskuteres der det er mulig.
- Vi bør forklare hvordan systemet kan startes og testes lokalt.

---

## Møte med Trym / internveileder - 29.04.2026

- Veileder anbefalte å prioritere stabilisering av eksisterende funksjonalitet fremfor å legge til nye features.
- Hvis en feature er uferdig, bør den enten ferdigstilles, forenkles eller flyttes til videre arbeid.
- Terminologi bør være konsekvent i rapporten.
- Rapporten bør vise sammenheng mellom prosjektmål, implementasjon, testing og resultater.
- Diskusjonskapittelet bør reflektere over tekniske valg, kompromisser og hva som kunne vært gjort annerledes med mer tid.

---

## Møte med Trym / internveileder - 06.05.2026

- Fokuset bør nå flyttes fra utvikling til ferdigstilling av bachelorrapporten.
- Hvert kapittel bør ha en tydelig funksjon og unngå unødvendige gjentakelser.
- Introduksjon, avgrensning, metode, implementasjon, testing, diskusjon og konklusjon bør henge godt sammen.
- Påstander om AI, medisinsk bildeanalyse, explainability og utviklingsmetodikk bør støttes med kilder.
- Referanser, figurer og bildetekster bør kontrolleres.
- Kjente mangler bør beskrives som begrensninger eller videre arbeid.

---

## Møte med Trym / internveileder - 13.05.2026

- Rapporten bør være tydelig, konsekvent og lett å følge.
- Konklusjonen bør svare på de opprinnelige prosjektmålene.
- Siste gjennomgang bør fokusere på språk, overskrifter, figurer, kilder og konsekvent begrepsbruk.
- Skrive mer på Process Dokumentation, men gjøre ferdig Discussion og Conclusion først og deretter se om hvordan vi ligger rundt ordomfang og hvor mye mer man kan dokumentere i process dokumentation. 
- Gjøre endringer ihht kommentarer som Trym har lagt til i bachelorrapporten. 
