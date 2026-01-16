"""
Logika gry Blackjack.

Zawiera implementację talii kart, obliczanie punktów oraz mechanikę gry.
"""

import random
from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class Card:
    """
    Reprezentacja pojedynczej karty do gry.
    
    Attributes:
        suit: Kolor karty.
        rank: Ranga karty (2-10, J, Q, K, A).
    """
    suit: str
    rank: str
    
    RANK_VALUES: Dict[str, int] = field(default_factory=lambda: {
        "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
        "J": 10, "Q": 10, "K": 10, "A": 11
    }, repr=False)
    
    def __post_init__(self) -> None:
        """Walidacja karty po utworzeniu."""
        valid_suits = {"hearts", "diamonds", "clubs", "spades"}
        valid_ranks = {"2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"}
        
        if self.suit not in valid_suits:
            raise ValueError(f"Nieprawidłowy kolor karty: {self.suit}")
        if self.rank not in valid_ranks:
            raise ValueError(f"Nieprawidłowa ranga karty: {self.rank}")
    
    @property
    def value(self) -> int:
        """
        Zwraca wartość punktową karty.
        
        Returns:
            int: Wartość punktowa (As = 11, figury = 10, reszta = wartość nominalna).
        """
        return self.RANK_VALUES[self.rank]
    
    def to_dict(self) -> Dict[str, any]:
        """
        Konwertuje kartę do słownika.
        
        Returns:
            Dict: Słownik z danymi karty.
        """
        return {
            "suit": self.suit,
            "rank": self.rank,
            "value": self.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, any]) -> "Card":
        """
        Tworzy kartę ze słownika.
        
        Args:
            data: Słownik z kluczami 'suit' i 'rank'.
            
        Returns:
            Card: Nowa instancja karty.
        """
        return cls(suit=data["suit"], rank=data["rank"])
    
    def __str__(self) -> str:
        """Tekstowa reprezentacja karty."""
        suit_symbols = {
            "hearts": "♥",
            "diamonds": "♦",
            "clubs": "♣",
            "spades": "♠"
        }
        return f"{self.rank}{suit_symbols.get(self.suit, self.suit)}"


class Deck:
    """
    Talia 52 kart do gry w Blackjack.
    
    Zarządza talią kart, umożliwia tasowanie i dobieranie kart.
    
    Attributes:
        cards: Lista kart w talii.
    """
    
    SUITS: List[str] = ["hearts", "diamonds", "clubs", "spades"]
    RANKS: List[str] = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
    
    def __init__(self) -> None:
        """Inicjalizuje talię kart."""
        self.cards: List[Card] = []
        self._create_deck()
    
    def _create_deck(self) -> None:
        """Tworzy pełną talię kart."""
        self.cards = []
        for suit in self.SUITS:
            for rank in self.RANKS:
                self.cards.append(Card(suit, rank))
    
    def shuffle(self) -> None:
        """Tasuje talię kart."""
        random.shuffle(self.cards)
    
    def draw(self) -> Optional[Card]:
        """
        Dobiera kartę z wierzchu talii.
        
        Returns:
            Card: Dobrana karta lub None jeśli talia pusta.
        """
        if self.cards:
            return self.cards.pop()
        return None
    
    def to_list(self) -> List[Dict[str, any]]:
        """
        Konwertuje talię do listy słowników.
        
        Returns:
            List[Dict]: Lista kart jako słowniki.
        """
        return [card.to_dict() for card in self.cards]
    
    @classmethod
    def from_list(cls, cards_data: List[Dict[str, any]]) -> "Deck":
        """
        Tworzy talię z listy słowników.
        
        Args:
            cards_data: Lista słowników z danymi kart.
            
        Returns:
            Deck: Nowa talia z podanymi kartami.
        """
        deck = cls.__new__(cls)
        deck.cards = [Card.from_dict(card) for card in cards_data]
        return deck
    
    def __len__(self) -> int:
        """Zwraca liczbę kart w talii."""
        return len(self.cards)


class Hand:
    """
    Ręka gracza - zbiór kart.
    
    Zarządza kartami gracza i oblicza wynik punktowy.
    
    Attributes:
        cards: Lista kart na ręce.
    """
    
    def __init__(self, cards: Optional[List[Card]] = None) -> None:
        """
        Inicjalizuje rękę gracza.
        
        Args:
            cards: Opcjonalna lista początkowych kart.
        """
        self.cards: List[Card] = cards if cards else []
    
    def add_card(self, card: Card) -> None:
        """
        Dodaje kartę do ręki.
        
        Args:
            card: Karta do dodania.
        """
        self.cards.append(card)
    
    def calculate_score(self) -> int:
        """
        Oblicza wynik punktowy ręki.
        
        Automatycznie dostosowuje wartość asów (11 lub 1)
        aby uzyskać najlepszy wynik bez przekroczenia 21.
        
        Returns:
            int: Wynik punktowy.
        """
        score = sum(card.value for card in self.cards)
        aces = sum(1 for card in self.cards if card.rank == "A")
        
        while score > 21 and aces > 0:
            score -= 10
            aces -= 1
        
        return score
    
    def is_blackjack(self) -> bool:
        """
        Sprawdza czy ręka to Blackjack (21 z dwóch pierwszych kart).
        
        Returns:
            bool: True jeśli Blackjack.
        """
        return len(self.cards) == 2 and self.calculate_score() == 21
    
    def is_bust(self) -> bool:
        """
        Sprawdza czy ręka przekroczyła 21 (przegrana).
        
        Returns:
            bool: True jeśli bust (powyżej 21).
        """
        return self.calculate_score() > 21
    
    def to_list(self) -> List[Dict[str, any]]:
        """
        Konwertuje rękę do listy słowników.
        
        Returns:
            List[Dict]: Lista kart jako słowniki.
        """
        return [card.to_dict() for card in self.cards]
    
    @classmethod
    def from_list(cls, cards_data: List[Dict[str, any]]) -> "Hand":
        """
        Tworzy rękę z listy słowników.
        
        Args:
            cards_data: Lista słowników z danymi kart.
            
        Returns:
            Hand: Nowa ręka z podanymi kartami.
        """
        cards = [Card.from_dict(card) for card in cards_data]
        return cls(cards)
    
    def __len__(self) -> int:
        """Zwraca liczbę kart na ręce."""
        return len(self.cards)
    
    def __str__(self) -> str:
        """Tekstowa reprezentacja ręki."""
        return ", ".join(str(card) for card in self.cards)


class BlackjackGame:
    """
    Główna klasa logiki gry Blackjack.
    
    Zarządza przebiegiem gry, w tym rozdaniem kart, 
    akcjami gracza oraz ustaleniem zwycięzcy.
    Krupier gra automatycznie według zasad (dobiera do 17).
    
    Attributes:
        deck: Talia kart.
        player_hand: Ręka gracza.
        dealer_hand: Ręka krupiera.
        game_over: Czy gra zakończona.
        player_stood: Czy gracz spasował.
    """
    
    DEALER_STAND_VALUE: int = 17
    
    def __init__(self, deck: Optional[Deck] = None,
                 player_hand: Optional[Hand] = None,
                 dealer_hand: Optional[Hand] = None) -> None:
        """
        Inicjalizuje nową grę w Blackjack.
        
        Args:
            deck: Opcjonalna talia kart (domyślnie nowa potasowana).
            player_hand: Opcjonalna ręka gracza.
            dealer_hand: Opcjonalna ręka krupiera.
        """
        self.deck = deck if deck else Deck()
        if not deck:
            self.deck.shuffle()
        
        self.player_hand = player_hand if player_hand else Hand()
        self.dealer_hand = dealer_hand if dealer_hand else Hand()
        self.game_over: bool = False
        self.player_stood: bool = False
    
    def deal_initial_cards(self) -> None:
        """
        Rozdaje początkowe karty (po 2 dla gracza i krupiera).
        
        Gracz otrzymuje obie karty odkryte, krupier ma jedną zakrytą.
        """
        for _ in range(2):
            card = self.deck.draw()
            if card:
                self.player_hand.add_card(card)
        
        for _ in range(2):
            card = self.deck.draw()
            if card:
                self.dealer_hand.add_card(card)
        
        # Sprawdź czy ktoś ma Blackjacka
        if self.player_hand.is_blackjack() or self.dealer_hand.is_blackjack():
            self.game_over = True
    
    def player_hit(self) -> Optional[Card]:
        """
        Gracz dobiera kartę (hit).
        
        Returns:
            Card: Dobrana karta lub None jeśli gra zakończona.
        """
        if self.game_over or self.player_stood:
            return None
        
        card = self.deck.draw()
        if card:
            self.player_hand.add_card(card)
            
            if self.player_hand.is_bust():
                self.game_over = True
        
        return card
    
    def player_stand(self) -> None:
        """
        Gracz pasuje (stand) - kończy dobieranie kart.
        
        Uruchamia turę krupiera.
        """
        if self.game_over:
            return
        
        self.player_stood = True
        self._dealer_play()
        self.game_over = True
    
    def _dealer_play(self) -> None:
        """
        Wykonuje turę krupiera według standardowych zasad.
        
        Krupier dobiera karty dopóki ma mniej niż 17 punktów.
        """
        while self.dealer_hand.calculate_score() < self.DEALER_STAND_VALUE:
            card = self.deck.draw()
            if card:
                self.dealer_hand.add_card(card)
            else:
                break
    
    def determine_winner(self) -> str:
        """
        Określa zwycięzcę gry.
        
        Returns:
            str: Wynik gry ('player_won', 'dealer_won', 'tie').
        """
        player_score = self.player_hand.calculate_score()
        dealer_score = self.dealer_hand.calculate_score()
        
        if self.player_hand.is_bust():
            return "dealer_won"
        
        if self.dealer_hand.is_bust():
            return "player_won"
        
        if self.player_hand.is_blackjack() and not self.dealer_hand.is_blackjack():
            return "player_won"
        
        if self.dealer_hand.is_blackjack() and not self.player_hand.is_blackjack():
            return "dealer_won"
        
        if self.player_hand.is_blackjack() and self.dealer_hand.is_blackjack():
            return "tie"
        
        if player_score > dealer_score:
            return "player_won"
        elif dealer_score > player_score:
            return "dealer_won"
        else:
            return "tie"
    
    def get_state(self) -> Dict[str, any]:
        """
        Zwraca aktualny stan gry.
        
        Returns:
            Dict: Słownik ze stanem gry.
        """
        return {
            "player_hand": self.player_hand.to_list(),
            "dealer_hand": self.dealer_hand.to_list(),
            "player_score": self.player_hand.calculate_score(),
            "dealer_score": self.dealer_hand.calculate_score(),
            "deck_remaining": len(self.deck),
            "game_over": self.game_over,
            "player_stood": self.player_stood
        }
    
    @classmethod
    def from_state(cls, player_hand_data: List[Dict],
                   dealer_hand_data: List[Dict],
                   deck_data: List[Dict]) -> "BlackjackGame":
        """
        Odtwarza grę ze stanu.
        
        Args:
            player_hand_data: Dane ręki gracza.
            dealer_hand_data: Dane ręki krupiera.
            deck_data: Dane talii.
            
        Returns:
            BlackjackGame: Odtworzona gra.
        """
        deck = Deck.from_list(deck_data)
        player_hand = Hand.from_list(player_hand_data)
        dealer_hand = Hand.from_list(dealer_hand_data)
        
        return cls(deck=deck, player_hand=player_hand, dealer_hand=dealer_hand)
