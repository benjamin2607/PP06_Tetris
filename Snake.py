import pygame
import random
import sys

# Pygame initialisieren
pygame.init()

# Fenstergröße und grundlegende Einstellungen
WIDTH = 600
HEIGHT = 400
SNAKE_SIZE = 10
SNAKE_SPEED = 15

# Fenster erstellen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Snake')

clock = pygame.time.Clock()

# Farben definieren
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Schriftart für Nachrichten
font_style = pygame.font.SysFont("bahnschrift", 25)


def message(msg, color):
    """Zeigt eine Nachricht im Fenster an."""
    mesg = font_style.render(msg, True, color)
    screen.blit(mesg, [WIDTH / 6, HEIGHT / 3])


def gameLoop():
    """Die Hauptspielschleife – steuert das gesamte Spiel."""
    game_over = False
    game_close = False

    # Startposition der Schlange (Mittel des Fensters)
    x1 = WIDTH / 2
    y1 = HEIGHT / 2

    x1_change = 0
    y1_change = 0

    # Schlange als Liste der Blöcke (jede Position ein Viereck)
    snake_List = []
    Length_of_snake = 1

    # Zufällige Position des Futters (Nahrung)
    foodx = round(random.randrange(0, WIDTH - SNAKE_SIZE) / 10.0) * 10.0
    foody = round(random.randrange(0, HEIGHT - SNAKE_SIZE) / 10.0) * 10.0

    while not game_over:

        while game_close:
            screen.fill(BLACK)
            message("Verloren! Drücke Q zum Beenden oder C zum Weiterspielen", RED)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    elif event.key == pygame.K_c:
                        gameLoop()  # Starte ein neues Spiel

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x1_change = -SNAKE_SIZE
                    y1_change = 0
                elif event.key == pygame.K_RIGHT:
                    x1_change = SNAKE_SIZE
                    y1_change = 0
                elif event.key == pygame.K_UP:
                    y1_change = -SNAKE_SIZE
                    x1_change = 0
                elif event.key == pygame.K_DOWN:
                    y1_change = SNAKE_SIZE
                    x1_change = 0

        # Überprüfe, ob die Schlange den Rand berührt hat
        if x1 >= WIDTH or x1 < 0 or y1 >= HEIGHT or y1 < 0:
            game_close = True

        # Aktualisiere die Schlange-Position
        x1 += x1_change
        y1 += y1_change
        screen.fill(BLACK)
        pygame.draw.rect(screen, GREEN, [foodx, foody, SNAKE_SIZE, SNAKE_SIZE])

        snake_Head = []
        snake_Head.append(x1)
        snake_Head.append(y1)
        snake_List.append(snake_Head)
        if len(snake_List) > Length_of_snake:
            del snake_List[0]

        # Kollision mit sich selber
        for x in snake_List[:-1]:
            if x == snake_Head:
                game_close = True

        # Schlangen zeichnen
        for block in snake_List:
            pygame.draw.rect(screen, WHITE, [block[0], block[1], SNAKE_SIZE, SNAKE_SIZE])

        pygame.display.update()

        # Nahrung "essen": Wenn der Kopf die Nahrung erreicht
        if x1 == foodx and y1 == foody:
            foodx = round(random.randrange(0, WIDTH - SNAKE_SIZE) / 10.0) * 10.0
            foody = round(random.randrange(0, HEIGHT - SNAKE_SIZE) / 10.0) * 10.0
            Length_of_snake += 1

        clock.tick(SNAKE_SPEED)

    pygame.quit()
    sys.exit()


# Spiel starten
if __name__ == "__main__":
    gameLoop()
