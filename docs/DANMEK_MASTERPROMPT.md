# DANMEK — ENDA AKTIVA MASTERPROMPTEN (separat från OLT:s övergripande dokument)

**DANMEK-039 · 2026-11-01 · OWNER-LOCKED · ACTIVE**

Denna fil ersätter samtliga tidigare DANMEK-masterpromptar och motstridiga DANMEK-arbetsinstruktioner. Historiska tekniska rapporter är inte aktiva styrdokument.

## Det enda aktiva språk- och kodningsuppdraget

**CHES engelska är DANMEK:s accepterade, kompletta textbas för Gamla testamentet (39 böcker).** Uppgiften är att korrigera **engelsk subjekt–verb-ordföljd genom hela denna text**, oavsett hur långt ifrån varandra verb och subjekt står. Texten ska förbli mycket bokstavlig och begriplig. Korrekt ordföljd betyder att det *verkliga subjektet i respektive sats* identifieras, inte att alla namn efter verb flyttas.

**NO HEBREW REVALIDATION.** Ingen jämförelse CHES↔hebreiska, CHES↔arameiska, CHES↔OSHB/WLC; ingen återkontroll av hebreiska ord, lemma, morfologi eller ordjustering som villkor för engelsk grammatik. **CHES's linguistic decisions** are accepted as the English working baseline. Forskning om grundspråk tillhör helt andra, separat beställda OLT-uppdrag och får inte importeras i DANMEK:s aktiva körväg.

## DANMEK-040 — KORRIGERAD SATSKOPPLING OCH UPPDELAT ENGELSKT VERB (2026-11-01)

Direkt engelskspråkig CHES-inventering visar **5 019** separata engelska pronomenprefixfragment, av vilka **4 586** kan paras med en eller två efterföljande lexikala verbdelar. Det är verbgrupper, inte bevisade ordföljdsfel. Den tidigare DANMEK-039 v1-regeln som kunde flytta ett **inbäddat bisatssubjekt till huvudverbets position** är utraderad: den saknade identifierade träffar i det undersökta faktiska relativsatsmönstret och var grammatiskt osäker. Varje identifierat subjekt ska kopplas till sin *egen* finita engelska verbgrupp, även om föregående huvudsats ligger långt bort.

Korrigera endast fullständiga subjektfraser. Samordningar (person + `and·` + annan person), titlar, `-of`-kedjor och separata objekt är inte förenklade namn som får lossas från sin fras. Nytt v2-revisionsnummer i **samma enda aktiva `scripts/danmek_039_english_only.py`**; inga äldre motorer, inga språkkälljämförelser eller parallella läsarversioner. [Korpusbaserad analys](DANMEK_040_REAL_ENGLISH_SPLIT_CLAUSE_AUDIT.md).

## DANMEK-041 — RÄTT SATSROLL EFTER MOTTAGARE OCH OBJEKT (2026-11-01)

Den verkliga engelska CHES-korpusen har minst två avgörande tvetydigheter: ett namn efter `said to·them` kan vara **talaren** eller **subjektet inne i det citerade talet**, och ett namn efter `called »·her` kan vara objektets **namnkomplement** i stället för agent. Flytta **inte** ett namn baserat på mottagaren/objektmarkören ensam. DANMEK-041 kräver självständig engelsk evidens efter **hela** subjektfrasen; en imperativ eller en avgränsad talöppning kan styrka talarroll, medan `not` ensamt inte räcker. Namngivnings-/identifieringsverb efter markerade objekt behandlas som osäkra. Objektmarkörernas antal måste förbli oförändrat.

Privat korpusskanning hittade 572 engelska talverb + tredje persons mottagarpronomen, varav 132 följdes av ett namnformat fragment; 25 uppfyllde den ytterligare konservativa talöppningsregeln. Det är **kandidatpositioner, inte 25 bevisat rättade verser**. Ingen grundtextkontroll. Endast den aktiva `scripts/danmek_039_english_only.py` får ändras. [Research](DANMEK_041_PRIVATE_ENGLISH_DIALOGUE_ROLE_AUDIT.md).

## DANMEK-042 — SLUTNA ENGELSKA PREPOSITIONSLED OCH MARKERADE DATIVOBJEKT (2026-11-01)

Korrigera subjektet i **samma engelska sats** även när ett redan fullständigt prepositions-/adverbialled står mellan det finita verbet och den *kompletta* subjektfrasen. Förflytta inte ett namn om prepositionen saknar eget objekt, om subjektfrasen är ofullständig/samordnad, eller om namnet redan hör till ett annat `NAME - verb`-led. Separat kategori: finit dative-/rapporteringsverb + slutet mottagarpronomen + fullständigt subjekt + uttryckligt fristående `»` för ett **annat objekt**. Den strukturen får korrigeras, men **inte** när objektmarkör saknas och inte heller med enbart namn när en talare/ett citerat subjekt är tvetydigt.

Den privata genomgången av 929 engelska CHES-kapitel ger **9 + 12 = 21** snäva källkandidater efter syntax-/frasgränskontroller. Detta är *varken* 21 säkerställda fel *eller* 21 verifierade utdataändringar. **Endast** `scripts/danmek_039_english_only.py` uppdateras som den aktiva motorn, med positiv och negativ syntetisk GitHub-CI och utan originalspråkskontroll. [Avgränsad korpusanalys](DANMEK_042_ENGLISH_CLOSED_ADJUNCT_AND_DATIVE_SUBJECTS.md).

## Engelska satsroller

1. Analysera de ursprungliga **engelska CHES-fragmentens ordningsföljd**. Identifiera engelska subjekt, finita verb/predikat, objekt, indirekta objekt, mottagare, prepositioner, inskjutna led, relativsatser, bisatser och satsgränser.
2. Flytta ett identifierat subjekt **före tillhörande verb även vid långt avstånd**. Flera predikat i en vers måste kunna hanteras oberoende. Det får inte finnas en generell maxdistansregel, personnamnsspecialfall eller subjekt-antagande grundat enbart på versnummer eller stor bokstav.
3. Bevara alla övriga engelska ord, pronomen, tempus, satsdelar och interlinjärliknande uttryck så långt möjligt. Modern idiomatisk stil är inte uppgiften. Ändra inte ordval på grund av en extern översättning.
4. **Objekt får aldrig gissas till subjekt.** En grammatisk tvetydighet rapporteras som `UNRESOLVED`; den auktoriserar ingen omflyttning. Testa särskilt transitiva verb, rapporterat tal, sammanhängande och långt avlägsna subjekt, flera satser och samordning.
5. Oönskade PDF-textartefakter såsom fristående `the`/`do` ska endast korrigeras om deras överlagrade metadata särskiljer dem från verkliga engelska ord; inga generella borttagningsregexar.

## En aktuell bibelutgåva — ingen kedja av äldre v2–v8

Tidigare DANMEK-skript och parallella läsare v2–v8 är **historiska prototyper, inte längre styrande implementationer eller låsta redigeringsgrundversioner**. Ingen ny DAG av inbördes importerade legacy-läsare får byggas. Endast `scripts/danmek_039_english_only.py` är den aktiva ingången. Den ska använda **Python-standardbiblioteket och privata CHES-JSON**, inte originalspråksmoduler eller andra DANMEK/CHES-översättningsskript.

Bygg en sammanhängande aktuell utgåva reproducerbart från privata CHES-data. Tidigare utdata behöver inte bevaras som parallella produkter, men **ursprungliga CHES-JSON ska aldrig modifieras eller skrivas över**. Skriv privat resultat atomiskt och kontrollera källintegritet.

Den uppladdade CHES-samlingen innehåller 929 kapitel och 23 144 versposter för 39 GT-böcker. Den innehåller **inte** automatiskt Nya testamentets 27 böcker; en komplett 66-boksbibel kräver faktiskt NT-material. Ingen vers får hittas på eller rekonstrueras som fyllnad.

## Verifiering och informationsskydd

- Den verkliga privata engelska korpusen är utvecklingsunderlag. Endast **syntetisk engelsk testtext** får hamna på offentliga GitHub eller GitHub-hostade Ubuntu Actions.
- Testa att den aktiva Python-modulen **saknar importer av alla `olt_core`, äldre `danmek_0xx`, `ches_0xx` och övriga originalspråksgranskare**. Den enda aktiva DANMEK-styrningsfilen är detta dokument och `data/policy/danmek_039_english_subject_verb_only.json`.
- GitHub Actions PASS är tillräckligt för **kodtesterna** enligt projektägarens arbetssätt, men inte ett språkvetenskapligt påstående att alla CHES-verser är rättade. Skilj på `detected`, `applied` och `unresolved`.
- Äldre `docs/DANMEK_*.md` får endast läsas som historiskt forskningsmaterial. Inga äldre instruktioner som säger `NO_CHANGE` för korrektur, kräver återkommande hebreisk kontroll eller låser gamla läsare är fortfarande bindande.
- Granskad och positivt mottagen provtext är inte automatiskt verifiering av varenda vers. Försäkringar om fullständig grammatik ska baseras på kontrollerade resultat, inte antaganden.
- CHES upphovsrättsligt skyddade källtext får inte läggas i offentliga GitHub, Actions-loggar eller offentliga artefakter. **Publication remains BLOCKED** om erforderliga spridningsrättigheter inte har klarlagts.

## Prioritet mot andra OLT-delprojekt

Denna reset gäller DANMEK:s CHES-baserade **engelska grammatik och läsutgåva**, inte fristående OLT-teologipolicy, forskning om grekiska NT eller källfilers existens i historiska forskningsmappar. Dessa ska däremot aldrig importeras eller användas som beroende i den aktiva engelska DANMEK-motorn.

**Endast denna fil och DANMEK-039-policyfilen styr nästa DANMEK-ändring.**
