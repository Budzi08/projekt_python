"""
Schematy Pydantic dla walidacji danych.

Definiuje schematy request/response dla API.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class PlayerBase(BaseModel):
    """
    Bazowy schemat gracza.
    
    Attributes:
        username: Nazwa użytkownika (3-50 znaków).
    """
    username: str = Field(..., min_length=3, max_length=50, description="Nazwa użytkownika")


class PlayerCreate(PlayerBase):
    """
    Schemat tworzenia nowego gracza.
    
    Attributes:
        username: Nazwa użytkownika.
        initial_balance: Początkowe saldo (opcjonalne, domyślnie 1000).
    """
    initial_balance: Optional[int] = Field(default=1000, ge=0, description="Początkowe saldo")


class PlayerUpdate(BaseModel):
    """
    Schemat aktualizacji gracza.
    
    Attributes:
        username: Nowa nazwa użytkownika (opcjonalna).
        balance: Nowe saldo (opcjonalne).
    """
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    balance: Optional[int] = Field(None, ge=0)


class PlayerResponse(PlayerBase):
    """
    Schemat odpowiedzi z danymi gracza.
    
    Attributes:
        id: ID gracza.
        username: Nazwa użytkownika.
        balance: Aktualne saldo.
        games_played: Liczba rozegranych gier.
        games_won: Liczba wygranych gier.
        created_at: Data utworzenia konta.
    """
    id: int
    balance: int
    games_played: int
    games_won: int
    created_at: datetime
    
    model_config = {"from_attributes": True}


class GameCreate(BaseModel):
    """
    Schemat tworzenia nowej gry.
    
    Attributes:
        player1_id: ID gracza.
        bet_amount: Kwota zakładu.
    """
    player1_id: int = Field(..., description="ID gracza")
    bet_amount: int = Field(default=10, ge=1, description="Kwota zakładu")


class GameResponse(BaseModel):
    """
    Schemat odpowiedzi z danymi gry.
    
    Attributes:
        id: ID gry.
        status: Status gry.
        player_id: ID gracza.
        bet_amount: Kwota zakładu.
        player_hand: Karty gracza.
        dealer_hand: Karty krupiera.
        player_score: Wynik gracza.
        dealer_score: Wynik krupiera.
        created_at: Data utworzenia.
        finished_at: Data zakończenia.
    """
    id: int
    status: str
    player_id: int
    bet_amount: int
    player_hand: List[dict]
    dealer_hand: List[dict]
    player_score: int
    dealer_score: int
    created_at: datetime
    finished_at: Optional[datetime]
    
    model_config = {"from_attributes": True}


class GameAction(BaseModel):
    """
    Schemat akcji w grze.
    
    Attributes:
        action: Rodzaj akcji ('hit' lub 'stand').
        player_id: ID gracza wykonującego akcję.
    """
    action: str = Field(..., description="Akcja: 'hit' lub 'stand'")
    player_id: int = Field(..., description="ID gracza wykonującego akcję")


class ServerStatus(BaseModel):
    """
    Schemat statusu serwera dla WebSocket.
    
    Attributes:
        status: Status serwera.
        datetime: Aktualna data i godzina.
        active_games: Liczba aktywnych gier.
        total_players: Łączna liczba graczy.
        server_uptime: Czas działania serwera.
    """
    status: str = "online"
    datetime: str
    active_games: int
    total_players: int
    server_uptime: str
