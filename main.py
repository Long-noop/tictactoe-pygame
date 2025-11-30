import pygame
import math
from agent.minimaxAgt import MinimaxAgent
from agent.randomAgt import RandomAgent
import datetime

pygame.init()

# Screen
WIDTH = 540
ROWS = 9
MENU_HEIGHT = 80
win = pygame.display.set_mode((WIDTH, WIDTH + MENU_HEIGHT))
pygame.display.set_caption("TicTacToe 9x9")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 200, 0)
LIGHT_BLUE = (173, 216, 230)
DARK_GRAY = (100, 100, 100)

# Images
# Images
X_IMAGE = pygame.transform.scale(pygame.image.load("images/x.png"), (36, 36))
O_IMAGE = pygame.transform.scale(pygame.image.load("images/o.png"), (36, 36))

# Fonts
END_FONT = pygame.font.SysFont('arial', 24)
MENU_FONT = pygame.font.SysFont('arial', 18)
INFO_FONT = pygame.font.SysFont('arial', 14)

# Game states
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"

# Global variables
current_state = STATE_MENU
selected_opponent = None
current_step = 0


class Button:
    def __init__(self, x, y, width, height, text, color, text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.hover = False

    def draw(self, surface):
        color = self.color if not self.hover else tuple(min(c + 30, 255) for c in self.color)
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)
        
        text_surface = MENU_FONT.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def check_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)


def draw_menu():
    """Vẽ menu chọn đối thủ"""
    win.fill(WHITE)
    
    # Title
    title_text = END_FONT.render("TIC-TAC-TOE 9x9", True, BLACK)
    win.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))
    
    subtitle_text = MENU_FONT.render("Choose Your Opponent", True, DARK_GRAY)
    win.blit(subtitle_text, (WIDTH // 2 - subtitle_text.get_width() // 2, 120))
    
    # Buttons (smaller layout for reduced window)
    button_width = 160
    button_height = 48
    button_spacing = 64
    start_y = 160
    
    buttons = {
        'random': Button(WIDTH // 2 - button_width // 2, start_y, 
                        button_width, button_height, "Random Agent", BLUE),
        'minimax': Button(WIDTH // 2 - button_width // 2, start_y + button_spacing, 
                         button_width, button_height, "Minimax Agent", RED),
        'ml': Button(WIDTH // 2 - button_width // 2, start_y + button_spacing * 2, 
                    button_width, button_height, "ML Agent (Coming)", DARK_GRAY)
    }
    
    for i, (key, button) in enumerate(buttons.items()):
        button.draw(win)
    
    pygame.display.update()
    return buttons


def draw_grid():
    gap = WIDTH // ROWS
    x = 0
    y = 0

    for i in range(ROWS):
        x = i * gap
        pygame.draw.line(win, GRAY, (x, 0), (x, WIDTH), 2)
        pygame.draw.line(win, GRAY, (0, x), (WIDTH, x), 2)


def draw_status_bar(game_array):
    """Vẽ thanh trạng thái hiển thị thông tin game"""
    status_y = WIDTH
    pygame.draw.rect(win, LIGHT_BLUE, (0, status_y, WIDTH, MENU_HEIGHT))
    pygame.draw.line(win, BLACK, (0, status_y), (WIDTH, status_y), 2)
    
    # Current step
    step_text = INFO_FONT.render(f"Step: {current_step}", True, BLACK)
    win.blit(step_text, (20, status_y + 15))
    
    # Current turn
    turn_text = INFO_FONT.render(f"Turn: {'X (You)' if x_turn else 'O (AI)'}", 
                                 True, BLACK)
    win.blit(turn_text, (20, status_y + 45))
    
    # Opponent type
    opponent_name = {
        'random': 'Random Agent',
        'minimax': 'Minimax Agent',
        'ml': 'ML Agent'
    }.get(selected_opponent, 'Unknown')
    
    opponent_text = INFO_FONT.render(f"Opponent: {opponent_name}", True, BLACK)
    win.blit(opponent_text, (250, status_y + 15))
    
    # Restart button
    restart_button.draw(win)
    
    # Stats
    filled_cells = sum(1 for row in game_array for cell in row if cell[2] != "")
    stats_text = INFO_FONT.render(f"Moves: {filled_cells}/81", True, BLACK)
    win.blit(stats_text, (250, status_y + 45))


def initialize_grid():
    gap = WIDTH // ROWS  # Kích thước mỗi ô
    game_array = [[None] * ROWS for _ in range(ROWS)]

    for i in range(ROWS):
        for j in range(ROWS):
            # Tính tọa độ trung tâm của mỗi ô
            x = j * gap + gap // 2
            y = i * gap + gap // 2
            game_array[i][j] = (x, y, "", True)

    return game_array


def make_move(game_array, i, j, symbol):
    global x_turn, o_turn, images, current_step
    x, y, _, _ = game_array[i][j]
    
    if symbol == 'x':
        images.append((x, y, X_IMAGE))
        x_turn = False
        o_turn = True
    else:
        images.append((x, y, O_IMAGE))
        x_turn = True
        o_turn = False
    
    game_array[i][j] = (x, y, symbol, False)
    current_step += 1
    
    # Log the move
    try:
        with open('game_log.txt', 'a', encoding='utf-8') as f:
            f.write(f"{datetime.datetime.now().isoformat()} - Step {current_step} - {symbol.upper()} -> ({i},{j})\n")
    except Exception:
        pass
    
    try:
        print(f"Step {current_step}: {symbol.upper()} -> ({i},{j})")
    except Exception:
        pass


def click(game_array):
    global x_turn, o_turn, images, ai_agent

    if x_turn:  # Human's turn (X)
        m_x, m_y = pygame.mouse.get_pos()
        
        # Check if click is on game board (not status bar)
        if m_y >= WIDTH:
            return

        for i in range(len(game_array)):
            for j in range(len(game_array[i])):
                x, y, char, can_play = game_array[i][j]
                dis = math.sqrt((x - m_x) ** 2 + (y - m_y) ** 2)

                if dis < WIDTH // ROWS // 2 and can_play:
                    make_move(game_array, i, j, 'x')
                    render(game_array)
                    pygame.display.update()
                    
                    if not has_won(game_array) and not has_drawn(game_array):
                        pygame.time.delay(500)
                        
                        # Make AI move
                        ai_move = ai_agent.get_move(game_array)
                        if ai_move:
                            make_move(game_array, ai_move[0], ai_move[1], 'o')
                            render(game_array)
                            pygame.display.update()
                    return


def has_won(game_array):
    def check_sequence(chars):
        if len(chars) < 5:
            return None
        for idx in range(len(chars) - 4):
            if chars[idx] == chars[idx+1] == chars[idx+2] == chars[idx+3] == chars[idx+4] and chars[idx] != "":
                return (chars[idx], idx)
        return None

    def highlight_win_cells(centers):
        win.fill(WHITE)
        draw_grid()
        gap = WIDTH // ROWS
        pad = max(4, gap // 12)
        highlight_color = (255, 180, 180)

        for (cx, cy) in centers:
            rect = pygame.Rect(cx - gap // 2 + pad, cy - gap // 2 + pad, gap - 2 * pad, gap - 2 * pad)
            pygame.draw.rect(win, highlight_color, rect, border_radius=6)

        for image in images:
            ix, iy, IMAGE = image
            win.blit(IMAGE, (ix - IMAGE.get_width() // 2, iy - IMAGE.get_height() // 2))
        
        draw_status_bar(game_array)
        pygame.display.update()
        pygame.time.delay(800)

    # Checking rows
    for row in range(len(game_array)):
        chars = [game_array[row][j][2] for j in range(len(game_array[row]))]
        res = check_sequence(chars)
        if res:
            winner, start = res
            centers = [(game_array[row][j][0], game_array[row][j][1]) for j in range(start, start+5)]
            highlight_win_cells(centers)
            display_message(winner.upper() + " has won!")
            return True

    # Checking columns
    for col in range(len(game_array[0])):
        chars = [game_array[i][col][2] for i in range(len(game_array))]
        res = check_sequence(chars)
        if res:
            winner, start = res
            centers = [(game_array[i][col][0], game_array[i][col][1]) for i in range(start, start+5)]
            highlight_win_cells(centers)
            display_message(winner.upper() + " has won!")
            return True

    # Checking diagonals
    n = len(game_array)
    for i in range(n - 4):
        for j in range(n - 4):
            if (game_array[i][j][2] == game_array[i+1][j+1][2] == 
                game_array[i+2][j+2][2] == game_array[i+3][j+3][2] == game_array[i+4][j+4][2]) and game_array[i][j][2] != "":
                centers = [(game_array[i+k][j+k][0], game_array[i+k][j+k][1]) for k in range(5)]
                highlight_win_cells(centers)
                display_message(game_array[i][j][2].upper() + " has won!")
                return True

            if (game_array[i][j+4][2] == game_array[i+1][j+3][2] == 
                game_array[i+2][j+2][2] == game_array[i+3][j+1][2] == game_array[i+4][j][2]) and game_array[i][j+4][2] != "":
                centers = [(game_array[i+k][j+4-k][0], game_array[i+k][j+4-k][1]) for k in range(5)]
                highlight_win_cells(centers)
                display_message(game_array[i][j+4][2].upper() + " has won!")
                return True

    return False


def has_drawn(game_array):
    for i in range(len(game_array)):
        for j in range(len(game_array[i])):
            if game_array[i][j][2] == "":
                return False

    display_message("It's a draw!")
    return True


def display_message(content):
    global current_state
    try:
        print(content)
    except Exception:
        pass
    
    pygame.time.delay(500)
    
    # Draw semi-transparent overlay
    overlay = pygame.Surface((WIDTH, WIDTH + MENU_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill(WHITE)
    win.blit(overlay, (0, 0))
    
    # Draw message
    end_text = END_FONT.render(content, 1, BLACK)
    win.blit(end_text, ((WIDTH - end_text.get_width()) // 2, (WIDTH - end_text.get_height()) // 2 - 50))
    
    # Draw restart button
    restart_msg = MENU_FONT.render("Click 'Restart' to play again", 1, DARK_GRAY)
    win.blit(restart_msg, ((WIDTH - restart_msg.get_width()) // 2, (WIDTH - restart_msg.get_height()) // 2 + 20))
    
    pygame.display.update()
    current_state = STATE_GAME_OVER


def render(game_array):
    win.fill(WHITE)
    draw_grid()

    for image in images:
        x, y, IMAGE = image
        win.blit(IMAGE, (x - IMAGE.get_width() // 2, y - IMAGE.get_height() // 2))

    draw_status_bar(game_array)
    pygame.display.update()


def reset_game():
    global images, x_turn, o_turn, current_state, current_step
    images = []
    x_turn = True
    o_turn = False
    current_step = 0
    current_state = STATE_MENU


def main():
    global x_turn, o_turn, images, draw, ai_agent, selected_opponent, current_state, restart_button, current_step

    images = []
    draw = False
    run = True
    x_turn = True
    o_turn = False
    current_step = 0
    
    # Create restart button (will be positioned in status bar)
    # adjust restart button to fit smaller status bar
    restart_button = Button(WIDTH - 130, WIDTH + 10, 110, 40, "Restart", RED)

    game_array = None
    menu_buttons = None

    while run:
        if current_state == STATE_MENU:
            menu_buttons = draw_menu()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    
                if event.type == pygame.MOUSEMOTION:
                    for button in menu_buttons.values():
                        button.check_hover(event.pos)
                    draw_menu()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    
                    if menu_buttons['random'].is_clicked(pos):
                        selected_opponent = 'random'
                        ai_agent = RandomAgent('o')
                        current_state = STATE_PLAYING
                        game_array = initialize_grid()
                        print(f"Game started: Human (X) vs Random Agent (O)")
                        
                    elif menu_buttons['minimax'].is_clicked(pos):
                        selected_opponent = 'minimax'
                        ai_agent = MinimaxAgent('o')
                        current_state = STATE_PLAYING
                        game_array = initialize_grid()
                        print(f"Game started: Human (X) vs Minimax Agent (O)")
                        
                    elif menu_buttons['ml'].is_clicked(pos):
                        # ML Agent coming soon
                        print("ML Agent is not implemented yet!")

        elif current_state == STATE_PLAYING:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    
                    # Check restart button
                    if restart_button.is_clicked(pos):
                        reset_game()
                        continue
                    
                    # Handle game click
                    if x_turn:
                        click(game_array)
                
                if event.type == pygame.MOUSEMOTION:
                    restart_button.check_hover(event.pos)

            if not (has_won(game_array) or has_drawn(game_array)):
                render(game_array)
            else:
                current_state = STATE_GAME_OVER

        elif current_state == STATE_GAME_OVER:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if restart_button.is_clicked(pos):
                        reset_game()
                
                if event.type == pygame.MOUSEMOTION:
                    restart_button.check_hover(event.pos)
            
            render(game_array)

    pygame.quit()


if __name__ == '__main__':
    main()