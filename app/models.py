"""
Modele bazy danych dla aplikacji Blackjack.

Definiuje encje Player (gracz) oraz Game (gra).
"""

from sqlalchemy import Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from typing import Optional, List
import enum

from .database import Base


class GameStatus(enum.Enum):
    """
    Status gry w Blackjack.
    
    Attributes:
        IN_PROGRESS: Gra w toku.
        PLAYER_WON: Gracz wygrał.
        DEALER_WON: Krupier wygrał.
        TIE: Remis (push).
    """
    IN_PROGRESS = "in_progress"
    PLAYER_WON = "player_won"
    DEALER_WON = "dealer_won"
    TIE = "tie"


class Player(Base):
    """
    Model gracza w bazie danych.
    
    Przechowuje informacje o graczu, w tym saldo i statystyki gier.
    
    Attributes:
        id: Unikalny identyfikator gracza.
        username: Nazwa użytkownika (unikalna).
        balance: Saldo gracza (domyślnie 1000).
        games_played: Liczba rozegranych gier.
        games_won: Liczba wygranych gier.
        created_at: Data utworzenia konta.
    """
    __tablename__ = "players"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    balance: Mapped[int] = mapped_column(Integer, default=1000)
    games_played: Mapped[int] = mapped_column(Integer, default=0)
    games_won: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    games: Mapped[List["Game"]] = relationship("Game", back_populates="player")
    
    def __repr__(self) -> str:
        """Reprezentacja tekstowa gracza."""
        return f"<Player(id={self.id}, username='{self.username}', balance={self.balance})>"


class Game(Base):
    """
    Model gry w bazie danych.
    
    Przechowuje informacje o pojedynczej grze w Blackjack,
    w tym stan kart, zakład i wynik.
    
    Attributes:
        id: Unikalny identyfikator gry.
        status: Aktualny status gry.
        player_id: ID gracza.
        bet_amount: Kwota zakładu.
        player_hand: Karty gracza (JSON).
        dealer_hand: Karty krupiera (JSON).
        deck: Pozostałe karty w talii (JSON).
        player_score: Wynik punktowy gracza.
        dealer_score: Wynik punktowy krupiera.
        created_at: Data utworzenia gry.
        finished_at: Data zakończenia gry.
    """
    __tablename__ = "games"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default=GameStatus.IN_PROGRESS.value)
    
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False)
    bet_amount: Mapped[int] = mapped_column(Integer, default=10)
    
    player_hand: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    dealer_hand: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    deck: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    
    player_score: Mapped[int] = mapped_column(Integer, default=0)
    dealer_score: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    player: Mapped["Player"] = relationship("Player", back_populates="games")
    
    def __repr__(self) -> str:
        """Reprezentacja tekstowa gry."""
        return f"<Game(id={self.id}, status='{self.status}')>"
