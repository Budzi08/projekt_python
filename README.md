Gra w Blackjack z interfejsem webowym, zaimplementowana w Pythonie z FastAPI.

Funkcjonalności
Aplikacja webowa - gra w przeglądarce
REST API - operacje CRUD dla graczy i gier
WebSocket - status serwera w czasie rzeczywistym (JSON)
Baza Danych - SQLite z SQLAlchemy ORM
Testy jednostkowe - pytest

Wymagania

- Python 3.9+

Instalacja

cd blackjack
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

Uruchomienie

uvicorn app.main:app --reload

Otwórz w przeglądarce: http://localhost:8000

Dokumentacja API: http://localhost:8000/docs

Zasady Blackjack

- Cel: uzyskać sumę kart jak najbliższą 21
- Karty 2-10: wartość nominalna
- J, Q, K: 10 punktów
- As: 11 lub 1 punkt
- Blackjack: 21 z dwóch kart (As + 10/figura)
- Bust: powyżej 21 = przegrana
