# 🌙 OLX Overnight Scraper - GitHub Actions

Automatyczny scraper działający w chmurze GitHub Actions.

## 📊 Limity GitHub Actions (darmowe konto)

- ✅ **2000 minut/miesiąc** dla prywatnych repo
- ✅ **Unlimited** dla publicznych repo  
- ⚠️ **Max 6 godzin na pojedynczy run** (hard limit)

## 🚀 INSTRUKCJA KROK PO KROKU

### KROK 1: Utwórz nowe repo na GitHub

1. Wejdź na: https://github.com/new
2. **Repository name**: `olx-overnight-scraper`
3. **Public/Private**: Wybierz **Public** (unlimited minuty) LUB **Private** (2000 min/miesiąc)
4. ❌ **NIE** zaznaczaj "Add README", "Add .gitignore" ani "Choose license"
5. Kliknij **Create repository**

### KROK 2: Push kodu do GitHub

Otwórz PowerShell w folderze `overnight_scraper_package` i wykonaj:

```powershell
# Inicjalizuj git (jeśli jeszcze nie było)
git init

# Dodaj wszystkie pliki
git add .

# Pierwszy commit
git commit -m "Initial commit: OLX overnight scraper"

# Podłącz do repo (ZAMIEŃ NA SWÓJ URL!)
git remote add origin https://github.com/nowyemailnormalnie-amik/olx-overnight-scraper.git

# Wypchnij kod
git branch -M main
git push -u origin main
```

**⚠️ GitHub poprosi o logowanie:**
- Username: `nowyemailnormalnie-amik`
- Password: **Musisz użyć Personal Access Token** (nie hasło!)

**Jak utworzyć token (jeśli nie masz):**
1. GitHub → Settings (prawy górny róg) → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Zaznacz: `repo` (full control)
4. Generate token
5. **SKOPIUJ TOKEN** (już się nie pokaże!)

### KROK 3: Sprawdź czy wszystko jest na GitHub

1. Wejdź na: https://github.com/nowyemailnormalnie-amik/olx-overnight-scraper
2. Powinieneś zobaczyć wszystkie pliki:
   - overnight_scraper.py
   - requirements.txt
   - README.md
   - .github/workflows/run_scraper.yml
   - itp.

### KROK 4: Uruchom scraper w chmurze

1. Na stronie repo kliknij zakładkę **Actions** (góra)
2. Kliknij **I understand my workflows, go ahead and enable them** (jeśli się pojawi)
3. Po lewej stronie zobaczysz **OLX Overnight Scraper**
4. Kliknij na niego
5. Po prawej kliknij przycisk **Run workflow** (szary dropdown)
6. Wpisz ile godzin (np. `5` - pamiętaj max to 5.5h)
7. Kliknij zielony **Run workflow**

### KROK 5: Śledź postęp

1. Odśwież stronę - zobaczysz żółty status "running"
2. Kliknij na nazwę runa (np. "OLX Overnight Scraper #1")
3. Kliknij na job "scrape"
4. Zobaczysz live logi - progress scrapowania w czasie rzeczywistym!

### KROK 6: Pobierz wyniki

**Opcja A - Artifacts (zawsze działa):**
1. Po zakończeniu runa (zielony check ✓)
2. Scroll w dół strony runa
3. Sekcja "Artifacts" - kliknij **scraping-results**
4. Pobierze się ZIP z CSV/JSON

**Opcja B - Z repo (jeśli auto-commit zadziałał):**
1. Wróć do głównej strony repo
2. Pliki `overnight_checkpoint.csv` itp. będą zaktualizowane
3. Możesz je po prostu pobrać stamtąd

### KROK 7: Wznów (jeśli chcesz więcej)

Dzięki resume capability możesz uruchomić ponownie:
1. Actions → Run workflow → wpisz np. `3`
2. Skrypt wczyta cache i będzie kontynuował (nie sprawdzi tych samych userów)

## 🎯 Strategia dla >6h scrapowania

Ponieważ GitHub ma limit 6h, możesz:

**Opcja 1: Kilka runów (POLECAM)**
- Run 1: 5h (safe margin)
- Run 2: 5h (kontynuuje dzięki cache)
- Run 3: 5h (dalej kontynuuje)
- = 15h total scrapowania bez duplikatów!

**Opcja 2: Schedule (automatycznie co noc)**
Mogę dodać cron do workflow - będzie działał sam każdej nocy.

## ⚠️ Ważne uwagi

- **Max 6h** to twardy limit GitHub - potem run się zabije
- **Resume działa** - możesz uruchomić wielokrotnie, cache się zachowuje
- **Public repo** = unlimited minuty (nie zjedziesz limitu 2000 min)
- **Logi są publiczne** jeśli repo public - upewnij się że nie ma haseł w kodzie
- **Artifacts** trzymane 30 dni, potem się usuwają

## 🐛 Troubleshooting

**"Permission denied" przy push:**
- Użyj Personal Access Token zamiast hasła

**Workflow nie pojawia się w Actions:**
- Upewnij się że plik jest w `.github/workflows/run_scraper.yml`
- Sprawdź czy push się udał (`git log --oneline`)

**Run się kończy po 6h:**
- To normalne - jest limit. Uruchom ponownie, resume zadziała.

**"Quota exceeded":**
- Zmieniłeś na private repo i zużyłeś 2000 min. Zmień na public LUB poczekaj do następnego miesiąca.

## 📞 Dalsze kroki

Po wykonaniu wszystkich kroków napisz mi:
- ✅ "Repo utworzone"
- ✅ "Push się udał"  
- ✅ "Run wystartował"
- ✅ "Widzę logi"

I będziemy kontynuować!
