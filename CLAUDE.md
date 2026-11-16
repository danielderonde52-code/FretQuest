# FretQuest — overdracht en werkafspraken

FretQuest is een oefenapp voor de gitaarhals, gebouwd voor en met Daniël. Eén HTML-bestand, Nederlandse interface,
gehost op GitHub Pages (`main`, root) en als PWA geïnstalleerd op zijn Android-telefoon, die hij **liggend** gebruikt.
Live: https://danielderonde52-code.github.io/FretQuest/

## Werkafspraken met Daniël
- Antwoord in het **Nederlands**, kort en gestructureerd. Hij werkt meestal vanaf zijn telefoon en gebruikt GitHub niet zelf.
- Elke wijziging gaat **direct naar `main`** (Pages publiceert dan binnen een à twee minuten). Geen branches of PR's, tenzij hij erom vraagt.
- Bij grotere keuzes (welke oefeningen, welke opzet) eerst kort voorleggen; kleine dingen gewoon doen en melden.
- Meld na elke wijziging: wat er veranderd is, wat getest is, en wat **niet** getest kon worden (geluid, echte microfoon, echte telefoon).
- Hij geeft feedback na echt gebruik en draait dingen terug als ze niets toevoegen. Bouw dus klein en omkeerbaar.
- De app moet deelbaar zijn met anderen: geen verwijzingen naar cursussen of merken (eerder zijn verwijzingen naar "LoG" verwijderd).
- Stijl: serieus en klassiek met een licht fantasy-accent, niet gimmicky. Donkergroen met goud, letters Marcellus / Marcellus SC / Spectral,
  nootkleuren "Edelmetaal" (grondtoon, terts, kwint, septiem, overige). Fretmarkeringen zijn ronde stippen.

## Bestanden
| Bestand | Wat |
|---|---|
| `index.html` | **De hele app**: omhullende pagina + stijl + markup + één `<script>` (IIFE). Dit is de bron; bewerk dit bestand direct. |
| `theorie.html` | De handleiding "De theorie achter de hals". Losstaand; bevat een **eigen kopie** van de theorie-, hals- en lescode uit de app. |
| `sw.js`, `manifest.webmanifest`, `icon-*.png` | PWA. De service worker is network-first (cache `fretquest-v2`); een nieuwe versie komt dus vanzelf binnen. |
| `dev/test.py` | Rooktest (Playwright). **Draai na elke wijziging**: `python3 dev/test.py`. |
| `dev/artifact.py` | Leidt uit `index.html` de bron voor een Claude-artifact af (voorvertoning in de chat). |
| `dev/gehoor-ronde2.patch` | Teruggedraaide code van gehoor ronde 2 (zie onder), ter referentie. |

Na een wijziging: `node --check` op het script (of gewoon `dev/test.py`), commit, push naar `main`.
Wie ook een artifact-voorvertoning wil: `python3 dev/artifact.py > bestand.html` en dat publiceren.

## Opbouw van `index.html`
- **Theorie**: `F` (22 materialen: `iv` intervallen, `g` groep, `par`, `ch` kleurnoten, `lab` afwijkende trapnamen),
  `getLens(fid,root,lens)` met lenzen `all`, `pos` (5 CAGED-posities), `nps` (3 noten per snaar), `set` (snaarset, alleen complete drieklankvormen), `str` (één snaar).
  Nootnamen volgen de toonsoort: `spell`, `nn`, `rn`. Kleurklasse per trap: `ivClass`.
- **Hals**: `board(o)` tekent de SVG-hals (stippen, vensters, links, bijschrift). `nd`, `mk`, `key` zijn de noot-helpers.
- **Geluid**: `Au` (additieve synth met gecachte buffers; `note`, `seq`, `chord`, `drone`, `hush`). **Microfoon**: `Mic` + `makeEngine`
  (McLeod Pitch Method met aanslagdetectie); een gehoorde noot komt binnen via `heard(midi,s,f)`. `run.muteUntil` voorkomt dat de app zijn eigen voorbeeld hoort.
- **Oefeningen**: object `DR`. Elke oefening heeft `n`, `d`, vlaggen (`free`, `gt` gitaar, `ear` gehoor, `nolens`, `fixlens`, `jam`) en `make()`
  dat een vraag teruggeeft van type `choice`, `tap` of `play`. Ronde: `startRound` → `nextQ` → `finish` → `finishRound`.
  Huidige oefeningen: naam, vind, trap, zoek, bouw, herken, wissel (scherm); hoor, hvind (gehoor); hspeel (gehoor + gitaar); gnoot, gtrap, gloop, gwissel, jam (gitaar).
- **Leerpad**: `STAGES` (10 stappen, elk met `dr` = lijst van `[oefening, materiaal, lens]`), `LESSONS` (uitleg per stap: `h`, `p`, `b()` = diagrammen),
  `HOW` (denkstap per oefening). **Regel:** alles wat een oefening kan vragen, moet in de uitleg van die stap staan. "Welke is dit?" kiest uit de hele groep van het materiaal.
- **Voortgang** (localStorage-sleutel `halskaart.v1`, niet hernoemen): per oefening de laatste 20 antwoorden `[ok,ms]`; `ms=-1` is niet geklokt.
  Niveaus `LVL` = Nieuw, Verkennen, Groeiend, Stevig, Vlot (`level(k)`), richttijden in `LIM`, spaced repetition in `review`/`isDue`.
  `plan()` stelt de dagkaarten samen (Herhalen, Nieuw/Vooruitkijken, Verdiepen, Afwisseling, Op gehoor, Met de gitaar); `ses…` is de sessie van tien minuten.
- **Telefoon liggend**: klasse `html.pl`; tijdens een ronde (`body.running`) is `#prRun` een schermvullende grid zonder scrollen. Grote opdracht via `q.big` (`#prBig`).
- **Rondleiding**: `TOUR` + `tourGo`. Start eenmalig zolang `ui.tour < 2`; verhoog dat getal om hem voor iedereen opnieuw te tonen.
- **Testhaak**: `window.__hk` geeft de belangrijkste interne objecten door aan `dev/test.py`.

## Ontwerpkeuzes die Daniël bewust heeft gemaakt
- **Geen halen of falen.** Niveaus in plaats van een norm; traag antwoorden wordt niet bestraft; het plan is geen poort ("alles staat open").
  De richttijd is ruim en telt het vinden van de knop mee.
- **Het eerste antwoord van een ronde wordt niet geklokt** (telefoon draaien, oriënteren).
- **Aantal vragen per ronde** is per oefening instelbaar (5 tot 50).
- **Vind de noot**: gevonden noten blijven zichtbaar; de hele hals tot fret 15 telt; een tik binnen 450 ms na een nieuwe vraag wordt genegeerd.
- **Hoor en vind / Hoor en speel**: één omcirkelde grondtoon is het vertrekpunt en klinkt eerst.
- **Gitaaroefeningen**: de opdracht staat groot in beeld; de hals alleen als hij iets toevoegt.
- **Gehoor**: puur luisteren met koptelefoon is de basis; spelen en zingen komen daar bovenop.
- **Gehoor ronde 2 is geprobeerd en teruggedraaid** (Welk akkoord, Welke kleur, Naspelen): voegde volgens Daniël in gebruik weinig toe.
  Niet opnieuw voorstellen zonder dat hij erom vraagt.

## Wat ik (Claude) niet kan controleren
Hoe het klinkt, hoe de microfoon zich gedraagt met een echte gitaar (lage E, de halve tel vasthouden bij "Landen op de drone"),
hoe het er op de echte telefoon uitziet, en of de Google-lettertypen laden (in de testomgeving geblokkeerd). Vraag Daniël daarnaar.

## Open ideeën (geen van alle toegezegd)
"Zing de trap" (overlapt mogelijk met zijn aparte app EarQuest), akkoordwissels, metronoom en sequenties bij "Loop de vorm",
hals tot fret 22 en drop D, export/import van voortgang, CAGED "alleen de greep" en een oefening "Bouw de greep", tikbare lesdiagrammen.
Nog te horen van Daniël na gebruik: geluidskwaliteit en drone-volume, of de richttijden goed voelen, of open snaren in "Vind de noot" moeten blijven.

## De handleiding bijwerken
`theorie.html` wordt met de hand bijgewerkt. Figuren verwijzen met `data-fig="L<stap>.<blok>.<diagram>"` naar de `LESSONS`-kopie **in dat bestand zelf**,
of met een naam naar `FIG`. Verandert de theorie of de uitleg in de app, werk dan de tekst hier ook bij en controleer of de kopie nog klopt.

## Commits
Commit als `Claude <noreply@anthropic.com>`, korte Nederlandse boodschap, en volg de attributieregels van de sessie.
