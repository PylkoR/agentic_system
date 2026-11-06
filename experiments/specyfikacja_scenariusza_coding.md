# Specyfikacja Scenariusza: Zespołowe Wytwarzanie Oprogramowania (Coding)

## Część 1: Co i w jaki sposób symulujemy?

### Istota symulowanej sytuacji

Symulujemy **cykl deweloperski z jawnym zarządzaniem zależnościami, iteracyjnym testowaniem i debugowaniem**. Zamiast tworzyć pełną aplikację (co przekracza możliwości kognitywne małych modeli), zespół pracuje nad pojedynczym, ściśle wyizolowanym mikrozadaniem programistycznym (np. napisaniem skryptu do walidacji i filtrowania paczki danych JSON). 

Celem eksperymentu jest zbadanie, jak modele 3B radzą sobie z przekazywaniem zależności (wynik jednego agenta jest wejściem dla drugiego) oraz z pętlą sprzężenia zwrotnego (reagowaniem na błędy wykazane w testach).

### Mechanika symulacji (Jak to robimy?)

1. **Mikrozadania i podział kompetencji:** Zadanie jest rozbite na etapy odpowiadające procesowi tworzenia oprogramowania (Projektowanie -> Implementacja -> Testowanie -> Debugowanie). Każdy agent ma dostęp tylko do tego etapu, za który odpowiada.
2. **Sekwencyjność i zależności (Dependency Chain):** System wymusza przepływ pracy. Programista nie może zacząć pisać, póki Architekt nie zdefiniuje szkieletu. Tester pisze testy na podstawie wymagań, a Rewidujący analizuje ewentualne błędy, by zawrócić proces do Programisty.
3. **Symulowane środowisko wykonawcze (Execution Environment):** System na zewnątrz dysponuje "narzędziem" uruchamiającym kod. Agenci nie uruchamiają kodu samodzielnie – po napisaniu kodu i testów, to środowisko eksperymentalne łączy je, uruchamia (np. w izolowanym kontenerze/piaskownicy Pythona) i wstrzykuje wyniki (pass/fail, stack trace) z powrotem do pamięci agentów (konkretnie do Rewidującego).
4. **Pętla poprawy błędów (Feedback Loop):** W przypadku niepowodzenia testów następuje iteracyjna naprawa kodu, weryfikująca zdolność zespołu do poprawnej komunikacji technicznej (wyjaśnienie błędu przez Rewidującego -> modyfikacja kodu przez Programistę).

## Część 2: Role i dane wejściowe (Input) dla zespołu 4 agentów

Każdy z agentów rozpoczyna pracę ze spersonalizowanym promptem, który jasno określa jego specjalizację i ogranicza zakres obowiązków.

### 1. Agent 1: Architekt (Główny Projektant)

* **Rola:** Definiuje struktury danych, nazewnictwo zmiennych oraz sygnatury funkcji (szkielet kodu). Rozwiązuje problem na poziomie architektury, nie implementuje logiki biznesowej.
* **Format danych wejściowych:** Otrzymuje wysokopoziomowy opis wymagań biznesowych (Task Info).
* **Przykład Inputu:**

  > **Rola:** Jesteś Architektem Oprogramowania. Odpowiadasz za projektowanie struktury modułów, bez pisania wewnętrznej logiki.
  > **Wymagania biznesowe:** Moduł `user_validator.py` musi przyjmować listę słowników (użytkowników). Ma usuwać duplikaty na podstawie pola 'email', odrzucać rekordy gdzie 'age' < 18 lub pole nie istnieje, a następnie zwracać przefiltrowaną listę.
  > **Twoje zadanie:** Wygeneruj wyłącznie szkielet kodu w języku Python (definicje klas/funkcji, type hinty oraz docstringi). Zostaw puste ciała funkcji (użyj `pass`).

### 2. Agent 2: Programista (Developer)

* **Rola:** Pisze właściwy kod na podstawie szkieletu. Odbiera również poprawki od Rewidującego w fazie debugowania.
* **Format danych wejściowych:** Szkielet kodu od Architekta + oryginalne wymagania (dla kontekstu) + ewentualne instrukcje naprawcze od Rewidującego w kolejnych iteracjach.
* **Przykład Inputu (Iteracja 1):**

  > **Rola:** Jesteś Programistą (Developer). Twoim zadaniem jest implementacja logiki w przygotowanym szkielecie.
  > **Wymagania biznesowe:** [Skrócony opis walidacji wieku i deduplikacji maili].
  > **Szkielet od Architekta:** 
  > `def filter_adult_users(users: list[dict]) -> list[dict]:`
  > `    """Filtruje uzytkownikow..."""`
  > `    pass`
  > **Twoje zadanie:** Zastąp `pass` poprawną logiką w języku Python. Pamiętaj o obsłudze wyjątków (np. brakujących kluczy w słowniku). Zwróć tylko gotowy kod.

### 3. Agent 3: Tester (QA)

* **Rola:** Opracowuje przypadki testowe w oparciu o wymagania biznesowe. Nie modyfikuje kodu źródłowego.
* **Format danych wejściowych:** Kod stworzony przez Programistę oraz wymagania biznesowe.
* **Przykład Inputu:**

  > **Rola:** Jesteś Inżynierem Jakości (QA). Twoim zadaniem jest napisanie testów jednostkowych do dostarczonego kodu.
  > **Wymagania biznesowe:** [Skrócony opis walidacji].
  > **Kod stworzony przez zespół:** [Zaimplementowany kod Programisty].
  > **Twoje zadanie:** Napisz 3 krótkie testy w bibliotece `pytest`, które sprawdzają: (1) poprawne odrzucanie osób poniżej 18 roku życia, (2) deduplikację takich samych adresów email, (3) obsługę błędu, gdy brakuje klucza 'age'. Zwróć tylko kod testów.

### 4. Agent 4: Rewidujący (Code Reviewer / Debugger)

* **Rola:** Analizuje wyniki wykonania kodu i testów. Pełni rolę debuggera, który tłumaczy błędy techniczne na zaleceń dla Programisty.
* **Format danych wejściowych:** Wyniki uruchomienia testów wstrzyknięte przez środowisko symulacyjne (sukces lub log błędu) oraz kod Programisty.
* **Przykład Inputu (Gdy testy nie przejdą):**

  > **Rola:** Jesteś Rewidującym (Code Reviewer/Debugger). Diagnozujesz przyczyny błędów w kodzie i dajesz wskazówki programiście.
  > **Kod Programisty:** [Zaimplementowany kod].
  > **Wynik testów (Execution Output):** 
  > `FAILED tests/test_validator.py::test_missing_age - KeyError: 'age' at line 12 in filter_adult_users`
  > **Twoje zadanie:** Przeanalizuj zrzut stosu (stack trace). Zidentyfikuj lukę w logice Programisty i wygeneruj jasną, zwięzłą instrukcję (np. użycie metody `.get()` zamiast nawiasów kwadratowych), co musi zmienić w swoim kodzie, aby test przeszedł. Nie pisz całego kodu za niego, wskaż rozwiązanie.