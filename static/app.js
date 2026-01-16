const API_URL = window.location.origin;
const WS_URL = `ws://${window.location.host}/ws/status`;

let currentPlayer = null;
let currentGame = null;
let currentBet = 10;

document.addEventListener('DOMContentLoaded', () => {
    loadPlayers();
    connectWebSocket();
});

function connectWebSocket() {
    const ws = new WebSocket(WS_URL);
    
    ws.onopen = () => {
        document.querySelector('.status-dot').classList.add('online');
        document.getElementById('status-text').textContent = 'Online';
    };
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        document.getElementById('status-text').textContent = 
            `Online | Aktywne gry: ${data.active_games} | Zarejestrowanych: ${data.total_players}`;
    };
    
    ws.onclose = () => {
        document.querySelector('.status-dot').classList.remove('online');
        document.getElementById('status-text').textContent = 'Rozłączono';
        setTimeout(connectWebSocket, 3000);
    };
    
    ws.onerror = () => {
        document.getElementById('status-text').textContent = 'Błąd połączenia';
    };
}

function showTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    
    document.getElementById(tabName + '-tab').classList.add('active');
    event.target.classList.add('active');
}


async function loadPlayers() {
    try {
        const response = await fetch(`${API_URL}/players/`);
        const players = await response.json();
        
        const select = document.getElementById('player-select');
        select.innerHTML = '<option value="">-- Wybierz gracza --</option>';
        
        players.forEach(player => {
            const option = document.createElement('option');
            option.value = player.id;
            option.textContent = `${player.username} ($${player.balance})`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Błąd ładowania graczy:', error);
    }
}

async function createPlayer() {
    const username = document.getElementById('new-username').value.trim();
    
    if (!username || username.length < 3) {
        alert('Nazwa użytkownika musi mieć minimum 3 znaki!');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/players/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, initial_balance: 1000 })
        });
        
        if (response.ok) {
            currentPlayer = await response.json();
            showGameScreen();
        } else {
            const error = await response.json();
            alert(error.detail || 'Błąd tworzenia gracza');
        }
    } catch (error) {
        alert('Błąd połączenia z serwerem');
    }
}

async function selectPlayer() {
    const playerId = document.getElementById('player-select').value;
    
    if (!playerId) {
        alert('Wybierz gracza!');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/players/${playerId}`);
        if (response.ok) {
            currentPlayer = await response.json();
            showGameScreen();
        }
    } catch (error) {
        alert('Błąd ładowania gracza');
    }
}

async function logout() {
    if (currentGame && currentGame.status === 'in_progress') {
        try {
            await fetch(`${API_URL}/games/${currentGame.id}`, {
                method: 'DELETE'
            });
        } catch (error) {
            console.error('Błąd usuwania gry:', error);
        }
    }
    
    currentPlayer = null;
    currentGame = null;
    document.getElementById('login-screen').classList.remove('hidden');
    document.getElementById('game-screen').classList.add('hidden');
    loadPlayers();
}

function showGameScreen() {
    document.getElementById('login-screen').classList.add('hidden');
    document.getElementById('game-screen').classList.remove('hidden');
    updatePlayerInfo();
    showBetPanel();
}

function updatePlayerInfo() {
    document.getElementById('player-name').textContent = currentPlayer.username;
    document.getElementById('player-balance').textContent = `$${currentPlayer.balance}`;
    document.getElementById('player-stats').textContent = 
        `${currentPlayer.games_won} wygranych / ${currentPlayer.games_played} gier`;
}

function showBetPanel() {
    document.getElementById('bet-panel').classList.remove('hidden');
    document.getElementById('action-panel').classList.add('hidden');
    document.getElementById('newgame-panel').classList.add('hidden');
    document.getElementById('game-result').classList.add('hidden');
    
    document.getElementById('dealer-cards').innerHTML = '';
    document.getElementById('player-cards').innerHTML = '';
    document.getElementById('dealer-score').textContent = '';
    document.getElementById('player-score').textContent = '';
    
    refreshPlayerData();
}

async function refreshPlayerData() {
    try {
        const response = await fetch(`${API_URL}/players/${currentPlayer.id}`);
        if (response.ok) {
            currentPlayer = await response.json();
            updatePlayerInfo();
        }
    } catch (error) {
        console.error('Błąd odświeżania danych:', error);
    }
}


function setBet(amount) {
    currentBet = amount;
    document.getElementById('custom-bet').value = amount;
    
    document.querySelectorAll('.btn-bet').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
}


async function startGame() {
    const customBet = document.getElementById('custom-bet').value;
    if (customBet) {
        currentBet = parseInt(customBet);
    }
    
    if (currentBet < 1) {
        alert('Minimalny zakład to $1!');
        return;
    }
    
    if (currentBet > currentPlayer.balance) {
        alert('Nie masz wystarczających środków!');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/games/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                player1_id: currentPlayer.id,
                bet_amount: currentBet
            })
        });
        
        if (response.ok) {
            currentGame = await response.json();
            displayGameState(true);
            
            if (currentGame.status === 'in_progress') {
                document.getElementById('bet-panel').classList.add('hidden');
                document.getElementById('action-panel').classList.remove('hidden');
            } else {
                endGame();
            }
        } else {
            const error = await response.json();
            alert(error.detail || 'Błąd rozpoczęcia gry');
        }
    } catch (error) {
        alert('Błąd połączenia z serwerem');
    }
}

async function hit() {
    try {
        const response = await fetch(`${API_URL}/games/${currentGame.id}/action`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                action: 'hit',
                player_id: currentPlayer.id
            })
        });
        
        if (response.ok) {
            currentGame = await response.json();
            displayGameState(true);
            
            if (currentGame.status !== 'in_progress') {
                endGame();
            }
        }
    } catch (error) {
        alert('Błąd wykonania akcji');
    }
}

async function stand() {
    try {
        const response = await fetch(`${API_URL}/games/${currentGame.id}/action`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                action: 'stand',
                player_id: currentPlayer.id
            })
        });
        
        if (response.ok) {
            currentGame = await response.json();
            displayGameState(false);
            endGame();
        }
    } catch (error) {
        alert('Błąd wykonania akcji');
    }
}


function displayGameState(hideDealer) {
    const playerCardsDiv = document.getElementById('player-cards');
    playerCardsDiv.innerHTML = '';
    currentGame.player_hand.forEach(card => {
        playerCardsDiv.appendChild(createCardElement(card));
    });
    document.getElementById('player-score').textContent = `(${currentGame.player_score})`;
    
    const dealerCardsDiv = document.getElementById('dealer-cards');
    dealerCardsDiv.innerHTML = '';
    currentGame.dealer_hand.forEach((card, index) => {
        if (hideDealer && index === 0 && currentGame.status === 'in_progress') {
            dealerCardsDiv.appendChild(createHiddenCard());
        } else {
            dealerCardsDiv.appendChild(createCardElement(card));
        }
    });
    
    if (hideDealer && currentGame.status === 'in_progress') {
        const visibleScore = currentGame.dealer_hand[1]?.value || '?';
        document.getElementById('dealer-score').textContent = `(${visibleScore}+?)`;
    } else {
        document.getElementById('dealer-score').textContent = `(${currentGame.dealer_score})`;
    }
}

function createCardElement(card) {
    const div = document.createElement('div');
    div.className = `playing-card ${card.suit}`;
    
    const suitSymbols = {
        'hearts': '♥',
        'diamonds': '♦',
        'clubs': '♣',
        'spades': '♠'
    };
    
    const symbol = suitSymbols[card.suit];
    
    div.innerHTML = `
        <div class="card-top">${card.rank}${symbol}</div>
        <div class="card-bottom">${card.rank}${symbol}</div>
    `;
    
    return div;
}

function createHiddenCard() {
    const div = document.createElement('div');
    div.className = 'playing-card hidden-card';
    div.textContent = '?';
    return div;
}

function endGame() {
    document.getElementById('action-panel').classList.add('hidden');
    document.getElementById('newgame-panel').classList.remove('hidden');
    
    const resultDiv = document.getElementById('game-result');
    resultDiv.classList.remove('hidden', 'win', 'lose', 'tie', 'blackjack');
    
    displayGameState(false);
    
    let message = '';
    let resultClass = '';
    
    if (currentGame.status === 'player_won') {
        if (currentGame.player_score === 21 && currentGame.player_hand.length === 2) {
            message = 'BLACKJACK!';
            resultClass = 'blackjack';
        } else {
            message = 'Wygrałeś!';
            resultClass = 'win';
        }
        message += ` +$${currentBet}`;
    } else if (currentGame.status === 'dealer_won') {
        message = 'Przegrałeś';
        resultClass = 'lose';
        message += ` -$${currentBet}`;
    } else {
        message = 'Remis!';
        resultClass = 'tie';
    }
    
    resultDiv.textContent = message;
    resultDiv.classList.add(resultClass);
    
    refreshPlayerData();
}
