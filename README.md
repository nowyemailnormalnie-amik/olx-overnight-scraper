# OLX Overnight Scraper

Skrypt do znajdowania firm z dużą liczbą ogłoszeń na OLX.pl (>300 aktywnych ogłoszeń).

## 🎯 Cel

Znalezienie 50-100 hurtowni/dropshippingów prowadzących sprzedaż na OLX poprzez losowe próbkowanie profili użytkowników.

## 📋 Wymagania

- Python 3.8+
- Biblioteki: requests, beautifulsoup4

## 🚀 Instalacja

```bash
pip install -r requirements.txt
```

## 💻 Użycie

```bash
python overnight_scraper.py
```

Skrypt zapyta o liczbę godzin działania (domyślnie 8).

## 📊 Parametry

- **Cel**: >300 aktywnych ogłoszeń
- **Miasta**: 10 największych w Polsce
- **Kategorie**: 8 (bez motoryzacji)
- **Checkpoint**: Co 10 sprawdzonych użytkowników
- **Prędkość**: ~200-500 użytkowników/godzinę

## 📁 Pliki wyjściowe

Skrypt automatycznie tworzy/aktualizuje następujące pliki:

- `overnight_checkpoint.csv` - ranking znalezionych firm (nazwa, liczba ogłoszeń, URL)
- `overnight_checkpoint_cache.json` - cache sprawdzonych użytkowników (do wznowienia)
- `overnight_checkpoint_stats.json` - statystyki działania

**Uwaga**: Puste wersje tych plików są dołączone jako przykład. Skrypt je nadpisze podczas działania.

## 🔄 Wznawianie

Skrypt automatycznie wczytuje poprzednie wyniki i pomija już sprawdzonych użytkowników. Możesz uruchomić go wielokrotnie - nie będzie sprawdzał tych samych profili.

## ⚡ Funkcje

- ✅ Losowe próbkowanie (różne kategorie + miasta)
- ✅ Optymalizacja regex (3-5x szybsza niż BeautifulSoup)
- ✅ Checkpoint co 10 użytkowników (bezpieczne przy crashu)
- ✅ Resume capability (cache sprawdzonych user_id)
- ✅ Ranking na żywo podczas działania
- ✅ Ctrl+C w każdej chwili (progress zapisany)

## 📝 Notatki

- Skrypt używa **losowego próbkowania** - nie znajdzie wszystkich firm na OLX, ale znajdzie wystarczająco dużo
- Im dłużej działa, tym więcej firm znajduje
- Użytkownicy z większą liczbą ogłoszeń mają większą szansę na odkrycie (ich ogłoszenia są w wielu kategoriach)
- OLX nie ma oficjalnego API do listowania użytkowników - to jedyna metoda

## 🔍 Jak to działa

1. Losuje kategorię + miasto + stronę
2. Pobiera listę ogłoszeń (regex)
3. Wchodzi losowo w ~25% ogłoszeń
4. Wyciąga user_id z ogłoszenia (regex)
5. Sprawdza profil użytkownika (1 request, regex)
6. Jeśli >300 ogłoszeń → dodaje do rankingu
7. Zapisuje checkpoint co 10 użytkowników
8. Powtarza aż do limitu czasu

## ⚠️ Rate Limiting

- 0.2s opóźnienie między requestami
- Random selection unika wzorców
- Jeden request per profil użytkownika

---

## 📦 Folder `istotne_skrypty` - Narzędzia pomocnicze

Po zebraniu firm za pomocą overnight_scraper, użyj narzędzi z folderu `istotne_skrypty` do dalszej pracy:

### 📧 extract_emails.py
**Wyciąga emaile z profili OLX znalezionych przez scraper**
- **Input**: `overnight_checkpoint.csv` (ranking firm)
- **Output**: CSV z emailami firm
- **Czas**: ~0.5s na firmę
- **Zależności**: requests, beautifulsoup4

### 🏢 scrape_baselinker.py
**Zbiera emaile hurtowników z BaseLinker.pl (alternatywne źródło kontaktów)**
- **Input**: Brak (scrape'uje stronę BaseLinker)
- **Output**: `baselinker_emails_[timestamp].csv`
- **Status**: ✅ Już zebrane 20 emaili w `baselinker_emails.csv`

### 📩 EMAIL_GOTOWY_AMADEUSZ.txt
**Szablon cold emaila RODO-compliant do kampanii B2B**
- Profesjonalny subject + value proposition (AI kategoryzator OLX)
- RODO-compliant footer (opt-out, dane firmy)
- Personalizacja: {IMIE}, {NAZWA_FIRMY}

### 📊 baselinker_emails.csv
**Gotowa baza 20 emaili hurtowników z BaseLinker.pl**
- Format: ID, Nazwa, Email, Źródło
- Status: ✅ Kompletne, gotowe do kampanii

### 🔄 Workflow (Kompletny proces)
1. **Znajdź firmy**: Uruchom `overnight_scraper.py` (działa automatycznie w GitHub Actions)
2. **Wyciągnij emaile**: `python extract_emails.py` → CSV z emailami firm OLX
3. **Backup**: Użyj `baselinker_emails.csv` (20 gotowych kontaktów)
4. **Kampania**: Skopiuj tekst z `EMAIL_GOTOWY_AMADEUSZ.txt`
5. **Wyślij**: Import CSV do systemu mailingowego

---
