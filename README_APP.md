# 📱 SMSAPI Studio — Panel Aplikacji Desktop / Web

Nowoczesna, pełnoprawna aplikacja graficzna dla platformy **SMSAPI** (`smsapi.pl`, `smsapi.com`, `smsapi.bg`, `smsapi.se`). Umożliwia wygodne zarządzanie wysyłkami SMS, MMS, wiadomościami głosowymi VMS, kodami uwierzytelniania dwuskładnikowego 2FA/MFA, bazą kontaktów oraz historią operacji.

---

## 🚀 Jak uruchomić aplikację?

### Sposób 1: Uruchomienie jednym kliknięciem (Windows / Linux / macOS)

* **Windows:** Kliknij dwukrotnie w plik **`start.bat`**.
* **Linux / macOS:** Uruchom w terminalu lub kliknij dwukrotnie w **`./run.sh`**.

Skrypt automatycznie zweryfikuje biblioteki, uruchomi lokalny serwer i **otworzy panel aplikacji w Twojej domyślnej przeglądarce internetowej** (`http://localhost:5000`).

---

### Sposób 2: Zbudowanie samodzielnego pliku `.exe` (PyInstaller)

Jeśli chcesz mieć pojedynczy program `.exe` do uruchamiania bez konieczności instalacji Pythona:

```bash
python build_exe.py
```

Gotowy plik wykonywalny znajdziesz w katalogu `dist/SMSAPI_Studio/`.

---

## 🌟 Funkcjonalności aplikacji

1. **📊 Pulpit i Stan Konta:**
   * Podgląd salda punktowego na żywo z szybkim odświeżaniem.
   * Statystyki wysyłek: wysłane dzisiaj, łączny koszt, wskaźnik skuteczności.
   * Moduł szybkiego SMS bezpośrednio z ekranu głównego.

2. **✉️ Centrum Wysyłki SMS:**
   * Wysyłka do jednego lub tysięcy numerów naraz.
   * Wybór zarejestrowanej nazwy nadawcy (*Sender ID*).
   * **Kalkulator znaków i części SMS w czasie rzeczywistym** (obsługa kodowania GSM-7 vs Unicode).
   * Detektor polskich znaków z opcją automatycznej normalizacji (`ą` -> `a`), pozwalającej zaoszczędzić punkty.
   * Opcje zaawansowane: **Flash SMS**, **Fast SMS** (priorytet), planowanie daty wysyłki, tryb testowy (symulacja bez pobierania punktów).
   * Gotowe i edytowalne szablony wiadomości.

3. **📁 Wysyłka Masowa z plików CSV / Excel:**
   * Wgrywanie plików metodą *Przeciągnij i upuść* (Drag & Drop).
   * Podgląd tabelaryczny danych w przeglądarce.
   * Dynamiczne mapowanie zmiennych (np. `[%imie%]`, `[%rabat%]`, `[%nr_zamowienia%]`).
   * Pasek postępu na żywo i szczegółowy raport po zakończeniu wysyłki.

4. **🔐 Moduł 2FA / MFA (Kody jednorazowe OTP):**
   * Automatyczne generowanie i wysyłka bezpiecznych kodów SMS weryfikujących tożsamość.
   * Formularz do weryfikacji poprawności wprowadzonego przez użytkownika kodu.

5. **📞 Wiadomości Głosowe VMS & MMS:**
   * **VMS:** Syntezator mowy (Text-To-Speech) z wyborem lektora (Ewa, Jacek, Jan, Maja), liczbą prób i interwałem połączeń.
   * **MMS:** Wysyłka wiadomości multimedialnych ze strukturą SMIL.

6. **👥 Książka Kontaktów i Grupy:**
   * Przeglądanie, wyszukiwanie i dodawanie kontaktów bezpośrednio do konta SMSAPI.
   * Zarządzanie grupami odbiorców.

7. **🔗 Skracacz Linków (idz.do) & Weryfikacja HLR:**
   * Generowanie krótkich linków `idz.do` do umieszczania w SMS-ach.
   * Analityka kliknięć (urządzenia, systemy, przeglądarki).
   * Sprawdzanie aktywności numeru w sieci komórkowej (zapytanie HLR).

8. **🚫 Czarna Lista (Blacklist / Opt-out):**
   * Blokowanie numerów, które zrezygnowały z subskrypcji.

9. **📜 Historia i Logi:**
   * Zapisywanie wszystkich operacji w lokalnej bazie danych SQLite.
   * Filtrowanie po typie, statusie i numerze telefonu.
   * Eksport pełnej historii do pliku CSV.

10. **⚙️ Ustawienia & Bezpieczeństwo:**
    * Bezpieczne lokalne przechowywanie tokenu OAuth SMSAPI.
    * Wybór platformy (`smsapi.pl`, `smsapi.com`, `smsapi.bg`, `smsapi.se`).
    * Testowanie połączenia jednym kliknięciem.

11. **🌐 Zdalny Dostęp z Internetu (Cloudflare Tunnel):**
    * Bezpieczne udostępnianie panelu poza sieć lokalną bez publicznego IP i bez przekierowania portów na routerze.
    * Gotowy skrypt `start_tunnel.bat` automatycznie pobiera i zestawia szyfrowany tunel HTTPS.

