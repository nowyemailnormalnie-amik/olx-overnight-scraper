"""
OVERNIGHT SCRAPER - Znajdź firmy z >300 ogłoszeń działając przez noc
=====================================================================

Strategia:
1. Iteruj po kategoriach × największe miasta Polski
2. Dla każdego ogłoszenia → wyciągnij user_id
3. Sprawdź profil użytkownika (cache żeby nie powtarzać)
4. Jeśli >300 ogłoszeń → zapisz
5. Checkpoint co 10 użytkowników
6. Ranking na bieżąco
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import csv
import json
import random
import os
from datetime import datetime
from collections import defaultdict

class OvernightScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Największe miasta w Polsce
        self.cities = [
            'warszawa', 'krakow', 'wroclaw', 'poznan', 'gdansk',
            'szczecin', 'bydgoszcz', 'lublin', 'katowice', 'bialystok'
        ]
        
        # Kategorie (bez motoryzacji!)
        self.categories = [
            'elektronika',
            'moda',
            'dom-ogrod',
            'dla-dzieci',
            'sport-hobby',
            'muzyka-edukacja',
            'zwierzeta',
            'praca',
        ]
        
        # Stan
        self.checked_users = set()  # user_id już sprawdzonych
        self.found_businesses = {}  # user_id -> {name, ads_count, url}
        
        self.stats = {
            'ads_checked': 0,
            'users_checked': 0,
            'businesses_found': 0,
            'start_time': datetime.now(),
        }
        
    def load_checkpoint(self):
        """Wczytaj poprzedni checkpoint żeby kontynuować"""
        print("\n🔄 Sprawdzam poprzednie wyniki...")
        
        # Wczytaj found_businesses z CSV
        csv_file = "overnight_checkpoint.csv"
        if os.path.exists(csv_file):
            try:
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        user_id = row['User_ID']
                        self.found_businesses[user_id] = {
                            'name': row['Nazwa'],
                            'ads_count': int(row['Liczba_Ogloszen']),
                            'profile_url': row['URL_Profilu']
                        }
                        self.checked_users.add(user_id)
                
                print(f"   ✅ Wczytano {len(self.found_businesses)} firm z poprzedniego runa")
            except Exception as e:
                print(f"   ⚠️ Błąd wczytywania CSV: {e}")
        
        # Wczytaj checked_users z cache
        cache_file = "overnight_checkpoint_cache.json"
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    cached_users = set(cache_data.get('checked_users', []))
                    self.checked_users.update(cached_users)
                
                print(f"   ✅ Wczytano {len(cached_users)} już sprawdzonych użytkowników")
                print(f"   ℹ️ Łącznie pomijam {len(self.checked_users)} użytkowników\n")
            except Exception as e:
                print(f"   ⚠️ Błąd wczytywania cache: {e}\n")
        else:
            print(f"   ℹ️ Brak cache - zaczynam od zera\n")
    
    def extract_user_id_from_url(self, url):
        """Wyciągnij user_id z URL"""
        match = re.search(r'/uzytkownik/([^/]+)', url)
        return match.group(1) if match else None
    
    def get_user_ads_count_fast(self, user_id):
        """Szybkie sprawdzenie liczby ogłoszeń użytkownika"""
        if user_id in self.checked_users:
            return None  # Już sprawdzony
        
        self.checked_users.add(user_id)
        
        profile_url = f"https://www.olx.pl/oferty/uzytkownik/{user_id}/"
        
        try:
            # Pojedynczy request na profil
            response = self.session.get(profile_url, timeout=8)
            
            if response.status_code != 200:
                return None
            
            # Szybki regex na liczbie ogłoszeń (bez parsowania całego HTML)
            ads_match = re.search(r'Znaleźliśmy\s+(\d+)\s+ogłosze', response.text, re.I)
            
            if not ads_match:
                return None
            
            ads_count = int(ads_match.group(1))
            
            # Wyciągnij nazwę (opcjonalnie, szybki regex)
            name_match = re.search(r'<h1[^>]*>([^<]+)</h1>', response.text)
            name = name_match.group(1).strip() if name_match else "Unknown"
            
            return {
                'user_id': user_id,
                'name': name,
                'ads_count': ads_count,
                'profile_url': profile_url,
            }
            
        except Exception as e:
            return None
    
    def scrape_listing_page(self, category, city, page=1):
        """Scrapuj jedną stronę listingu"""
        
        # Losuj miasto lub kategorię
        if random.random() > 0.5:
            url = f"https://www.olx.pl/{category}/{city}/"
        else:
            url = f"https://www.olx.pl/{category}/"
        
        if page > 1:
            url += f"?page={page}"
        
        try:
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                return []
            
            # Regex dla linków do ogłoszeń (szybsze niż BeautifulSoup)
            ad_urls = re.findall(r'href="(/d/oferta/[^"]+)"', response.text)
            
            return [f"https://www.olx.pl{url}" for url in ad_urls[:40]]  # Max 40 per stronę
            
        except Exception as e:
            return []
    
    def extract_user_from_ad(self, ad_url):
        """Wejdź w ogłoszenie i wyciągnij user_id"""
        try:
            response = self.session.get(ad_url, timeout=8)
            
            if response.status_code != 200:
                return None
            
            # Regex dla linku do profilu (szybsze)
            user_match = re.search(r'href="[^"]*?/uzytkownik/([^/"]+)', response.text)
            
            if user_match:
                return user_match.group(1)
            
            return None
            
        except Exception as e:
            return None
    
    def save_checkpoint(self):
        """Zapisz checkpoint"""
        filename = "overnight_checkpoint.csv"
        
        # Sortuj po liczbie ogłoszeń
        sorted_businesses = sorted(
            self.found_businesses.items(),
            key=lambda x: x[1]['ads_count'],
            reverse=True
        )
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Ranking', 'User_ID', 'Nazwa', 'Liczba_Ogloszen', 'URL_Profilu'])
            
            for rank, (user_id, data) in enumerate(sorted_businesses, 1):
                writer.writerow([
                    rank,
                    user_id,
                    data['name'],
                    data['ads_count'],
                    data['profile_url']
                ])
        
        # Cache checked_users żeby nie sprawdzać ponownie
        cache_file = "overnight_checkpoint_cache.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({
                'checked_users': list(self.checked_users),
                'last_update': datetime.now().isoformat(),
            }, f, indent=2)
        
        # JSON ze statystykami
        stats_file = filename.replace('.csv', '_stats.json')
        runtime = (datetime.now() - self.stats['start_time']).total_seconds()
        
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump({
                'ads_checked': self.stats['ads_checked'],
                'users_checked': self.stats['users_checked'],
                'businesses_found': self.stats['businesses_found'],
                'start_time': self.stats['start_time'].isoformat(),
                'runtime_seconds': runtime,
                'runtime_hours': runtime / 3600,
                'users_per_hour': self.stats['users_checked'] / (runtime / 3600) if runtime > 0 else 0,
                'total_businesses_found': len(self.found_businesses),
                'total_checked_users': len(self.checked_users),
            }, f, indent=2)
        
        return filename
    
    def print_ranking(self):
        """Wyświetl aktualny ranking"""
        sorted_businesses = sorted(
            self.found_businesses.items(),
            key=lambda x: x[1]['ads_count'],
            reverse=True
        )
        
        print("\n" + "="*80)
        print(f"🏆 AKTUALNY RANKING - TOP {min(20, len(sorted_businesses))}")
        print("="*80)
        
        for rank, (user_id, data) in enumerate(sorted_businesses[:20], 1):
            print(f"{rank:2d}. {data['name'][:30]:30s} | {data['ads_count']:5d} ogł. | {user_id}")
        
        print("="*80)
    
    def print_stats(self):
        """Wyświetl statystyki"""
        runtime = (datetime.now() - self.stats['start_time']).total_seconds()
        
        print(f"\n📊 STATYSTYKI:")
        print(f"   Czas działania: {runtime/3600:.1f}h ({runtime/60:.0f} min)")
        print(f"   Ogłoszeń sprawdzonych: {self.stats['ads_checked']}")
        print(f"   Użytkowników sprawdzonych: {self.stats['users_checked']}")
        print(f"   Unikalnych użytkowników: {len(self.checked_users)}")
        print(f"   Firm z >300 ogł: {len(self.found_businesses)}")
        
        if runtime > 0:
            print(f"   Tempo: {self.stats['users_checked']/(runtime/3600):.0f} users/h")
    
    def run_overnight(self, max_hours=8):
        """Główna pętla - działa przez noc"""
        print("="*80)
        print("🌙 OVERNIGHT SCRAPER - Start!")
        print("="*80)
        print(f"Cel: Znajdź użytkowników z >300 ogłoszeń")
        print(f"Max czas: {max_hours} godzin")
        print(f"Miasta: {', '.join(self.cities)}")
        print(f"Kategorie: {', '.join(self.categories)}")
        print(f"\nStart: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")
        
        start_time = time.time()
        max_runtime = max_hours * 3600
        
        checkpoint_counter = 0
        # Wczytaj poprzednie wyniki
        self.load_checkpoint()
        
        
        try:
            while True:
                # Sprawdź czas
                if time.time() - start_time > max_runtime:
                    print("\n⏰ Osiągnięto max czas działania")
                    break
                
                # Losuj kategorię i miasto
                category = random.choice(self.categories)
                city = random.choice(self.cities)
                page = random.randint(1, 5)  # Pierwsze 5 stron
                
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 📍 {category}/{city} (strona {page})")
                
                # Pobierz listę ogłoszeń
                ad_urls = self.scrape_listing_page(category, city, page)
                
                if not ad_urls:
                    print(f"   ⚠️ Brak ogłoszeń")
                    time.sleep(2)
                    continue
                
                print(f"   Znaleziono {len(ad_urls)} ogłoszeń")
                
                # Sprawdź każde ogłoszenie
                for i, ad_url in enumerate(ad_urls, 1):
                    self.stats['ads_checked'] += 1
                    
                    # Wyciągnij user_id z ogłoszenia
                    user_id = self.extract_user_from_ad(ad_url)
                    
                    if not user_id:
                        continue
                    
                    if user_id in self.checked_users:
                        continue  # Już sprawdzony
                    
                    # Sprawdź profil użytkownika
                    print(f"   [{i}/{len(ad_urls)}] 👤 {user_id}...", end=" ", flush=True)
                    
                    user_data = self.get_user_ads_count_fast(user_id)
                    self.stats['users_checked'] += 1
                    checkpoint_counter += 1
                    
                    if not user_data:
                        print("✗")
                    else:
                        ads_count = user_data['ads_count']
                        
                        # Jeśli >300 ogłoszeń → zapisz!
                        if ads_count >= 300:
                            self.found_businesses[user_id] = user_data
                            self.stats['businesses_found'] += 1
                            print(f"🎯 {ads_count} ogł. → ZAPISANO!")
                        
                        elif ads_count >= 100:
                            print(f"✓ {ads_count} ogł.")
                        else:
                            print(f"○ {ads_count} ogł.")
                    
                    # Co 10 użytkowników → checkpoint i ranking
                    if checkpoint_counter % 10 == 0:
                        filename = self.save_checkpoint()
                        print(f"\n💾 Checkpoint: {filename}")
                        self.print_ranking()
                        self.print_stats()
                    
                    # Mini delay
                    time.sleep(0.2)
                
                # Pauza między stronami
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n⚠️ Przerwano przez użytkownika (Ctrl+C)")
        
        # Finalne zapisanie
        print("\n" + "="*80)
        print("🏁 KONIEC SCRAPINGU")
        print("="*80)
        
        filename = self.save_checkpoint()
        print(f"\n💾 Zapisano wyniki: {filename}")
        
        self.print_ranking()
        self.print_stats()
        
        print(f"\n✅ Zakończono: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)


if __name__ == "__main__":
    scraper = OvernightScraper()
    
    print("\n🌙 OVERNIGHT SCRAPER")
    print("=" * 80)
    print("Ten skrypt będzie działał przez noc szukając firm z >300 ogłoszeń")
    print("\nParametry:")
    print("  - Cel: >300 ogłoszeń")
    print("  - Miasta: 10 największych w Polsce")
    print("  - Kategorie: 8 (bez motoryzacji)")
    print("  - Checkpoint co 10 znalezionych firm")
    print("  - Ranking aktualizowany na bieżąco")
    print("\nMożesz przerwać w każdej chwili (Ctrl+C) - progress zostanie zapisany")
    print("=" * 80)
    
    # Zapytaj o max czas
    try:
        hours = input("\nIle godzin ma działać? (domyślnie 8): ").strip()
        max_hours = float(hours) if hours else 8
    except:
        max_hours = 8
    
    print(f"\n▶️ START - będzie działać przez {max_hours}h")
    print("Naciśnij Ctrl+C aby przerwać w dowolnym momencie\n")
    
    time.sleep(2)
    
    # Uruchom
    scraper.run_overnight(max_hours=max_hours)
