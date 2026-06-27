import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

from utils import (deck, rank_value, player_hand, ai_hand, table_cards, table_ranks, attack_defense_cards, discard, 
                   trump_suit, attacker, defender, deal_card, set_first_attacker, player_attack, player_defend, player_take_cards, player_end_round,
                   ai_move, hint, check_game_over)

class DurakApp:
    def __init__(self, root, deck):
        self.root = root
        self.root.title("Durak - Card Game")
        self.root.geometry("1100x750")
        self.root.configure(bg = "#1a1a2e")
        self.root.resizable(False, False)
        self.deck = deck
        self.rank_value = {}
        for card in deck:
            rank = card[:-1]
            if rank.isdigit():
                self.rank_value[card] = int(rank)
            elif rank == 'J':
                self.rank_value[card] = 11
            elif rank == 'Q':
                self.rank_value[card] = 12
            elif rank == 'K':
                self.rank_value[card] = 13
            else:
                self.rank_value[card] = 14
        self.player_hand = []
        self.ai_hand = []
        self.table_cards = []
        self.table_ranks = [card[:-1] for card in table_cards]
        self.attack_defense_cards = {}
        self.discard = []
        self.trump_suit = None
        self.attacker = None
        self.defender = None
        self.selected_card = None
        self.selected_attack = None
        self.card_images = {}
        all_cards = ['6♠', '7♠', '8♠', '9♠', '10♠', 'J♠', 'Q♠', 'K♠', 'A♠',
             '6♣', '7♣', '8♣', '9♣', '10♣', 'J♣', 'Q♣', 'K♣', 'A♣',
             '6♥', '7♥', '8♥', '9♥', '10♥', 'J♥', 'Q♥', 'K♥', 'A♥',
             '6♦', '7♦', '8♦', '9♦', '10♦', 'J♦', 'Q♦', 'K♦', 'A♦']
        for card in all_cards:
            if card[-1] == "♣":
                card_name = card[:-1] + "C"
            elif card[-1] == "♠":
                card_name = card[:-1] + "S"
            elif card[-1] == "♥":
                card_name = card[:-1] + "H"
            else:
                card_name = card[:-1] + "D"
            path = f"{card_name}.png"
            img = Image.open(path).resize((60, 90))
            self.card_images[card_name] = ImageTk.PhotoImage(img)
        self.card_images["back"] = ImageTk.PhotoImage(Image.open("back.png").resize((60, 90)))
        self.build_ui()
        self.new_game()

    def build_ui(self):
        # Header
        header = tk.Frame(self.root, bg = "#26345a", height = 48)
        header.pack(fill = "x")

        lbl_header1 = tk.Label(header, text = "Durak", font = ("Arial", 18, "bold"), bg = "#26345a", fg = "#f5a623")
        lbl_header1.pack(side = "left", padx = 20, pady = 8)
        lbl_header2 = tk.Label(header, text = "Learn. Play. Win.", font = ("Arial", 11), bg = "#26345a", fg = "#838c96")
        lbl_header2.pack(side = "left")

        small_frame = tk.Frame(header, bg = "#26345a")
        small_frame.pack(side = "right", padx = 10)
        btn_rules = tk.Button(small_frame, text = "Rules", font = ("Arial", 11, "bold"), bg = "#0f3460", fg = "#ffffff", padx = 10, command = self.show_rules)
        btn_rules.pack(side = "left", padx = 4)
        btn_new_game = tk.Button(small_frame, text = "New Game", font = ("Arial", 11), bg = "#e94560", fg = "#ffffff", padx = 10, command = self.new_game)
        btn_new_game.pack(side = "left", padx = 4)

        # Main Frame
        main = tk.Frame(self.root, bg = "#1a1a2e")
        main.pack(fill = "both", expand = True, padx = 10, pady = 5)

        # Left Panel
        left = tk.Frame(main, bg = "#1a1a2e")
        left.pack(side = "left", fill = "both", expand = True)

        # AI Hand
        ai_frame = tk.Frame(left)
        ai_frame.pack(fill = "x", pady = 4)
        self.ai_canvas = tk.Canvas(ai_frame, bg = "#1a1a2e", height = 100)
        self.ai_canvas.pack(fill = "x", padx = 5, pady = 5)

        # Table
        table_frame = tk.Frame(left)
        table_frame.pack(fill = "both", expand = True, pady = 4)
        self.table_canvas = tk.Canvas(table_frame, bg = "#1e6b3c")
        self.table_canvas.pack(fill = "both", expand = True, padx = 5, pady = 5)

        # Player Hand
        player_frame = tk.Frame(left)
        player_frame.pack(fill = "x", pady = 4)
        self.player_canvas = tk.Canvas(player_frame, bg = "#1a1a2e", height = 120)
        self.player_canvas.pack(fill = "x", padx = 5, pady = 5)

        # Right Panel
        right = tk.Frame(main, bg = "#1a1a2e", width = 220)
        right.pack(side = "right", fill = "y", padx = 8)
        right.pack_propagate(False)

        # Status
        tk.Label(right, text = "STATUS", font = ("Arial", 11), bg = "#1a1a2e", fg = "#f5a623").pack(pady = 2)
        self.status_lbl = tk.Label(right, text = "...", font = ("Arial", 12, "bold"), bg = "#1a1a2e", fg = "#ffffff")
        self.status_lbl.pack(padx = 6, pady = 4)

        # Hint
        self.hint_lbl = tk.Label(right, text = "Hint will appear here", font = ("Arial", 10), bg = "#1a1a2e", fg = "#f39c12")
        self.hint_lbl.pack(padx = 6, pady = 4)

        # Deck and Trump
        tk.Label(right, text = "Deck & Trump", font = ("Arial", 11), bg = "#1a1a2e", fg = "#f5a623").pack(pady = 2)
        self.deck_lbl = tk.Label(right, text = "", font = ("Arial", 11), bg = "#1a1a2e", fg = "#838c96")
        self.deck_lbl.pack()
        self.trump_lbl = tk.Label(right, text = "", font = ("Arial", 16, "bold"), bg = "#1a1a2e", fg = "#ffffff")
        self.trump_lbl.pack(pady = 2)

        # Action Buttons
        tk.Label(right, text="ACTIONS", font = ("Arial", 11), bg = "#1a1a2e", fg = "#f5a623").pack(pady = 2)

        self.btn_attack = tk.Button(right, text="Attack / Add Card", font = ("Arial", 11, "bold"), bg = "#0f3460", fg = "#ffffff", pady = 6, command = self.action_attack)
        self.btn_attack.pack(fill = "x", padx = 10, pady = 3)

        self.btn_defend = tk.Button(right, text="Defend Selected", font = ("Arial", 11, "bold"), bg = "#0f3460", fg = "#ffffff", pady = 6, command = self.action_defend)
        self.btn_defend.pack(fill = "x", padx = 10, pady = 3)

        self.btn_take = tk.Button(right, text="Take Cards", font = ("Arial", 11, "bold"), bg = "#0f3460", fg = "#ffffff", pady = 6, command = self.action_take_cards)
        self.btn_take.pack(fill = "x", padx = 10, pady = 3)

        self.btn_end = tk.Button(right, text="End Round", font = ("Arial", 11, "bold"), bg = "#0f3460", fg = "#ffffff", pady = 6, command = self.action_end_round)
        self.btn_end.pack(fill = "x", padx = 10, pady = 3)

        # Event Log
        tk.Label(right, text = "EVENT LOG", font = ("Arial", 11), bg = "#1a1a2e", fg = "#f5a623").pack(pady = 2)
        log_frame = tk.Frame(right, bg = "#1a1a2e")
        log_frame.pack(fill = "both", expand = True, padx = 6)
        self.log_text = tk.Text(log_frame, font = ("Arial", 9), bg = "#26345a", fg = "#838c96", bd = 0, height = 10, state = "disabled", wrap = "word")
        self.log_text.pack(fill = "both", expand = True)


    # Cards
    def draw_card(self, canvas, x, y, card, face_up, tag):
        if card[-1] == "♣":
            card_name = card[:-1] + "C"
        elif card[-1] == "♠":
            card_name = card[:-1] + "S"
        elif card[-1] == "♥":
            card_name = card[:-1] + "H"
        else:
            card_name = card[:-1] + "D"
        img = self.card_images[card_name] if face_up else self.card_images["back"]
        canvas.create_image(x, y, anchor = "nw", image = img, tags = tag)


    # Render
    def render(self):
        import utils
        self.attacker = utils.attacker
        self.defender = utils.defender
        self.trump_suit = utils.trump_suit
        self.render_player_hand()
        self.render_ai_hand()
        self.render_table()
        self.update_info()

    def render_player_hand(self):
        self.player_canvas.delete('all')
        x = 10
        for card in self.player_hand:
            tag = f"{card}"
            selected = False
            if card == self.selected_card:
                selected = True
            y = 0 if selected else 10
            self.draw_card(self.player_canvas, x, y, card, face_up = True, tag = tag)
            self.player_canvas.tag_bind(tag, "<Button-1>", lambda e, c = card: self.select_card(c))
            x += 70

    def render_ai_hand(self):
        self.ai_canvas.delete("all")
        x = 10
        y = 0
        for card in self.ai_hand:
            tag = f"{card}"
            self.draw_card(self.ai_canvas, x, y, card, face_up = False, tag = tag)
            x += 70

    def render_table(self):
        self.table_canvas.delete("all")
        space = 90
        x_attack = 20
        x_defense = 18
        y_defense = 20
        for i, (attack, defense) in enumerate(self.attack_defense_cards.items()):
            x = x_attack + i * space
            tag = f"{attack}"
            is_target = False
            if attack == self.selected_attack:
                is_target = True
            y_attack = 30 if is_target else 20
            self.draw_card(self.table_canvas, x, y_attack, attack, face_up = True, tag = tag)
            if self.defender == "player" and defense is None:
                self.table_canvas.tag_bind(tag, "<Button-1>", lambda e, a = attack: self.select_attack(a))
            if defense:
                self.draw_card(self.table_canvas, x + x_defense, y_attack + y_defense, defense, face_up = True, tag = f"{defense}")

    def select_card(self, card):
        self.selected_card = card
        self.render()

    def select_attack(self, attack):
        self.selected_attack = attack
        self.render()

    def update_info(self):
        if self.attacker == "player":
            status_text = "Your turn to attack"
        elif self.defender == "player":
            status_text = "Your turn to defend"
        else:
            status_text = "AI is thinking..."
        self.status_lbl.config(text = status_text)

        hint_text = hint()
        if hint_text:
            self.hint_lbl.config(text = hint_text)

        self.deck_lbl.config(text = f"Cards left: {len(self.deck)}")
        self.trump_lbl.config(text = f"Trump: {self.trump_suit}")


    # Actions

    def action_attack(self):
        if not self.selected_card:
            self.append_event_to_log("You should select a card before moving.")
            return
        
        result = player_attack(self.selected_card)
        self.append_event_to_log(result)
        self.selected_card = None
        self.selected_attack = None
        self.render()

        over = check_game_over()
        if over:
            self.show_game_over()
            return
        
        self.root.after(800, self.ai_step)

    def action_defend(self):
        if not self.selected_card or not self.selected_attack:
            self.append_event_to_log("You should select both defend and attack card.")
            return
        
        result = player_defend(self.selected_card, self.selected_attack)
        self.append_event_to_log(result)
        self.selected_card = None
        self.selected_attack = None
        self.render()

        over = check_game_over()
        if over:
            self.show_game_over()
            return
        
        self.root.after(800, self.ai_step)

    def action_take_cards(self):
        result = player_take_cards()
        self.append_event_to_log(result)
        self.selected_card = None
        self.selected_attack = None
        self.render()

        over = check_game_over()
        if over:
            self.show_game_over()
            return
        
        self.root.after(800, self.ai_step)

    def action_end_round(self):
        result = player_end_round()
        self.append_event_to_log(result)
        self.selected_card = None
        self.selected_attack = None
        self.render()

        over = check_game_over()
        if over:
            self.show_game_over()
            return
        
        self.root.after(800, self.ai_step)

    def ai_step(self):
        import utils
        if not self.ai_hand:
            return
        result = ai_move()
        self.append_event_to_log(result)
        self.render()
        over = check_game_over()
        if over:
            self.show_game_over()
        self.attacker = utils.attacker
        self.defender = utils.defender

    def append_event_to_log(self, message):
        self.log_text.config(state = "normal")
        self.log_text.insert("end", f"{message} \n")
        self.log_text.see("end")
        self.log_text.config(state = "disabled")

    def show_game_over(self):
        result = check_game_over()
        if result[1] == "player":
            title = "You Win!"
            message = ("Congratulations! You got rid of all cards. \n"
                       "The AI is the Durak!")
        elif result[1] == "ai":
            title = "You Lose!"
            message = "You are the Durak! Better luck next time."
        else:
            title = "Draw!"
            message = "Both emtied their hands at the same time."
        if messagebox.askyesno(title, message + "\n\nPlay again?"):
            self.new_game()
        else:
            self.root.destroy()
        
    def new_game(self):
        import utils
        utils.init_game()
        self.deck = utils.deck
        self.player_hand = utils.player_hand
        self.ai_hand = utils.ai_hand
        self.table_cards = utils.table_cards
        self.attack_defense_cards = utils.attack_defense_cards
        self.discard = utils.discard
        self.trump_suit = utils.trump_suit
        self.attacker = utils.attacker
        self.defender = utils.defender
        self.log_text.config(state = "normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state = "disabled")
        self.render()

        if self.attacker == "ai":
            self.root.after(800, self.ai_step)


    # Rules Window
        
    def show_rules(self):
        sections = [
            ("♠ DURAK — RULES & GUIDE ♣", "header"),
            ("", "body"),
            ("OBJECTIVE", "section"),
            ("Get rid of all your cards first.\nThe last player holding cards is the Durak (fool) and loses.", "body"),
            ("", "body"),
            ("SETUP", "section"),
            ("  •  36 cards: ranks 6 through Ace in 4 suits\n"
             "  •  Each player is dealt 6 cards\n"
             "  •  The bottom card of the deck sets the Trump suit\n"
             "  •  The player holding the lowest trump attacks first", "body"),
            ("GAMEPLAY", "section"),
            ("  1.  The Attacker plays one card face-up on the table.\n"
            "  2.  The Defender must beat it with either:\n"
            "      A higher card of the SAME suit, OR\n"
            "      Any TRUMP card (if the attack is not trump).\n"
            "  3.  The Attacker may add more cards, but only if\n"
            "        their rank already appears on the table.\n"
            "        Maximum 6 attack cards per round.\n"
            "  4.  If the Defender cannot beat a card, they must\n"
            "      TAKE all cards from the table.\n"
            "  5.  If all attacks are defended, cards go to discard.\n"
            "  6.  Both players refill their hands to 6 from the deck.", "body"),
            ("", "body"),
            ("TRUMP CARDS", "section"),
            ("A trump card beats ANY non-trump card, regardless of rank.\n"
            "A higher trump beats a lower trump.\n"
            "The trump suit is shown by the rotated card at the bottom\n"
            "of the deck pile on the table.", "body"),
            ("", "body"),
            ("WINNING", "section", ),
            ("  ✔  Empty your hand = you WIN\n"
            "  ✘  Last one holding cards = you LOSE (Durak!)\n"
            "  ═  Both empty at once = Draw", "body"),
            ("", "body"),
            ("BEGINNER TIPS", "section"),
            ("Save trump cards — use them only when necessary\n"
            "Open attacks with your lowest non-trump cards\n"
            "Track which ranks are on the table so you know\n"
            "what you can legally add to the attack\n"
            "Taking cards is sometimes smarter than burning\n"
            "a trump on a weak attack\n"
            "Watch the AI's hand size — a small hand means\n"
            "they may be close to winning", "body"),
            ("", "body"),
            ("CONTROLS", "section"),
            ("Click a card in your hand → select it (lifts up)\n"
            "Click a table card → select it as defense target\n"
            "Attack button → play selected card as attack\n"
            "Defend button → play selected card to defend\n"
            "Take Cards → give up defending, take all\n"
            "End Round → finish your attack turn", "body")
        ]
        
        rules = tk.Toplevel(self.root)
        rules.title("Durak - Rules & Guide")
        rules.geometry("480x500")
        rules.configure(bg = "#26345a")
        rules.resizable(False, False)

        rule_frame = tk.Frame(rules, bg="#26345a")
        rule_frame.pack(fill = "both", expand = True)

        text = tk.Text(rule_frame, font = ("Arial", 11), bg = "#26345a", fg = "#ffffff", bd = 0, highlightthickness = 0, wrap = "word", padx = 20, pady = 14, state = "disabled", spacing1 = 2, spacing2 = 3, spacing3 = 4)
        text.pack(side = "left", fill = "both", expand = True)
        scrollbar = tk.Scrollbar(rule_frame, orient = "vertical")
        scrollbar.pack(side = "right", fill = "y")
        text.configure(yscrollcommand = scrollbar.set)
        scrollbar.config(command = text.yview)

        text.tag_config("header", font = ("Arial", 14, "bold"), fg = "#f5a623", justify = "center", spacing1 = 8, spacing3 = 8)
        text.tag_config("section", font = ("Arial", 11, "bold"), fg = "#f5a623", spacing1 = 10, spacing3 = 2)
        text.tag_config("body", font = ("Arial", 11), fg = "#ffffff", spacing1 = 1, spacing3 = 1)

        text.config(state = "normal")
        for content, tag in sections:
            text.insert("end", content + "\n", tag)
        text.config(state = "disabled")
        
        def scroll(event):
            text.yview_scroll(int(-1 * (event.delta / 120)), "units")

        rules.bind("<MouseWheel>", scroll)
        rules.bind("<Button-4>", lambda e: text.yview_scroll(-1, "units"))
        rules.bind("<Button-5>", lambda e: text.yview_scroll(1, "units"))
        
        tk.Button(rules, text = "Got it!", font = ("Arial", 11, "bold"), bg = "#e94560", fg = "#ffffff", padx = 20, pady = 6, command = rules.destroy).pack(pady = 10)
        


if __name__ == "__main__":
    root = tk.Tk()
    app = DurakApp(root, deck)

    root.mainloop()