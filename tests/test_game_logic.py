"""
Testy jednostkowe dla logiki gry Blackjack.
"""

import pytest
from app.game_logic import Card, Deck, Hand, BlackjackGame


class TestCard:
    """Testy dla klasy Card."""
    
    def test_card_creation(self):
        """Testuje tworzenie karty."""
        card = Card("hearts", "A")
        assert card.suit == "hearts"
        assert card.rank == "A"
        assert card.value == 11
    
    def test_card_values(self):
        """Testuje wartości kart."""
        assert Card("hearts", "2").value == 2
        assert Card("hearts", "10").value == 10
        assert Card("hearts", "J").value == 10
        assert Card("hearts", "Q").value == 10
        assert Card("hearts", "K").value == 10
        assert Card("hearts", "A").value == 11
    
    def test_card_invalid_suit(self):
        """Testuje błąd dla nieprawidłowego koloru."""
        with pytest.raises(ValueError):
            Card("invalid", "A")
    
    def test_card_invalid_rank(self):
        """Testuje błąd dla nieprawidłowej rangi."""
        with pytest.raises(ValueError):
            Card("hearts", "X")
    
    def test_card_to_dict(self):
        """Testuje konwersję karty do słownika."""
        card = Card("spades", "K")
        data = card.to_dict()
        assert data["suit"] == "spades"
        assert data["rank"] == "K"
        assert data["value"] == 10
    
    def test_card_from_dict(self):
        """Testuje tworzenie karty ze słownika."""
        data = {"suit": "diamonds", "rank": "7"}
        card = Card.from_dict(data)
        assert card.suit == "diamonds"
        assert card.rank == "7"


class TestDeck:
    """Testy dla klasy Deck."""
    
    def test_deck_creation(self):
        """Testuje tworzenie talii."""
        deck = Deck()
        assert len(deck) == 52
    
    def test_deck_shuffle(self):
        """Testuje tasowanie talii."""
        deck1 = Deck()
        deck2 = Deck()
        deck1.shuffle()
        cards1 = [str(c) for c in deck1.cards]
        cards2 = [str(c) for c in deck2.cards]
        assert cards1 != cards2
    
    def test_deck_draw(self):
        """Testuje dobieranie karty."""
        deck = Deck()
        card = deck.draw()
        assert card is not None
        assert isinstance(card, Card)
        assert len(deck) == 51
    
    def test_deck_draw_empty(self):
        """Testuje dobieranie z pustej talii."""
        deck = Deck()
        for _ in range(52):
            deck.draw()
        assert deck.draw() is None
    
    def test_deck_to_list(self):
        """Testuje konwersję talii do listy."""
        deck = Deck()
        cards_list = deck.to_list()
        assert len(cards_list) == 52
        assert all(isinstance(c, dict) for c in cards_list)
    
    def test_deck_from_list(self):
        """Testuje tworzenie talii z listy."""
        deck1 = Deck()
        cards_list = deck1.to_list()
        deck2 = Deck.from_list(cards_list)
        assert len(deck2) == 52


class TestHand:
    """Testy dla klasy Hand."""
    
    def test_hand_creation(self):
        """Testuje tworzenie ręki."""
        hand = Hand()
        assert len(hand) == 0
    
    def test_hand_add_card(self):
        """Testuje dodawanie karty."""
        hand = Hand()
        hand.add_card(Card("hearts", "A"))
        assert len(hand) == 1
    
    def test_hand_calculate_score(self):
        """Testuje obliczanie wyniku."""
        hand = Hand()
        hand.add_card(Card("hearts", "5"))
        hand.add_card(Card("spades", "10"))
        assert hand.calculate_score() == 15
    
    def test_hand_ace_adjustment(self):
        """Testuje automatyczną redukcję wartości asa."""
        hand = Hand()
        hand.add_card(Card("hearts", "A"))
        hand.add_card(Card("spades", "A"))
        hand.add_card(Card("diamonds", "9"))
        assert hand.calculate_score() == 21
    
    def test_hand_multiple_aces(self):
        """Testuje wiele asów."""
        hand = Hand()
        hand.add_card(Card("hearts", "A"))
        hand.add_card(Card("spades", "A"))
        hand.add_card(Card("diamonds", "A"))
        hand.add_card(Card("clubs", "8"))
        assert hand.calculate_score() == 21
    
    def test_hand_is_blackjack(self):
        """Testuje sprawdzanie Blackjacka."""
        hand = Hand()
        hand.add_card(Card("hearts", "A"))
        hand.add_card(Card("spades", "K"))
        assert hand.is_blackjack() is True
    
    def test_hand_is_not_blackjack(self):
        """Testuje sprawdzanie gdy nie ma Blackjacka."""
        hand = Hand()
        hand.add_card(Card("hearts", "10"))
        hand.add_card(Card("spades", "K"))
        assert hand.is_blackjack() is False
    
    def test_hand_is_bust(self):
        """Testuje sprawdzanie przekroczenia 21."""
        hand = Hand()
        hand.add_card(Card("hearts", "K"))
        hand.add_card(Card("spades", "K"))
        hand.add_card(Card("diamonds", "5"))
        assert hand.is_bust() is True
    
    def test_hand_to_list(self):
        """Testuje konwersję ręki do listy."""
        hand = Hand()
        hand.add_card(Card("hearts", "A"))
        hand.add_card(Card("spades", "K"))
        cards_list = hand.to_list()
        assert len(cards_list) == 2


class TestBlackjackGame:
    """Testy dla klasy BlackjackGame."""
    
    def test_game_creation(self):
        """Testuje tworzenie gry."""
        game = BlackjackGame()
        assert game.game_over is False
        assert game.player_stood is False
    
    def test_game_deal_initial_cards(self):
        """Testuje początkowe rozdanie kart."""
        game = BlackjackGame()
        game.deal_initial_cards()
        assert len(game.player_hand) == 2
        assert len(game.dealer_hand) == 2
    
    def test_game_player_hit(self):
        """Testuje dobieranie karty przez gracza."""
        game = BlackjackGame()
        game.deal_initial_cards()
        initial_count = len(game.player_hand)
        card = game.player_hit()
        assert card is not None
        assert len(game.player_hand) == initial_count + 1
    
    def test_game_player_stand(self):
        """Testuje pasowanie gracza."""
        game = BlackjackGame()
        game.deal_initial_cards()
        game.player_stand()
        assert game.player_stood is True
        assert game.game_over is True
    
    def test_game_determine_winner_player_bust(self):
        """Testuje wygraną krupiera gdy gracz przekroczy 21."""
        game = BlackjackGame()
        game.player_hand.add_card(Card("hearts", "K"))
        game.player_hand.add_card(Card("spades", "K"))
        game.player_hand.add_card(Card("diamonds", "K"))
        game.dealer_hand.add_card(Card("clubs", "5"))
        game.dealer_hand.add_card(Card("hearts", "5"))
        
        assert game.determine_winner() == "dealer_won"
    
    def test_game_determine_winner_dealer_bust(self):
        """Testuje wygraną gracza gdy krupier przekroczy 21."""
        game = BlackjackGame()
        game.player_hand.add_card(Card("hearts", "10"))
        game.player_hand.add_card(Card("spades", "8"))
        game.dealer_hand.add_card(Card("clubs", "K"))
        game.dealer_hand.add_card(Card("hearts", "K"))
        game.dealer_hand.add_card(Card("diamonds", "5"))
        
        assert game.determine_winner() == "player_won"
    
    def test_game_determine_winner_tie(self):
        """Testuje remis."""
        game = BlackjackGame()
        game.player_hand.add_card(Card("hearts", "10"))
        game.player_hand.add_card(Card("spades", "8"))
        game.dealer_hand.add_card(Card("clubs", "10"))
        game.dealer_hand.add_card(Card("diamonds", "8"))
        
        assert game.determine_winner() == "tie"
    
    def test_game_get_state(self):
        """Testuje pobieranie stanu gry."""
        game = BlackjackGame()
        game.deal_initial_cards()
        state = game.get_state()
        
        assert "player_hand" in state
        assert "dealer_hand" in state
        assert "player_score" in state
        assert "dealer_score" in state
        assert "game_over" in state
    
    def test_game_from_state(self):
        """Testuje odtwarzanie gry ze stanu."""
        game1 = BlackjackGame()
        game1.deal_initial_cards()
        state = game1.get_state()
        
        game2 = BlackjackGame.from_state(
            player_hand_data=state["player_hand"],
            dealer_hand_data=state["dealer_hand"],
            deck_data=game1.deck.to_list()
        )
        
        assert len(game2.player_hand) == len(game1.player_hand)
        assert len(game2.dealer_hand) == len(game1.dealer_hand)
