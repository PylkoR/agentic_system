# Specyfikacja Scenariusza: Rozproszona Diagnostyka Awarii (Root Cause Analysis)

## Część 1: Co i w jaki sposób symulujemy?

### Istota symulowanej sytuacji
Symulujemy **proces grupowego rozwiązywania problemu w warunkach głębokiej asymetrii informacji**. Scenariuszem bazowym jest nagła awaria w infrastrukturze Smart Home / IoT (Internet of Things). Doszło do incydentu (np. zablokowanie systemu i wyzwolenie alarmu), a celem zespołu agentów jest ustalenie chronologii wydarzeń i zidentyfikowanie przyczyny źródłowej (Root Cause). 

Kluczowym założeniem jest to, że żaden z agentów nie dysponuje pełnym obrazem sytuacji. Aby rozwiązać problem, muszą oni wymienić się krytycznymi fragmentami informacji, połączyć je w logiczny ciąg przyczynowo-skutkowy i wyeliminować fałszywe tropy.

### Mechanika symulacji (Jak to robimy?)
1. **Środowisko statyczne i "odłączone":** Ze względu na ograniczenia kognitywne małych modeli (klasy 3B), agenci nie wykonują aktywnych zapytań do zewnętrznych baz danych ani nie przeszukują internetu. Cały niezbędny kontekst (tzw. stan lokalny) jest im wstrzykiwany na samym początku w postaci krótkich, tekstowych wycinków logów.
2. **Narzucenie ról i specjalizacji:** Każdy model otrzymuje ścisłą "personę", która determinuje, na jakie dane zwraca uwagę i za co odpowiada.
3. **Wymuszona iteracyjność (Kroki):** Proces diagnostyczny jest podzielony na określoną liczbę tur (np. maksymalnie 10 iteracji). W każdej turze agenci analizują swoje dane, generują wnioski i przekazują je dalej (zgodnie z badanym paradygmatem). Po osiągnięciu konsensusu, system musi wygenerować końcowy raport w ustrukturyzowanym formacie (np. JSON).
4. **Ukryta zagadka (Scenariusz incydentu):** Scenariusz jest skonstruowany tak, by wymagał połączenia 3 faktów. *Przykład:* Zewnętrzny atak brute-force (widoczny dla Agenta Bezpieczeństwa) powoduje przeciążenie bramki sieciowej (widoczne dla Agenta Sieciowego), co z kolei aktywuje protokół awaryjnego ryglowania drzwi i alarm (widoczne dla Agenta Sensorycznego).

---

## Część 2: Role i dane wejściowe (Input) dla zespołu 4 agentów

Każdy z agentów na starcie symulacji otrzymuje precyzyjnie skonstruowany prompt systemowy. Składa się on z definicji roli, nadrzędnego celu oraz wycinka logów systemowych.

### 1. Agent 1: Główny Koordynator (Planista / Lider)
* **Rola:** Zarządzanie procesem diagnostycznym. Koordynator nie posiada bezpośredniego dostępu do logów technicznych. Jego zadaniem jest zbieranie ustaleń od pozostałych ekspertów, łączenie faktów, zadawanie pytań pomocniczych oraz sformułowanie końcowej przyczyny awarii.
* **Format danych wejściowych:** Otrzymuje wysokopoziomowy opis problemu zgłoszony przez użytkownika (tzw. bilet wsparcia technicznego).
* **Przykład Inputu:**
  > **Rola:** Jesteś Głównym Koordynatorem zespołu diagnostycznego. Twoim celem jest ustalenie przyczyny awarii na podstawie raportów od ekspertów.
  > **Zgłoszenie Użytkownika:** "O godzinie 23:15 system alarmowy w moim domu włączył się bez powodu. Drzwi frontowe zablokowały się na głucho, a aplikacja mobilna pokazywała błąd połączenia z centralą. Musiałem zresetować zasilanie."
  > **Twoje zadanie:** Poproś ekspertów o analizę ich logów z okolic godziny 23:15, znajdź powiązania i wygeneruj końcowy raport.

### 2. Agent 2: Ekspert ds. Sieci (Network Agent)
* **Rola:** Analiza ruchu sieciowego, opóźnień i komunikacji między usługami.
* **Format danych wejściowych:** Zestawienie kilku linijek logów z routera lub bramki IoT (API Gateway).
* **Przykład Inputu:**
  > **Rola:** Jesteś Ekspertem ds. Sieci. Odpowiadasz za analizę ruchu sieciowego.
  > **Lokalne Obserwacje (Logi Bramki IoT):**
  > `23:14:45 - INFO - [API] Normal traffic load.`
  > `23:14:50 - WARN - [API] Spike detected. Incoming requests: 500/sec from IP 185.12.X.X.`
  > `23:14:52 - ERROR - [Router] MQTT Broker Timeout. Dropping packets.`
  > `23:15:01 - INFO - [Router] Connection restored.`
  > **Twoje zadanie:** Przeanalizuj powyższe logi i poinformuj zespół o wykrytych anomaliach.

### 3. Agent 3: Ekspert ds. Sensoryki (Sensor Agent)
* **Rola:** Monitorowanie stanu urządzeń końcowych (czujników, zamków, termostatów) oraz interpretacja ich zachowania.
* **Format danych wejściowych:** Logi sprzętowe z urządzeń Z-Wave/Zigbee.
* **Przykład Inputu:**
  > **Rola:** Jesteś Ekspertem ds. Sensoryki. Monitorujesz stan fizycznych urządzeń w systemie.
  > **Lokalne Obserwacje (Logi Urządzeń):**
  > `23:14:48 - [Front_Door_Lock] Status: CLOSED, Battery: 82%`
  > `23:14:55 - [Front_Door_Lock] WARNING: Lost heartbeat with Gateway.`
  > `23:14:56 - [Front_Door_Lock] ACTION: Executing 'Failsafe_Lockdown' protocol.`
  > `23:15:00 - [Alarm_Siren] TRIGGERED by Front_Door_Lock (Reason: System isolation).`
  > **Twoje zadanie:** Zinterpretuj zachowanie sprzętu i przekaż zespołowi, co doprowadziło do uruchomienia alarmu z perspektywy urządzeń.

### 4. Agent 4: Ekspert ds. Bezpieczeństwa (Security Agent)
* **Rola:** Weryfikacja audytów bezpieczeństwa, prób logowania i uprawnień użytkowników.
* **Format danych wejściowych:** Logi serwisu autoryzacyjnego (Auth Service).
* **Przykład Inputu:**
  > **Rola:** Jesteś Ekspertem ds. Bezpieczeństwa. Analizujesz próby dostępu i potencjalne naruszenia procedur.
  > **Lokalne Obserwacje (Logi Autoryzacji):**
  > `23:14:48 - [Auth] User: admin - Login attempt from IP 185.12.X.X - FAILED (Wrong Password)`
  > `23:14:49 - [Auth] User: admin - Login attempt from IP 185.12.X.X - FAILED (Wrong Password)`
  > `23:14:50 - [Auth] ALARM: Brute-force attack detected on account 'admin'.`
  > `23:14:51 - [Auth] ACTION: Temporarily banning IP 185.12.X.X and forcing session disconnects.`
  > **Twoje zadanie:** Oceń powyższe logi pod kątem zagrożeń i poinformuj zespół o podjętych przez system akcjach bezpieczeństwa.