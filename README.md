# Cel aplikacji

Za pomocą dowolnych bibliotek w Pythonie, C++ lub JavaScript stwórz aplikację graficzną, 
która wczytuje dostarczony plik zawierający chmurę punktów 3D (plik .txt z listą punktów 
o współrzędnych X, Y, Z). Wyświetl wizualizację wczytanej chmury punktów oraz oznacz kolorami 
punkty zgodnie z poniższymi wymaganiami:

- **czerwony** – punkty o współrzędnej Z < -1  
- **pomarańczowy** – punkty o współrzędnej Z ≥ -1 i Z < 0.5  
- **zielony** – pozostałe punkty  

W aplikacji powinna istnieć możliwość manipulacji chmurą punktów (obracanie, przybliżanie).  
Zaimplementuj funkcję przełączania oznaczeń kolorami – domyślnie punkty powinny mieć jednolity kolor.  

Pod uwagę będą brane również: **czytelność kodu** oraz **walory estetyczne interfejsu**.  
Rozwiązanie umieść w repozytorium GitHub wraz z plikiem `README` opisującym sposób uruchomienia.

---

# Wymagania

- Python **≥ 3.10**
- Zainstalowana przeglądarka internetowa

---

# Instalacja

Uruchom kolejne polecenia w konsoli:

### Windows

```bash
git clone https://github.com/pawpie-otw/3dpointcloud
cd 3dpointcloud
.\install.bat
```

### Linux

```bash
git clone https://github.com/pawpie-otw/3dpointcloud
cd 3dpointcloud
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
```

# Uruchomienie

Poniższe polecenie uruchamiamy w katalogu głównym aplikacji

### Windows:
```bash
.\.venv\Scripts\python.exe .\main.py
```

### Linux:
```bash
.\.venv\Scripts\python.exe .\main.py
```

# Obsługa aplikacji
- Wczytaj dane z pliku - kliknij przycisk "Wczytaj plik" i wskaż plik w odpowiednim formacie (poprawne wczytanie będzie potwierdzone odpowiednią informacją wyświetloną w aplikacji),
- Narysuj wykres:
    - "Stwórz wykres \[MPL\]" tworzy wykres przy użyciu matplotlib wewnątrz aplikcji,
    - "Stwórz wykres w przeglądarce \[Plotly\]" buduje i otwiera wykres w postaci strony www w przeglądarce.

## Przykładowy format pliku z danymi:
```
35.25813 -13.46673 26.08573
32.74439 -14.88116 24.22593
32.74474 -15.06398 24.22619
32.55049 -15.15619 24.08248
31.75766 -14.96419 23.49590
31.27534 -14.91138 23.13906
31.97902 -15.42527 23.65968
```

## Wykres Matplotlib

### Manipulacja
- LPM + ruch – obrót
- PPM + ruch góra/dół – przybliżenie/oddalenie
- Przycisk „Resetuj widok” – przywraca domyślną pozycję
- „Nałóż maskę kolorów” – włącza kolorowanie punktów wg reguły
- „Zamknij wykres” – usuwa wykres z okna

### Cechy
- wykres wbudowany w aplikację
- ograniczone możliwości manipulacji
- mniejsza wydajność przy dużych zbiorach

## Wykres Plotly

### Manipulacja
- LPM + ruch – obrót
- Scroll – przybliżenie/oddalenie
- PPM + ruch – przesunięcie kamery
- Menu po prawej – zmiana trybu kolorowania
- Menu w prawym górnym rogu – reset widoku i inne narzędzia

### Cechy
- otwiera się w przeglądarce
- nowoczesny i wydajny – obsługuje duże zbiory danych