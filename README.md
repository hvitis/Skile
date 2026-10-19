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

---

## Struktura repozytorium

```text
Skile/
├── README.md
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

## Licencja

Zawartość repozytorium jest udostępniana na warunkach licencji MIT. Szczegóły licencyjne poszczególnych skilli znajdują się w ich nagłówkach metadanych.
