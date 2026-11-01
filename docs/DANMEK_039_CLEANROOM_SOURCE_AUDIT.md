# DANMEK-039 — teknisk importinventering och avveckling

## Varför den tidigare koden inte är den aktiva motorn

Det äldre grammatikspåret hade en lång inbördes importkedja, med ungefär denna riktning:

`danmek_038 → danmek_037 → danmek_036 → danmek_030/034/035 → danmek_027 → ches_015 → ches_014`.

Bland annat `ches_014_offline_english_bridge.py` importerar `olt_core.sources` som del av en historisk, ursprungsspråksinriktad CHES-arbetsgång. `danmek_022_private_automated_triage.py` importerar också `load_ot_book` och `read_provenance` direkt. Dessa importer är **inte** auktoriserade i den nuvarande engelska grammatikanalysen.

Den nya **enda aktiva** motorn `scripts/danmek_039_english_only.py` återanvänder det som är användbart *konceptuellt*: CHES JSON-fragment, verifierad bok-/kapitel-/versstruktur, privat källintegritet, engelsk finit verbgrupp, namn-/subjektfraser, objektmarkörer, mottagarled, kontextuell satsanknytning, syntetiska negativtester och privat HTML/TXT-export. Den är omskriven med enbart Python-standardbiblioteket och importerar **inte en enda modul** från äldre DANMEK, CHES-bryggor eller `olt_core`.

## Gällande beslut om gammal kod

- Tidigare DANMEK-008–038 körbara läsare, manuskriptbaserade jämförelseskript och rapporteringsköer är **icke-aktiva historiska implementationer**. Inget av dem finns i den aktiva 039-importkedjan.
- Den gamla `docs/DANMEK_MASTERPROMPT.md` med cirka 87 kB motsägelsefulla DANMEK-regler är **ersatt** av en kort enda aktiv masterprompt.
- Den gamla `data/policy/danmek_024_english_comprehensibility_owner_priority.json` är reducerad till en `SUPERSEDED`-post. Ett regressionstest förbjuder att dess gamla beteende återinförs.
- `docs/STATUS_CURRENT.md` har rensats på äldre DANMEK-sektioner men behåller oberoende OLT-projektinformation.
- Gammal historisk kod finns ännu i GitHub så länge den används av äldre tester eller separata OLT-forskningsverktyg. **Den är inte en aktiv DANMEK-motor.** Att radera den fysiskt utan importberoendegranskning riskerar att slå sönder andra OLT-delar; den får endast återanvändas efter en uttrycklig kodgranskning som visar att den inte återinför de gamla uppdragen.
- Den aktiva `DANMEK-039` modulen verifieras av en **egen GitHub Actions-grind** som kontrollerar importberoenden, nya styrpolicyn, syntetiska långdistanssubjekt och objekt som inte ska flyttas.

## Återstående språkvetenskapligt arbete

Den engelska motorn innehåller kontrollerade sätt att hitta subjekt med markerade objekt och vissa satsankare, inklusive en relativsatsanknuten **avståndsoberoende** sökning. Detta är **inte** ett fullständigt syntaktiskt system för alla 23 144 verser. Andra tvetydiga subjekt/objekt måste fortsätta inventeras och lösas med faktisk engelsk kontext, aldrig genom hebreisk jämförelse.

Den uppladdade CHES ZIP-korpusen avser 39 GT-böcker. Utgåva av alla 66 böcker förutsätter separat faktiskt engelsk NT-data. CHES-texten och privata utdata får inte publiceras utan nödvändiga rättigheter.
