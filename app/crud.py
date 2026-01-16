"""
Operacje CRUD dla bazy danych.

Zawiera funkcje do tworzenia, odczytu, aktualizacji i usuwania
rekordów graczy i gier.
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from . import models, schemas
from .game_logic import BlackjackGame


def create_player(db: Session, player: schemas.PlayerCreate) -> models.Player:
    """
    Tworzy nowego gracza w bazie danych.
    
    Args:
        db: Sesja bazy danych.
        player: Dane nowego gracza.
        
    Returns:
        Player: Utworzony gracz.
        
    Raises:
        ValueError: Jeśli username już istnieje.
    """
    existing = db.query(models.Player).filter(
        models.Player.username == player.username
    ).first()
    
    if existing:
        raise ValueError(f"Gracz o nazwie '{player.username}' już istnieje")
    
    db_player = models.Player(
        username=player.username,
        balance=player.initial_balance
    )
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player


def get_player(db: Session, player_id: int) -> Optional[models.Player]:
    """
    Pobiera gracza po ID.
    
    Args:
        db: Sesja bazy danych.
        player_id: ID gracza.
        
    Returns:
        Player: Gracz lub None jeśli nie znaleziono.
    """
    return db.query(models.Player).filter(models.Player.id == player_id).first()


def get_players(db: Session, skip: int = 0, limit: int = 100) -> List[models.Player]:
    """
    Pobiera listę graczy
    
    Args:
        db: Sesja bazy danych.
        skip: Liczba rekordów do pominięcia.
        limit: Maksymalna liczba rekordów.
        
    Returns:
        List[Player]: Lista graczy.
    """
    return db.query(models.Player).offset(skip).limit(limit).all()


def update_player(db: Session, player_id: int, 
                  player_update: schemas.PlayerUpdate) -> Optional[models.Player]:
    """
    Aktualizuje dane gracza.
    
    Args:
        db: Sesja bazy danych.
        player_id: ID gracza do aktualizacji.
        player_update: Nowe dane gracza.
        
    Returns:
        Player: Zaktualizowany gracz lub None jeśli nie znaleziono.
    """
    db_player = get_player(db, player_id)
    if not db_player:
        return None
    
    update_data = player_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_player, field, value)
    
    db.commit()
    db.refresh(db_player)
    return db_player


def delete_player(db: Session, player_id: int) -> bool:
    """
    Usuwa gracza z bazy danych.
    
    Args:
        db: Sesja bazy danych.
        player_id: ID gracza do usunięcia.
        
    Returns:
        bool: True jeśli usunięto, False jeśli nie znaleziono.
    """
    db_player = get_player(db, player_id)
    if not db_player:
        return False
    
    db.delete(db_player)
    db.commit()
    return True


def update_player_stats(db: Session, player_id: int, won: bool) -> Optional[models.Player]:
    """
    Aktualizuje statystyki gracza po zakończonej grze.
    
    Args:
        db: Sesja bazy danych.
        player_id: ID gracza.
        won: Czy gracz wygrał.
        
    Returns:
        Player: Zaktualizowany gracz.
    """
    db_player = get_player(db, player_id)
    if not db_player:
        return None
    
    db_player.games_played += 1
    if won:
        db_player.games_won += 1
    
    db.commit()
    db.refresh(db_player)
    return db_player


def update_player_balance(db: Session, player_id: int, 
                          amount: int) -> Optional[models.Player]:
    """
    Aktualizuje saldo gracza.
    
    Args:
        db: Sesja bazy danych.
        player_id: ID gracza.
        amount: Kwota do dodania (ujemna = odjęcie).
        
    Returns:
        Player: Zaktualizowany gracz.
    """
    db_player = get_player(db, player_id)
    if not db_player:
        return None
    
    db_player.balance += amount
    db.commit()
    db.refresh(db_player)
    return db_player

def create_game(db: Session, game_data: schemas.GameCreate) -> models.Game:
    """
    Tworzy nową grę w bazie danych.
    
    Args:
        db: Sesja bazy danych.
        game_data: Dane nowej gry.
        
    Returns:
        Game: Utworzona gra z początkowym rozdaniem kart.
        
    Raises:
        ValueError: Jeśli gracz nie istnieje lub ma za mało środków.
    """
    player = get_player(db, game_data.player1_id)
    if not player:
        raise ValueError(f"Gracz o ID {game_data.player1_id} nie istnieje")
    
    if player.balance < game_data.bet_amount:
        raise ValueError(f"Gracz {player.username} ma niewystarczające środki")
    

    game = BlackjackGame()
    game.deal_initial_cards()
    state = game.get_state()
    
    db_game = models.Game(
        status=models.GameStatus.IN_PROGRESS.value,
        player_id=game_data.player1_id,
        bet_amount=game_data.bet_amount,
        player_hand=state["player_hand"],
        dealer_hand=state["dealer_hand"],
        deck=game.deck.to_list(),
        player_score=state["player_score"],
        dealer_score=state["dealer_score"]
    )
    

    if state["game_over"]:
        winner = game.determine_winner()
        db_game.status = winner
        db_game.finished_at = datetime.utcnow()
        
        if winner == "player_won":
            update_player_stats(db, game_data.player1_id, won=True)
            update_player_balance(db, game_data.player1_id, game_data.bet_amount)
        elif winner == "dealer_won":
            update_player_stats(db, game_data.player1_id, won=False)
            update_player_balance(db, game_data.player1_id, -game_data.bet_amount)
        else:
            update_player_stats(db, game_data.player1_id, won=False)
    
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    return db_game


def get_game(db: Session, game_id: int) -> Optional[models.Game]:
    """
    Pobiera grę po ID.
    
    Args:
        db: Sesja bazy danych.
        game_id: ID gry.
        
    Returns:
        Game: Gra lub None jeśli nie znaleziono.
    """
    return db.query(models.Game).filter(models.Game.id == game_id).first()


def get_games(db: Session, skip: int = 0, limit: int = 100) -> List[models.Game]:
    """
    Pobiera listę gier.
    
    Args:
        db: Sesja bazy danych.
        skip: Liczba rekordów do pominięcia.
        limit: Maksymalna liczba rekordów.
        
    Returns:
        List[Game]: Lista gier.
    """
    return db.query(models.Game).offset(skip).limit(limit).all()


def get_active_games(db: Session) -> List[models.Game]:
    """
    Pobiera wszystkie aktywne gry.
    
    Args:
        db: Sesja bazy danych.
        
    Returns:
        List[Game]: Lista aktywnych gier.
    """
    return db.query(models.Game).filter(
        models.Game.status == models.GameStatus.IN_PROGRESS.value
    ).all()


def game_action(db: Session, game_id: int, action: schemas.GameAction) -> models.Game:
    """
    Wykonuje akcję w grze (hit lub stand).
    
    Args:
        db: Sesja bazy danych.
        game_id: ID gry.
        action: Akcja do wykonania.
        
    Returns:
        Game: Zaktualizowana gra.
        
    Raises:
        ValueError: Jeśli gra nie istnieje lub jest zakończona.
    """
    db_game = get_game(db, game_id)
    if not db_game:
        raise ValueError(f"Gra o ID {game_id} nie istnieje")
    
    if db_game.status != models.GameStatus.IN_PROGRESS.value:
        raise ValueError("Gra jest już zakończona")
    
    if action.player_id != db_game.player_id:
        raise ValueError(f"Gracz {action.player_id} nie uczestniczy w tej grze")
    
    game = BlackjackGame.from_state(
        player_hand_data=db_game.player_hand,
        dealer_hand_data=db_game.dealer_hand,
        deck_data=db_game.deck
    )
    
    if action.action == "hit":
        game.player_hit()
    elif action.action == "stand":
        game.player_stand()
    else:
        raise ValueError(f"Nieznana akcja: {action.action}")
    
    state = game.get_state()
    db_game.player_hand = state["player_hand"]
    db_game.dealer_hand = state["dealer_hand"]
    db_game.deck = game.deck.to_list()
    db_game.player_score = state["player_score"]
    db_game.dealer_score = state["dealer_score"]
    
    if state["game_over"]:
        winner = game.determine_winner()
        db_game.status = winner
        db_game.finished_at = datetime.utcnow()
        
        if winner == "player_won":
            update_player_stats(db, db_game.player_id, won=True)
            update_player_balance(db, db_game.player_id, db_game.bet_amount)
        elif winner == "dealer_won":
            update_player_stats(db, db_game.player_id, won=False)
            update_player_balance(db, db_game.player_id, -db_game.bet_amount)
        else:
            update_player_stats(db, db_game.player_id, won=False)
    
    db.commit()
    db.refresh(db_game)
    return db_game


def delete_game(db: Session, game_id: int) -> bool:
    """
    Usuwa grę z bazy danych.
    
    Args:
        db: Sesja bazy danych.
        game_id: ID gry do usunięcia.
        
    Returns:
        bool: True jeśli usunięto, False jeśli nie znaleziono.
    """
    db_game = get_game(db, game_id)
    if not db_game:
        return False
    
    db.delete(db_game)
    db.commit()
    return True
