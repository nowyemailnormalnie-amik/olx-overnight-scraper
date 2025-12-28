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
