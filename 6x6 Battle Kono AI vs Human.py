import tkinter as tk
from tkinter import messagebox
import math
import copy

BOARD_SIZE = 6
HUMAN = 1
AI = 2
EMPTY = 0
SEARCH_DEPTH = 2
WINNING_SCORE = 70  # 🏆 Win Condition


class BattleKonoGame:
    def __init__(self):
        self.board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_player = HUMAN
        self.human_score = 0
        self.ai_score = 0
        self.game_over = False
        self.initialize_board()

    def initialize_board(self):
        for c in range(BOARD_SIZE):
            self.board[0][c] = AI
            self.board[BOARD_SIZE - 1][c] = HUMAN

    def get_valid_moves(self, row, col):
        moves = []
        piece = self.board[row][col]
        if piece == EMPTY:
            return moves

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                if self.board[nr][nc] == EMPTY:
                    moves.append((nr, nc))
                elif self.board[nr][nc] != piece:
                    jump_r, jump_c = nr + dr, nc + dc
                    if 0 <= jump_r < BOARD_SIZE and 0 <= jump_c < BOARD_SIZE:
                        if self.board[jump_r][jump_c] == EMPTY:
                            moves.append((jump_r, jump_c))
        return moves

    def move_piece(self, fr, fc, tr, tc):
        piece = self.board[fr][fc]
        captured = False

        if abs(fr - tr) == 2 or abs(fc - tc) == 2:
            mid_r = (fr + tr) // 2
            mid_c = (fc + tc) // 2
            if self.board[mid_r][mid_c] != EMPTY:
                self.board[mid_r][mid_c] = EMPTY
                captured = True
                if piece == HUMAN:
                    self.human_score += 2
                else:
                    self.ai_score += 2

        self.board[tr][tc] = piece
        self.board[fr][fc] = EMPTY

        if piece == HUMAN and tr == 0:
            self.human_score += 5
        elif piece == AI and tr == BOARD_SIZE - 1:
            self.ai_score += 5
        else:
            if piece == HUMAN:
                self.human_score += 1
            else:
                self.ai_score += 1

        if self.human_score >= WINNING_SCORE or self.ai_score >= WINNING_SCORE:
            self.game_over = True
            return captured

        self.check_game_over()
        return captured

    def get_all_moves(self, player):
        all_moves = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] == player:
                    for move in self.get_valid_moves(r, c):
                        all_moves.append((r, c, move[0], move[1]))
        return all_moves

    def check_game_over(self):
        human_pieces = sum(row.count(HUMAN) for row in self.board)
        ai_pieces = sum(row.count(AI) for row in self.board)
        
        if human_pieces == 0 or ai_pieces == 0:
            self.game_over = True
            return True
        
        next_player = AI if self.current_player == HUMAN else HUMAN
        if not self.get_all_moves(next_player):
            self.game_over = True
            return True
            
        return False

    def is_game_over(self):
        return self.game_over

    def get_winner(self):
        if self.human_score >= WINNING_SCORE:
            return "Human (70 Points!)"
        elif self.ai_score >= WINNING_SCORE:
            return "AI (70 Points!)"
        elif self.human_score > self.ai_score:
            return "Human"
        elif self.ai_score > self.human_score:
            return "AI"
        else:
            return "Tie"

    def evaluate(self):
        score = self.ai_score - self.human_score
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] == AI:
                    score += r
                elif self.board[r][c] == HUMAN:
                    score -= (BOARD_SIZE - 1 - r)
        return score


class MinimaxAI:
    def choose_move(self, game):
        best_score = -math.inf
        best_move = None
        moves = game.get_all_moves(AI)
        if not moves:
            return None

        for move in moves:
            temp_game = copy.deepcopy(game)
            temp_game.move_piece(*move)
            score = self.minimax(temp_game, SEARCH_DEPTH - 1, False)
            if score > best_score:
                best_score = score
                best_move = move
        return best_move

    def minimax(self, game, depth, maximizing):
        if depth == 0 or game.is_game_over():
            return game.evaluate()

        player = AI if maximizing else HUMAN
        moves = game.get_all_moves(player)
        if not moves:
            return game.evaluate()

        if maximizing:
            best = -math.inf
            for move in moves:
                temp = copy.deepcopy(game)
                temp.move_piece(*move)
                best = max(best, self.minimax(temp, depth - 1, False))
            return best
        else:
            best = math.inf
            for move in moves:
                temp = copy.deepcopy(game)
                temp.move_piece(*move)
                best = min(best, self.minimax(temp, depth - 1, True))
            return best


class GameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Battle Kono AI")
        self.root.resizable(False, False)
        
        # ==========================================
        # 🎨 CUSTOM THEME SETTINGS
        # ==========================================
        self.BG_COLOR = "#121212"        
        self.BOARD_EMPTY = "#1e1e2f"     
        self.BOARD_HUMAN = "#1a237e"     
        self.BOARD_AI = "#4a148c"        
        self.COLOR_SELECTED = "#ffd700"  
        self.COLOR_VALID = "#00e676"     
        self.HUMAN_ICON = "▲"            
        self.HUMAN_COLOR = "#448aff"     
        self.AI_ICON = "▼"               
        self.AI_COLOR = "#ff5252"        
        self.TEXT_COLOR = "#ffffff"
        # ==========================================
        
        # ⏱ TIMER SETTINGS
        self.TURN_TIME_LIMIT = 30  # Seconds per turn
        self.time_left = self.TURN_TIME_LIMIT
        self.timer_running = False
        self.timer_id = None

        # ↩ UNDO SETTINGS
        self.previous_game_state = None

        self.root.configure(bg=self.BG_COLOR)
        
        self.game = BattleKonoGame()
        self.ai = MinimaxAI()
        self.selected = None
        self.valid_moves = []
        self.game_over_shown = False

        # --- UI ELEMENTS ---
        self.status_label = tk.Label(root, text=f"Your Turn (First to {WINNING_SCORE})", 
                                     font=("Arial", 14, "bold"), 
                                     fg=self.HUMAN_COLOR, bg=self.BG_COLOR)
        self.status_label.pack(pady=(10, 5))

        self.score_label = tk.Label(root, text="Human: 0 | AI: 0", 
                                    font=("Arial", 12), 
                                    fg=self.TEXT_COLOR, bg=self.BG_COLOR)
        self.score_label.pack(pady=5)

        # Timer Label
        self.timer_label = tk.Label(root, text=f"⏱ Time: {self.time_left}s", 
                                    font=("Arial", 16, "bold"), 
                                    fg=self.TEXT_COLOR, bg=self.BG_COLOR)
        self.timer_label.pack(pady=5)

        # Board Frame
        board_frame = tk.Frame(root, bg=self.BG_COLOR)
        board_frame.pack(pady=10)

        self.buttons = []
        for r in range(BOARD_SIZE):
            row_buttons = []
            for c in range(BOARD_SIZE):
                btn = tk.Button(board_frame, width=6, height=3,
                                command=lambda r=r, c=c: self.handle_click(r, c),
                                font=("Arial", 16, "bold"), relief="flat", bd=0,
                                activebackground=self.COLOR_SELECTED)
                btn.grid(row=r, column=c, padx=3, pady=3)
                row_buttons.append(btn)
            self.buttons.append(row_buttons)

        # Buttons Frame (Undo + New Game)
        btn_frame = tk.Frame(root, bg=self.BG_COLOR)
        btn_frame.pack(pady=15)

        self.undo_btn = tk.Button(btn_frame, text="↩ Undo Move", command=self.undo_move, 
                                  font=("Arial", 12, "bold"), bg="#333333", fg=self.TEXT_COLOR, 
                                  activebackground="#555555", activeforeground=self.TEXT_COLOR,
                                  width=12, relief="flat", bd=0)
        self.undo_btn.pack(side="left", padx=10)

        reset_btn = tk.Button(btn_frame, text="🔄 New Game", command=self.reset_game, 
                              font=("Arial", 12, "bold"), bg="#333333", fg=self.TEXT_COLOR, 
                              activebackground="#555555", activeforeground=self.TEXT_COLOR,
                              width=12, relief="flat", bd=0)
        reset_btn.pack(side="left", padx=10)

        self.update_board()
        self.start_timer() # Start timer on game launch

    # ==========================================
    # ⏱ TIMER METHODS
    # ==========================================
    def start_timer(self):
        self.stop_timer()
        self.time_left = self.TURN_TIME_LIMIT
        self.timer_running = True
        self.update_timer_display()

    def stop_timer(self):
        self.timer_running = False
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

    def update_timer_display(self):
        if not self.timer_running:
            return
        
        color = "#ff5252" if self.time_left <= 5 else self.TEXT_COLOR
        self.timer_label.config(text=f"⏱ Time: {self.time_left}s", fg=color)
        
        if self.time_left <= 0:
            self.skip_human_turn()
            return

        self.time_left -= 1
        self.timer_id = self.root.after(1000, self.update_timer_display)

    def skip_human_turn(self):
        self.stop_timer()
        if not self.game.is_game_over() and self.game.current_player == HUMAN:
            self.selected = None
            self.valid_moves = []
            self.status_label.config(text="Time's up! AI thinking...", fg=self.AI_COLOR)
            self.update_board()
            self.root.after(500, self.ai_turn)

    # ==========================================
    # ↩ UNDO METHODS
    # ==========================================
    def undo_move(self):
        # Can only undo if it's human turn, game isn't over, and we have a saved state
        if self.previous_game_state is None or self.game.current_player != HUMAN or self.game.is_game_over():
            return
        
        # Restore the game state
        self.game = self.previous_game_state
        self.previous_game_state = None # Clear saved state so you can't undo infinitely
        
        self.selected = None
        self.valid_moves = []
        self.status_label.config(text=f"Move Undone! Your Turn", fg=self.HUMAN_COLOR)
        self.update_board()
        self.start_timer() # Reset timer

    # ==========================================
    # GAME LOGIC METHODS
    # ==========================================
    def reset_game(self):
        self.stop_timer()
        self.game = BattleKonoGame()
        self.previous_game_state = None
        self.selected = None
        self.valid_moves = []
        self.game_over_shown = False
        self.status_label.config(text=f"Your Turn (First to {WINNING_SCORE})", fg=self.HUMAN_COLOR)
        self.update_board()
        self.start_timer()

    def update_board(self):
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.game.board[r][c]
                text = ""
                fg_color = self.TEXT_COLOR
                bg_color = self.BOARD_EMPTY
                
                if piece == HUMAN:
                    text = self.HUMAN_ICON
                    fg_color = self.HUMAN_COLOR
                    bg_color = self.BOARD_HUMAN
                elif piece == AI:
                    text = self.AI_ICON
                    fg_color = self.AI_COLOR
                    bg_color = self.BOARD_AI
                
                if self.selected == (r, c):
                    bg_color = self.COLOR_SELECTED
                    fg_color = "#000000" 
                elif (r, c) in self.valid_moves:
                    bg_color = self.COLOR_VALID
                    fg_color = "#000000" 
                
                self.buttons[r][c].config(text=text, bg=bg_color, fg=fg_color)

        self.score_label.config(text=f"Human: {self.game.human_score} | AI: {self.game.ai_score}")

        if self.game.is_game_over() and not self.game_over_shown:
            self.stop_timer() # Stop timer on game over
            self.game_over_shown = True
            winner = self.game.get_winner()
            if "70" in winner:
                msg = f"🏆 {winner} wins instantly!\nHuman: {self.game.human_score} | AI: {self.game.ai_score}"
            elif winner == "Tie":
                msg = f"It's a tie!\nHuman: {self.game.human_score} | AI: {self.game.ai_score}"
            else:
                msg = f"{winner} wins!\nHuman: {self.game.human_score} | AI: {self.game.ai_score}"
            messagebox.showinfo("Game Over", msg)

    def handle_click(self, r, c):
        if self.game.is_game_over() or self.game.current_player != HUMAN:
            return

        if self.selected is None:
            if self.game.board[r][c] == HUMAN:
                self.selected = (r, c)
                self.valid_moves = self.game.get_valid_moves(r, c)
                self.status_label.config(text=f"Selected ({r},{c}) - Choose destination")
                self.update_board()
        else:
            fr, fc = self.selected
            if (r, c) in self.valid_moves:
                # 💾 SAVE STATE FOR UNDO RIGHT BEFORE MOVING
                self.previous_game_state = copy.deepcopy(self.game)
                
                self.game.move_piece(fr, fc, r, c)
                self.selected = None
                self.valid_moves = []
                self.stop_timer() # Stop timer while AI thinks
                
                if not self.game.is_game_over():
                    self.game.current_player = AI
                    self.status_label.config(text="AI thinking...", fg=self.AI_COLOR)
                    self.update_board()
                    self.root.after(500, self.ai_turn)
                else:
                    self.update_board()
            elif (r, c) == self.selected:
                self.selected = None
                self.valid_moves = []
                self.status_label.config(text=f"Your Turn", fg=self.HUMAN_COLOR)
                self.update_board()
            elif self.game.board[r][c] == HUMAN:
                self.selected = (r, c)
                self.valid_moves = self.game.get_valid_moves(r, c)
                self.status_label.config(text=f"Selected ({r},{c}) - Choose destination")
                self.update_board()
            else:
                self.selected = None
                self.valid_moves = []
                self.status_label.config(text=f"Your Turn", fg=self.HUMAN_COLOR)
                self.update_board()

    def ai_turn(self):
        if self.game.is_game_over():
            return
            
        move = self.ai.choose_move(self.game)
        if move:
            self.game.move_piece(*move)
        
        self.game.current_player = HUMAN
        self.status_label.config(text=f"Your Turn", fg=self.HUMAN_COLOR)
        self.update_board()
        
        # Restart timer for the human player
        if not self.game.is_game_over():
            self.start_timer()


if __name__ == "__main__":
    root = tk.Tk()
    app = GameGUI(root)
    root.mainloop()