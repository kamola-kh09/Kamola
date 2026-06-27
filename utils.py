import random

# initialization
deck = []
rank_value = {}
player_hand = []
ai_hand = []
table_cards = []
table_ranks = []
attack_defense_cards = {}
discard = []
trump_suit = None
attacker = None
defender = None

def init_game():
    global deck, rank_value, trump_suit, attacker, defender
    deck[:] = ['6♠', '7♠', '8♠', '9♠', '10♠', 'J♠', 'Q♠', 'K♠', 'A♠', 
            '6♣', '7♣', '8♣', '9♣', '10♣', 'J♣', 'Q♣', 'K♣', 'A♣', 
            '6♥', '7♥', '8♥', '9♥', '10♥', 'J♥', 'Q♥', 'K♥', 'A♥', 
            '6♦', '7♦', '8♦', '9♦', '10♦', 'J♦', 'Q♦', 'K♦', 'A♦']
    for card in deck:
        rank = card[:-1]
        if rank.isdigit(): 
            rank_value[card] = int(rank)
        elif rank == 'J': 
            rank_value[card] = 11
        elif rank == 'Q': 
            rank_value[card] = 12
        elif rank == 'K': 
            rank_value[card] = 13
        else: 
            rank_value[card] = 14
    player_hand[:] = []
    ai_hand[:] = []
    table_cards[:] = []
    attack_defense_cards.clear()
    discard[:] = []

    random.shuffle(deck)
    for _ in range(6):
        deal_card(player_hand)
        deal_card(ai_hand)

    trump_suit = deck[0][-1]
    set_first_attacker()


# deal the cards
def deal_card(turn):
    if not deck:
        return
    card = random.choice(deck)
    turn.append(card)
    deck.remove(card)

# set first attacker
def set_first_attacker():
    global attacker, defender
    player_trumps = [card for card in player_hand if card[-1] == trump_suit]
    ai_trumps = [card for card in ai_hand if card[-1] == trump_suit]
    if player_trumps and ai_trumps:
        lowest_player_trump = min(player_trumps, key = lambda card: rank_value[card])
        lowest_ai_trump = min(ai_trumps, key = lambda card: rank_value[card])
        if rank_value[lowest_player_trump] < rank_value[lowest_ai_trump]:
            attacker = "player"
            defender = "ai"
        else:
            attacker = "ai"
            defender = "player"
    elif not player_trumps:
        attacker = "ai"
        defender = "player"
    elif not ai_trumps:
        attacker = "player"
        defender = "ai"
    else:
        attacker = "player"
        defender = "ai"
    return attacker, defender

# player functions
def player_attack(card):
    global table_ranks
    if attacker != "player":
        return "It is not your turn to attack."
    if table_cards:
        table_ranks = [card[:-1] for card in table_cards]
        if len(table_cards) < 12:
            valid = []
            for card in player_hand:
                if card[-1] in table_ranks:
                    valid.append(card)
            if card in valid:
                player_hand.remove(card)
                table_cards.append(card)
                table_ranks = [card[:-1] for card in table_cards]
                attack_defense_cards[card] = None
                return f"You attacked with {card}."
            else:
                return f"You cannot attack with {card}, there is no such rank on table."
        else:
            return "The table is full, you cannot attack more."
    else:
        player_hand.remove(card)
        table_cards.append(card)
        table_ranks = [card[:-1] for card in table_cards]
        attack_defense_cards[card] = None
        return f"You started attacking with {card}."

def player_defend(card, attack):
    global table_ranks
    if defender != "player":
        return "It is not your turn to defend."
    if card[-1] == attack[-1]:
        if rank_value[card] > rank_value[attack]:
            player_hand.remove(card)
            table_cards.append(card)
            table_ranks = [card[:-1] for card in table_cards]
            attack_defense_cards[attack] = card
            return f"You defended {attack} with {card}."
        else:
            return f"You cannot beat {attack} with {card}."
    if card[-1] == trump_suit:
        player_hand.remove(card)
        table_cards.append(card)
        table_ranks = [card[:-1] for card in table_cards]
        attack_defense_cards[attack] = card
        return f"You defended {attack} with {card}."
    else:
        return f"You cannot beat {attack} with {card}."

def player_take_cards():
    global attacker, defender, table_ranks
    if defender != "player":
        return "You cannot take cards, it is not you defending."
    player_hand.extend(table_cards)
    table_cards.clear()
    table_ranks = [card[:-1] for card in table_cards]
    attack_defense_cards.clear()
    while len(ai_hand) < 6:
        deal_card(ai_hand)
    attacker = "ai"
    defender = "player"
    return "You took all cards. It is turn of AI to attack."

def player_end_round():
    global attacker, defender, table_ranks
    if attacker != "player":
        return "You cannot end round. It is not you attacking."
    discard.extend(table_cards)
    table_cards.clear()
    table_ranks = [card[:-1] for card in table_cards]
    attack_defense_cards.clear()
    while len(player_hand) < 6:
        deal_card(player_hand)
    while len(ai_hand) < 6:
        deal_card(ai_hand)
    attacker = "ai"
    defender = "player"
    return "You ended the round. It is now turn of AI to attack."

# ai moves
def ai_move():
    global attacker, defender, table_ranks
    if attacker == "ai":
        if table_cards and len(table_cards) < 12:
            valid = []
            for card in ai_hand:
                if card[:-1] in table_ranks:
                    valid.append(card)
            non_trump_valid = []
            for card in valid:
                if card[-1] != trump_suit:
                    non_trump_valid.append(card)
            if non_trump_valid:
                best = min(non_trump_valid, key = lambda card: rank_value[card])
            elif valid:
                best = min(valid, key = lambda card: rank_value[card])
            else:
                best = None
            if not best:
                discard.extend(table_cards)
                table_cards.clear()
                table_ranks = [card[:-1] for card in table_cards]
                attack_defense_cards.clear()
                while len(ai_hand) < 6:
                    deal_card(ai_hand)
                while len(player_hand) < 6:
                    deal_card(player_hand)
                attacker = "player"
                defender = "ai"
                return f"AI could not attack, it ends round. It is now your turn to attack"
            ai_hand.remove(best)
            table_cards.append(best)
            table_ranks = [card[:-1] for card in table_cards]
            attack_defense_cards[best] = None
            return f"AI attacked with {best}. You should defend."
        elif not table_cards:
            non_trump = [card for card in ai_hand if card[-1] != trump_suit]
            if non_trump:
                best = min(non_trump, key = lambda card: rank_value[card])
            else:
                best = min(ai_hand, key = lambda card: rank_value[card])
            ai_hand.remove(best)
            table_cards.append(best)
            table_ranks = [card[:-1] for card in table_cards]
            attack_defense_cards[best] = None
            return f"AI started attacking with {best}. You should defend."
        else:
            discard.extend(table_cards)
            table_cards.clear()
            table_ranks = [card[:-1] for card in table_cards]
            attack_defense_cards.clear()
            while len(ai_hand) < 6:
                deal_card(ai_hand)
            while len(player_hand) < 6:
                deal_card(player_hand)
            attacker = "player"
            defender = "ai"
            return f"The table is full, this round ends. You should attack next."
        
    elif defender == "ai":
        undefended = [attack for attack, defense in attack_defense_cards.items() if attack_defense_cards[attack] == None]
        for attack in undefended:
            valid_defense = [card for card in ai_hand if (card[-1] == attack[-1] and rank_value[card] > rank_value[attack]) or card[-1] == trump_suit]
            non_trump = [card for card in valid_defense if card[-1] != trump_suit]
            if valid_defense:
                best = min(non_trump if non_trump else valid_defense, key = lambda card: rank_value[card])
                ai_hand.remove(best)
                table_cards.append(best)
                table_ranks = [card[:-1] for card in table_cards]
                attack_defense_cards[attack] = best
            else:
                ai_hand.extend(table_cards)
                table_cards.clear()
                table_ranks = [card[:-1] for card in table_cards]
                attack_defense_cards.clear()
                while len(player_hand) < 6:
                    deal_card(player_hand)
                attacker = "player"
                defender = "ai"
                return "AI could not defend. It takes all cards."
        return "AI defended all. Attack again or end round."
            
# hint
def hint():
    if attacker == "player":
        if not table_cards:
            non_trump_cards = [card for card in player_hand if card[-1] != trump_suit]
            if non_trump_cards:
                best_choice = min(non_trump_cards, key = lambda card: rank_value[card])
                return f"Start with a low non-trump card like {best_choice}."
            return f"You can attack only with trump cards."
        
        valid_cards = [card for card in player_hand if card[:-1] in table_ranks]
        if valid_cards:
            return f"You can add: {', '.join(str(card) for card in valid_cards)}"
        else:
            return "No matching ranks. You should end the round."
            
    if defender == "player":
        undefended = [attack for attack, defense in attack_defense_cards.items() if attack_defense_cards[attack] == None]
        if undefended:
            attack = undefended[0]
            valid_cards = [card for card in player_hand if (card[:-1] == attack[:-1] and rank_value[card] > rank_value[attack]) or card[-1] == trump_suit]
            if not valid_cards:
                return "You cannot beat the attack cards. Consider taking all cards"
            non_trump_valid_cards = [card for card in valid_cards if card[-1] != trump_suit]
                
            best = min(non_trump_valid_cards if non_trump_valid_cards else valid_cards, key = lambda card: rank_value[card])
            return f"Beat {attack} with {best}."

# check for game over and identify the winner
def check_game_over():
    if deck:
        return False
    if not player_hand and not ai_hand:
        winner = 'draw'
        return True, winner
    elif not player_hand:
        winner = 'player'
        return True, winner
    elif not ai_hand:
        winner = 'ai'
        return True, winner