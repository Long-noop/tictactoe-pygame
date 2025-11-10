import pygame
import math
from randomAgt import RandomAgent
pygame.init()

# Screen
WIDTH = 600  # Increased to accommodate 6x6 grid
ROWS = 6
win = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("TicTacToe 6x6")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Images
X_IMAGE = pygame.transform.scale(pygame.image.load("images/x.png"), (70, 70))  # Reduced size to fit 6x6 grid
O_IMAGE = pygame.transform.scale(pygame.image.load("images/o.png"), (70, 70))  # Reduced size to fit 6x6 grid

# Fonts
END_FONT = pygame.font.SysFont('arial', 50)  # Increased font size for larger board


def draw_grid():
    gap = WIDTH // ROWS

    # Starting points
    x = 0
    y = 0

    for i in range(ROWS):
        x = i * gap

        pygame.draw.line(win, GRAY, (x, 0), (x, WIDTH), 3)
        pygame.draw.line(win, GRAY, (0, x), (WIDTH, x), 3)


def initialize_grid():
    dis_to_cen = WIDTH // ROWS // 2

    # Initializing the array
    game_array = [[None] * ROWS for _ in range(ROWS)]  # Create 6x6 array

    for i in range(len(game_array)):
        for j in range(len(game_array[i])):
            x = dis_to_cen * (2 * j + 1)
            y = dis_to_cen * (2 * i + 1)

            # Adding centre coordinates
            game_array[i][j] = (x, y, "", True)

    return game_array



def make_move(game_array, i, j, symbol):
    global x_turn, o_turn, images
    x, y, _, _ = game_array[i][j]
    
    if symbol == 'x':
        images.append((x, y, X_IMAGE))
        x_turn = False
        o_turn = True
    else:  # symbol == 'o'
        images.append((x, y, O_IMAGE))
        x_turn = True
        o_turn = False
    
    game_array[i][j] = (x, y, symbol, False)

def click(game_array):
    global x_turn, o_turn, images, random_agent

    if x_turn:  # Human's turn (X)
        # Mouse position
        m_x, m_y = pygame.mouse.get_pos()

        for i in range(len(game_array)):
            for j in range(len(game_array[i])):
                x, y, char, can_play = game_array[i][j]

                # Distance between mouse and the centre of the square
                dis = math.sqrt((x - m_x) ** 2 + (y - m_y) ** 2)

                # If it's inside the square
                if dis < WIDTH // ROWS // 2 and can_play:
                    # Make human move
                    make_move(game_array, i, j, 'x')
                    render()  # Update display to show human's move
                    pygame.display.update()
                    
                    # Check if game is over after human move
                    if not has_won(game_array) and not has_drawn(game_array):
                        # Add delay before AI moves
                        pygame.time.delay(800)  # Increased delay to 800ms
                        
                        # Make AI move
                        ai_move = random_agent.get_move(game_array)
                        if ai_move:
                            make_move(game_array, ai_move[0], ai_move[1], 'o')
                            render()  # Update display to show AI's move
                            pygame.display.update()


# Checking if someone has won
def has_won(game_array):
    # Function to check 4 in a row
    def check_sequence(chars):
        if len(chars) < 4:
            return False
        # Check for any consecutive 4 same symbols
        for i in range(len(chars) - 3):
            if chars[i] == chars[i+1] == chars[i+2] == chars[i+3] and chars[i] != "":
                return chars[i]
        return None

    # Checking rows
    for row in range(len(game_array)):
        chars = [game_array[row][j][2] for j in range(len(game_array[row]))]
        winner = check_sequence(chars)
        if winner:
            display_message(winner.upper() + " has won!")
            return True

    # Checking columns
    for col in range(len(game_array[0])):
        chars = [game_array[i][col][2] for i in range(len(game_array))]
        winner = check_sequence(chars)
        if winner:
            display_message(winner.upper() + " has won!")
            return True

    # Checking diagonals (both directions, all possible 4-in-a-row positions)
    for i in range(len(game_array) - 3):
        for j in range(len(game_array[0]) - 3):
            # Check diagonal from top-left to bottom-right
            if (game_array[i][j][2] == game_array[i+1][j+1][2] == 
                game_array[i+2][j+2][2] == game_array[i+3][j+3][2]) and game_array[i][j][2] != "":
                display_message(game_array[i][j][2].upper() + " has won!")
                return True
            
            # Check diagonal from top-right to bottom-left
            if (game_array[i][j+3][2] == game_array[i+1][j+2][2] == 
                game_array[i+2][j+1][2] == game_array[i+3][j][2]) and game_array[i][j+3][2] != "":
                display_message(game_array[i][j+3][2].upper() + " has won!")
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
    pygame.time.delay(500)
    win.fill(WHITE)
    end_text = END_FONT.render(content, 1, BLACK)
    win.blit(end_text, ((WIDTH - end_text.get_width()) // 2, (WIDTH - end_text.get_height()) // 2))
    pygame.display.update()
    pygame.time.delay(3000)


def render():
    win.fill(WHITE)
    draw_grid()

    # Drawing X's and O's
    for image in images:
        x, y, IMAGE = image
        win.blit(IMAGE, (x - IMAGE.get_width() // 2, y - IMAGE.get_height() // 2))

    pygame.display.update()


def main():
    global x_turn, o_turn, images, draw, random_agent

    images = []
    draw = False

    run = True

    x_turn = True
    o_turn = False

    # Initialize the random agent as 'o' player
    random_agent = RandomAgent('o')

    game_array = initialize_grid()

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN and x_turn:  # Only accept clicks during human's turn
                click(game_array)

        # Only render if there's no move being made
        if not (has_won(game_array) or has_drawn(game_array)):
            render()
            pygame.display.update()

        if has_won(game_array) or has_drawn(game_array):
            run = False


while True:
    if __name__ == '__main__':
        main()
