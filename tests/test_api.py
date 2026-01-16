"""
Testy API dla aplikacji Blackjack.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine


@pytest.fixture(autouse=True)
def setup_database():
    """Przygotowuje bazę danych przed każdym testem."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


class TestPlayerAPI:
    """Testy API dla graczy."""
    
    def test_create_player(self):
        """Testuje tworzenie gracza."""
        response = client.post("/players/", json={
            "username": "testplayer",
            "initial_balance": 500
        })
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testplayer"
        assert data["balance"] == 500
    
    def test_create_player_duplicate(self):
        """Testuje błąd przy duplikacie nazwy."""
        client.post("/players/", json={"username": "duplicate"})
        response = client.post("/players/", json={"username": "duplicate"})
        assert response.status_code == 400
    
    def test_get_players(self):
        """Testuje pobieranie listy graczy."""
        client.post("/players/", json={"username": "player1"})
        client.post("/players/", json={"username": "player2"})
        
        response = client.get("/players/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
    
    def test_get_player(self):
        """Testuje pobieranie gracza po ID."""
        create_response = client.post("/players/", json={"username": "gettest"})
        player_id = create_response.json()["id"]
        
        response = client.get(f"/players/{player_id}")
        assert response.status_code == 200
        assert response.json()["username"] == "gettest"
    
    def test_get_player_not_found(self):
        """Testuje błąd gdy gracz nie istnieje."""
        response = client.get("/players/99999")
        assert response.status_code == 404
    
    def test_update_player(self):
        """Testuje aktualizację gracza."""
        create_response = client.post("/players/", json={"username": "updatetest"})
        player_id = create_response.json()["id"]
        
        response = client.put(f"/players/{player_id}", json={
            "balance": 2000
        })
        assert response.status_code == 200
        assert response.json()["balance"] == 2000
    
    def test_delete_player(self):
        """Testuje usuwanie gracza."""
        create_response = client.post("/players/", json={"username": "deletetest"})
        player_id = create_response.json()["id"]
        
        response = client.delete(f"/players/{player_id}")
        assert response.status_code == 200
        
        get_response = client.get(f"/players/{player_id}")
        assert get_response.status_code == 404


class TestGameAPI:
    """Testy API dla gier."""
    
    def test_create_game(self):
        """Testuje tworzenie gry."""
        player_response = client.post("/players/", json={"username": "gameplayer"})
        player_id = player_response.json()["id"]
        
        response = client.post("/games/", json={
            "player1_id": player_id,
            "bet_amount": 50
        })
        assert response.status_code == 200
        data = response.json()
        assert data["player_id"] == player_id
        assert data["bet_amount"] == 50
        assert len(data["player_hand"]) == 2
        assert len(data["dealer_hand"]) == 2
    
    def test_create_game_player_not_found(self):
        """Testuje błąd gdy gracz nie istnieje."""
        response = client.post("/games/", json={
            "player1_id": 99999,
            "bet_amount": 10
        })
        assert response.status_code == 400
    
    def test_get_game(self):
        """Testuje pobieranie gry."""
        player_response = client.post("/players/", json={"username": "getgame"})
        player_id = player_response.json()["id"]
        
        game_response = client.post("/games/", json={
            "player1_id": player_id,
            "bet_amount": 10
        })
        game_id = game_response.json()["id"]
        
        response = client.get(f"/games/{game_id}")
        assert response.status_code == 200
    
    def test_game_action_hit(self):
        """Testuje akcję hit."""
        player_response = client.post("/players/", json={"username": "hitplayer"})
        player_id = player_response.json()["id"]
        
        game_response = client.post("/games/", json={
            "player1_id": player_id,
            "bet_amount": 10
        })
        game_id = game_response.json()["id"]
        
        if game_response.json()["status"] == "in_progress":
            response = client.post(f"/games/{game_id}/action", json={
                "action": "hit",
                "player_id": player_id
            })
            assert response.status_code == 200
            assert len(response.json()["player_hand"]) >= 3
    
    def test_game_action_stand(self):
        """Testuje akcję stand."""
        player_response = client.post("/players/", json={"username": "standplayer"})
        player_id = player_response.json()["id"]
        
        game_response = client.post("/games/", json={
            "player1_id": player_id,
            "bet_amount": 10
        })
        game_id = game_response.json()["id"]
        
        if game_response.json()["status"] == "in_progress":
            response = client.post(f"/games/{game_id}/action", json={
                "action": "stand",
                "player_id": player_id
            })
            assert response.status_code == 200
            assert response.json()["status"] != "in_progress"
    
    def test_delete_game(self):
        """Testuje usuwanie gry."""
        player_response = client.post("/players/", json={"username": "deletegame"})
        player_id = player_response.json()["id"]
        
        game_response = client.post("/games/", json={
            "player1_id": player_id,
            "bet_amount": 10
        })
        game_id = game_response.json()["id"]
        
        response = client.delete(f"/games/{game_id}")
        assert response.status_code == 200


class TestHealthEndpoints:
    """Testy dla endpointów informacyjnych."""
    
    def test_root(self):
        """Testuje endpoint główny - zwraca stronę HTML."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_api_info(self):
        """Testuje endpoint informacji o API."""
        response = client.get("/api")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Blackjack API"
    
    def test_health(self):
        """Testuje endpoint health check."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
