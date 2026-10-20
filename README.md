# Skile

Kolekcja wyspecjalizowanych umiejętności (skills) dla asystentów i agentów AI zgodnych ze specyfikacją `SKILL.md` (agentskills.io).

Każdy skill definiuje precyzyjne zasady, procesy wykonawcze, wzorce zachowań lub szablony, które pozwalają agentom realizować złożone zadania z zachowaniem wysokiego standardu inżynieryjnego i edytorskiego.

---

## Dostępne umiejętności

### Kategoria: Research (`research/`)

- **domain-modeling** (`research/domain-modeling/SKILL.md`)
  - **Cel:** Aktywne modelowanie i doskonalenie modelu dziedziny projektu podczas projektowania i programowania.
  - **Zastosowanie:** Weryfikacja spójności terminologii biznesowej, identyfikacja dwuznaczności w języku domenowym, prowadzenie słowników pojęć (`GLOSSARY.md` / `GLOSSARY-MAP.md`) oraz rejestrowanie nieoczywistych, trudnych do odwrócenia decyzji architektonicznych (`ADR`).
  - **Materiały pomocnicze:**
    - `GLOSSARY-FORMAT.md` - format i reguły tworzenia słownika pojęć domenowych.
    - `ADR-FORMAT.md` - kryteria i minimalistyczny szablon Architectural Decision Record.

- **deep-search-into-md** (`research/deep-search-into-md/SKILL.md`)
  - **Cel:** Przeprowadzanie dogłębnego researchu i syntezy wiedzy do pojedynczego, kumulatywnie rozbudowywanego dossier w formacie Markdown.
  - **Zastosowanie:** Analiza przełomów naukowo-technicznych, trudnych zagadnień inżynieryjnych lub materiałów źródłowych (nagrania wideo, publikacje). Wymusza precyzję historyczną, unikanie równań na rzecz czytelnej dekonstrukcji etapów fizycznych/mechanicznych oraz rozróżnianie rozwiązanych problemów od aktywnych wyzwań i nierozwiązanych hipotez.

### Kategoria: Writing (`writing/`)

- **nie-pisz-jak-ai** (`writing/nie-pisz-jak-ai/SKILL.md`)
  - **Cel:** Audyt i redakcja tekstów w języku polskim w celu eliminacji charakterystycznych cech tekstów generowanych przez modele LLM („AI-izmów”).
  - **Zastosowanie:** Usuwanie anglojęzycznych kalk składniowych, przesadnej symetrii, sztucznych wstępów i podsumowań, fałszywej emonacjonalności oraz korporacyjnego żargonu. Oferuje trzy tryby pracy: audyt bez modyfikacji tekstu (`detect`), przeredagowanie tekstu (`rewrite`) oraz precyzyjne nanoszenie poprawek w pliku (`edit`).

- **blog-writing-guide** (`writing/blog-writing-guide/SKILL.md`)
  - **Cel:** Standard tworzenia, recenzowania i ulepszania wpisów na blogi inżynieryjne (oparty na wytycznych technicznego bloga Sentry).
  - **Zastosowanie:** Tworzenie artykułów z perspektywy praktyka (senior engineera), skupionych na realnych problemach, architekturze, kompromisach technologicznych i wyciągniętych wnioskach. Eliminuje marketingowy szum, frazesy i sztampowe struktury generowane przez AI.

### Kategoria: Cooking (`cooking/`)

- **recipe-into-table** (`cooking/recipe-into-table/SKILL.md`)
  - **Cel:** Zamiana przepisu z dowolnego źródła na jeden, zawsze ten sam format: drukowaną tabelę w stylu Cooking for Engineers (składniki po lewej, każda czynność obejmuje składniki, które łączy), zapisaną jako jednostronicowy PDF.
  - **Zastosowanie:** Przepisy z wklejonego tekstu, stron WWW (dane schema.org), filmów z YouTube i innych serwisów (opis, rozdziały, napisy), plików PDF, DOCX, ODT i EPUB oraz zdjęć kartek z przepisami. Każda strona dostaje motyw zależny od rodzaju dania: ikonę liniową, paletę kolorów, deseń w tle i girlandy w narożnikach. Kilka przepisów trafia do jednego PDF-a, po jednym na stronę. Karta ma zawsze format A4, a cała jej treść jest po polsku: przepis zostaje przetłumaczony, a ilości przeliczone na gramy, mililitry i stopnie Celsjusza.
  - **Materiały pomocnicze:**
    - `scripts/fetch_recipe.py` – pobiera tekst przepisu z adresu URL, filmu lub pliku.
    - `scripts/render_recipe.py` – układa tabelę z drzewa przepisu (JSON) i renderuje HTML oraz PDF.
    - `scripts/recipe_theme.py` – ikony, palety kolorów i ornamenty dla 17 rodzajów dań.

---

## Struktura repozytorium

```text
Skile/
├── README.md
├── cooking/
│   └── recipe-into-table/
│       ├── SKILL.md
│       └── scripts/
│           ├── fetch_recipe.py
│           ├── recipe_theme.py
│           └── render_recipe.py
├── research/
│   ├── deep-search-into-md/
│   │   └── SKILL.md
│   └── domain-modeling/
│       ├── ADR-FORMAT.md
│       ├── GLOSSARY-FORMAT.md
│       ├── SKILL.md
│       └── agents/
│           └── openai.yaml
└── writing/
    ├── blog-writing-guide/
    │   └── SKILL.md
    └── nie-pisz-jak-ai/
        └── SKILL.md
```

---

## Standard i format pliku

Każda umiejętność jest zorganizowana w dedykowanym katalogu zawierającym plik `SKILL.md`. Plik ten posiada nagłówek YAML frontmatter zgodny ze standardem agentskills.io:

```yaml
---
name: nazwa-skilla
description: Zwięzły opis przeznaczenia skilla i warunków jego wywołania.
---
```

W treści dokumentu znajdują się bezpośrednie instrukcje dla agenta: rola, kryteria decyzyjne, ograniczenia, schematy postępowania krok po kroku oraz przykłady oczekiwanych rezultatów.

---

## Jak używać

Umiejętności z tego repozytorium można wdrożyć w dowolnym środowisku wspierającym instrukcje dla agentów:

1. **Claude Code / Codex:**
   - Skopiuj wybrany katalog ze skillem (np. `writing/nie-pisz-jak-ai`) do katalogu umiejętności skonfigurowanego w Twoim narzędziu (np. `~/.agents/skills/` lub folderu roboczego projektu).

---

## Przykład użycia: recipe-into-table

Od linku, filmu albo zdjęcia kartki do polskiej karty z przepisem na stronie A4, którą można powiesić w kuchni. Na górze karty jest ikona rodzaju dania, tytuł, liczba porcji i czasy. Pod nimi znajduje się tabela, a niżej wskazówki i źródło. Kolory, deseń w tle i girlandy w narożnikach zależą od rodzaju dania.

Tabelę czyta się od lewej do prawej: składniki są w pierwszej kolumnie, a każda czynność zajmuje dokładnie te wiersze, które łączy. Gałęzie (np. masa maślana i suche składniki) schodzą się w prawo, aż do ostatniego, ciemnego pola z końcowym krokiem.

### 1. Zainstaluj skill

```bash
cp -r cooking/recipe-into-table ~/.claude/skills/
```

Do pobierania przepisów z filmów potrzebny jest `yt-dlp`, a do PDF-ów `pdftotext` (pakiet poppler). Plik PDF powstaje w Chrome, Chromium, Edge albo WeasyPrint. Bez nich skill oddaje plik HTML gotowy do wydruku z przeglądarki.

```bash
brew install yt-dlp poppler        # macOS; na Linuksie: pip install yt-dlp, apt install poppler-utils
```

### 2. Poproś agenta o tabelę

```text
Zrób mi tabelę z tego przepisu: https://www.allrecipes.com/recipe/10813/best-chocolate-chip-cookies/
Zamień ten film na kartę z przepisem do druku: https://www.youtube.com/watch?v=loqCY9b7aec
Przerób wszystkie przepisy z ~/Downloads/babcia.pdf na tabele, w jednym PDF-ie
[zdjęcie kartki z przepisem] Zrób z tego tabelę do powieszenia w kuchni
```

### 3. Co robi agent

1. **Pobiera przepis.** `fetch_recipe.py` wyciąga ze strony dane schema.org (dokładne składniki, czasy, liczbę porcji), z filmu opis, rozdziały i napisy, a z pliku sam tekst. Zdjęcia agent odczytuje bezpośrednio. Jeśli opis filmu linkuje do spisanego przepisu, agent pobiera też ten przepis i bierze z niego ilości.
2. **Spisuje składniki i kroki**, żeby żaden nie zginął po drodze.
3. **Buduje drzewo przepisu w JSON.** Składniki są liśćmi, czynności węzłami, a ostatni krok korzeniem. Pole `dish_type` wybiera ikonę i kolory. Całą treść agent pisze po polsku, z ilościami w gramach, mililitrach, łyżkach i łyżeczkach.
4. **Renderuje stronę** poleceniem `render_recipe.py przepis.json --pdf`.
5. **Sprawdza PDF.** Każdy przepis ma mieścić się na jednej stronie, nic nie może być ucięte, a każda czynność musi stać obok właściwych składników.
6. **Oddaje PDF** razem z plikami JSON i HTML. Poprawki („piecz 5 minut dłużej”, „zrób podwójną porcję”) nanosi w JSON i renderuje stronę ponownie.

### 4. Skrypty uruchamiane ręcznie

Oba skrypty działają też bez agenta (Python 3.8+, tylko biblioteka standardowa):

```bash
cd cooking/recipe-into-table

# Pobranie przepisu ze strony, filmu lub pliku (wynik w Markdownie)
python3 scripts/fetch_recipe.py "https://www.allrecipes.com/recipe/10813/best-chocolate-chip-cookies/"
python3 scripts/fetch_recipe.py "https://www.youtube.com/watch?v=loqCY9b7aec" -o /tmp/film.md
python3 scripts/fetch_recipe.py ~/Downloads/przepis.pdf

# Render drzewa przepisu do PDF (A4 w poziomie; --portrait dla pionu)
python3 scripts/render_recipe.py ~/przepisy/ciasteczka.json --pdf

# Kilka przepisów w jednym PDF-ie, po jednym na stronę
python3 scripts/render_recipe.py ~/przepisy/ciasteczka.json ~/przepisy/makaron.json -o ~/przepisy/ksiazka.html --pdf
```

Format drzewa przepisu (z kompletnym przykładem), zasady modelowania, reguły polskiej treści i listę rodzajów dań opisuje [`cooking/recipe-into-table/SKILL.md`](cooking/recipe-into-table/SKILL.md).

---

## Licencja

Zawartość repozytorium jest udostępniana na warunkach licencji MIT. Szczegóły licencyjne poszczególnych skilli znajdują się w ich nagłówkach metadanych.
