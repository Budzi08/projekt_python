"""
Główna aplikacja FastAPI dla gry Blackjack.

Definiuje endpointy REST API oraz WebSocket do komunikacji w czasie rzeczywistym.
"""

from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import asyncio
import os

from .database import engine, get_db, Base
from . import models, schemas, crud

SERVER_START_TIME = datetime.utcnow()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Blackjack API",
    description="REST API dla gry w Blackjack (tryb single player)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/players/", response_model=schemas.PlayerResponse, tags=["Players"])
def create_player(player: schemas.PlayerCreate, db: Session = Depends(get_db)):
    """
    Tworzy nowego gracza.
    
    Args:
        player: Dane nowego gracza.
        db: Sesja bazy danych.
        
    Returns:
        PlayerResponse: Utworzony gracz.
        
    Raises:
        HTTPException: Jeśli nazwa użytkownika jest zajęta.
    """
    try:
        return crud.create_player(db, player)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/players/", response_model=List[schemas.PlayerResponse], tags=["Players"])
def read_players(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Pobiera listę wszystkich graczy.
    
    Args:
        skip: Liczba rekordów do pominięcia.
        limit: Maksymalna liczba rekordów.
        db: Sesja bazy danych.
        
    Returns:
        List[PlayerResponse]: Lista graczy.
    """
    return crud.get_players(db, skip=skip, limit=limit)


@app.get("/players/{player_id}", response_model=schemas.PlayerResponse, tags=["Players"])
def read_player(player_id: int, db: Session = Depends(get_db)):
    """
    Pobiera gracza po ID.
    
    Args:
        player_id: ID gracza.
        db: Sesja bazy danych.
        
    Returns:
        PlayerResponse: Dane gracza.
        
    Raises:
        HTTPException: Jeśli gracz nie istnieje.
    """
    db_player = crud.get_player(db, player_id)
    if db_player is None:
        raise HTTPException(status_code=404, detail="Gracz nie znaleziony")
    return db_player


@app.put("/players/{player_id}", response_model=schemas.PlayerResponse, tags=["Players"])
def update_player(player_id: int, player: schemas.PlayerUpdate, 
                  db: Session = Depends(get_db)):
    """
    Aktualizuje dane gracza.
    
    Args:
        player_id: ID gracza do aktualizacji.
        player: Nowe dane gracza.
        db: Sesja bazy danych.
        
    Returns:
        PlayerResponse: Zaktualizowany gracz.
        
    Raises:
        HTTPException: Jeśli gracz nie istnieje.
    """
    db_player = crud.update_player(db, player_id, player)
    if db_player is None:
        raise HTTPException(status_code=404, detail="Gracz nie znaleziony")
    return db_player


@app.delete("/players/{player_id}", tags=["Players"])
def delete_player(player_id: int, db: Session = Depends(get_db)):
    """
    Usuwa gracza.
    
    Args:
        player_id: ID gracza do usunięcia.
        db: Sesja bazy danych.
        
    Returns:
        dict: Potwierdzenie usunięcia.
        
    Raises:
        HTTPException: Jeśli gracz nie istnieje.
    """
    if not crud.delete_player(db, player_id):
        raise HTTPException(status_code=404, detail="Gracz nie znaleziony")
    return {"message": "Gracz usunięty pomyślnie"}


@app.post("/games/", response_model=schemas.GameResponse, tags=["Games"])
def create_game(game: schemas.GameCreate, db: Session = Depends(get_db)):
    """
    Tworzy nową grę w Blackjack.
    
    Args:
        game: Dane nowej gry (ID gracza i zakład).
        db: Sesja bazy danych.
        
    Returns:
        GameResponse: Utworzona gra z początkowym rozdaniem.
        
    Raises:
        HTTPException: Jeśli gracz nie istnieje lub ma za mało środków.
    """
    try:
        return crud.create_game(db, game)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/games/", response_model=List[schemas.GameResponse], tags=["Games"])
def read_games(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Pobiera listę wszystkich gier.
    
    Args:
        skip: Liczba rekordów do pominięcia.
        limit: Maksymalna liczba rekordów.
        db: Sesja bazy danych.
        
    Returns:
        List[GameResponse]: Lista gier.
    """
    return crud.get_games(db, skip=skip, limit=limit)


@app.get("/games/{game_id}", response_model=schemas.GameResponse, tags=["Games"])
def read_game(game_id: int, db: Session = Depends(get_db)):
    """
    Pobiera grę po ID.
    
    Args:
        game_id: ID gry.
        db: Sesja bazy danych.
        
    Returns:
        GameResponse: Dane gry.
        
    Raises:
        HTTPException: Jeśli gra nie istnieje.
    """
    db_game = crud.get_game(db, game_id)
    if db_game is None:
        raise HTTPException(status_code=404, detail="Gra nie znaleziona")
    return db_game


@app.post("/games/{game_id}/action", response_model=schemas.GameResponse, tags=["Games"])
def game_action(game_id: int, action: schemas.GameAction, 
                db: Session = Depends(get_db)):
    """
    Wykonuje akcję w grze (hit lub stand).
    
    Args:
        game_id: ID gry.
        action: Akcja do wykonania.
        db: Sesja bazy danych.
        
    Returns:
        GameResponse: Zaktualizowany stan gry.
        
    Raises:
        HTTPException: Jeśli gra nie istnieje lub akcja jest nieprawidłowa.
    """
    try:
        return crud.game_action(db, game_id, action)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/games/{game_id}", tags=["Games"])
def delete_game(game_id: int, db: Session = Depends(get_db)):
    """
    Usuwa grę.
    
    Args:
        game_id: ID gry do usunięcia.
        db: Sesja bazy danych.
        
    Returns:
        dict: Potwierdzenie usunięcia.
        
    Raises:
        HTTPException: Jeśli gra nie istnieje.
    """
    if not crud.delete_game(db, game_id):
        raise HTTPException(status_code=404, detail="Gra nie znaleziona")
    return {"message": "Gra usunięta pomyślnie"}


def get_server_uptime() -> str:
    """
    Oblicza czas działania serwera.
    
    Returns:
        str: Czas działania w formacie "Xh Ym Zs".
    """
    delta = datetime.utcnow() - SERVER_START_TIME
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"


@app.websocket("/ws/status")
async def websocket_status(websocket: WebSocket):
    """
    WebSocket endpoint do monitorowania statusu serwera.
    
    Wysyła aktualizacje co sekundę z informacjami o:
    - status: Status serwera (online)
    - datetime: Aktualna data i godzina
    - active_games: Liczba aktywnych gier
    - total_players: Łączna liczba graczy
    - server_uptime: Czas działania serwera
    
    Args:
        websocket: Połączenie WebSocket.
    """
    await websocket.accept()
    
    try:
        while True:
            db = next(get_db())
            try:
                active_games = len(crud.get_active_games(db))
                total_players = len(crud.get_players(db))
            finally:
                db.close()
            
            status_data = schemas.ServerStatus(
                status="online",
                datetime=datetime.utcnow().isoformat(),
                active_games=active_games,
                total_players=total_players,
                server_uptime=get_server_uptime()
            )
            
            await websocket.send_json(status_data.model_dump())
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        pass


@app.get("/", tags=["Info"])
def root():
    """
    Serwuje główną stronę aplikacji webowej.
    
    Returns:
        FileResponse: Plik index.html.
    """
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/api", tags=["Info"])
def api_info():
    """
    Endpoint z informacjami o API.
    
    Returns:
        dict: Informacje o API.
    """
    return {
        "name": "Blackjack API",
        "version": "1.0.0",
        "description": "REST API dla gry w Blackjack",
        "documentation": "/docs",
        "websocket": "/ws/status"
    }


@app.get("/health", tags=["Info"])
def health_check():
    """
    Endpoint sprawdzający stan serwera.
    
    Returns:
        dict: Status serwera.
    """
    return {
        "status": "healthy",
        "uptime": get_server_uptime()
    }
