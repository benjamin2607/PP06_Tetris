import pygame
import random
from enum import Enum
from collections import deque

# Globale Definitionen
background = 'Black'
Input = Enum('Input', ['Left', 'Right', 'RotateLeft', 'RotateRight', 'Fall'])


class MehrsteinTetris:
    def __init__(self, columns=20, rows=30):
        self.columns = columns
        self.rows = rows
        self.score = 0
        # Erstelle das Raster (Grid) als Liste von Zeilen, die mit der Hintergrundfarbe gefüllt sind.
        self.grid = [[background for _ in range(columns)] for _ in range(rows)]
        # Definiere eine Liste möglicher Farben für die Tetris-Teile.
        self.colors = ["Red", "Green", "Blue"]
        # Setze current_color beim Start fest
        self.current_color = random.choice(self.colors)
        # Initial wird ein Standard-Teil, hier ein I-Teil, in der Mitte des Spielfelds erzeugt.
        self._current = [(columns // 2 - 2, 0),
                         (columns // 2 - 1, 0),
                         (columns // 2, 0),
                         (columns // 2 + 1, 0)]

    def current(self):
        """Gibt die aktuellen Koordinaten des fallenden Teils zurück."""
        return self._current

    def ended(self):
        """
        Das Spiel ist beendet, wenn in der obersten Zeile eine
        Zelle nicht mehr der Hintergrundfarbe entspricht.
        """
        row_zero = [cell for cell in self.grid[0] if cell != background]
        return len(row_zero) != 0

    def get_new_piece(self):
        """
        Erzeugt ein neues Tetris-Teil aus einer festgelegten Auswahl an Formen.
        Die Formen werden als Liste relativer Koordinaten definiert.
        Anschließend wird ein horizontaler Offset berechnet, sodass das Teil
        innerhalb der Spielfeldgrenzen platziert werden kann.
        """
        shapes = [
            [(0, 0), (1, 0), (2, 0), (3, 0)],  # I-Form
            [(0, 0), (0, 1), (1, 0), (1, 1)],  # O-Form
            [(1, 0), (0, 1), (1, 1), (2, 1)],  # T-Form
            [(1, 0), (2, 0), (0, 1), (1, 1)],  # S-Form
            [(0, 0), (1, 0), (1, 1), (2, 1)],  # Z-Form
            [(0, 0), (0, 1), (1, 1), (2, 1)],  # J-Form
            [(2, 0), (0, 1), (1, 1), (2, 1)]  # L-Form
        ]
        shape = random.choice(shapes)
        # Bestimme den horizontalen Offset, damit das neue Teil in das Spielfeld passt.
        xs = [x for (x, y) in shape]
        min_x = min(xs)
        max_x = max(xs)
        offset_min = -min_x
        offset_max = self.columns - 1 - max_x
        offset = random.randint(offset_min, offset_max) if offset_max >= offset_min else offset_min
        new_piece = [(x + offset, y) for (x, y) in shape]
        # Weise dem neuen Teil eine zufällige Farbe zu.
        self.current_color = random.choice(self.colors)
        return new_piece

    def move(self):
        new_coords = [(x, y + 1) for (x, y) in self._current]
        can_move = True
        for (x, y) in new_coords:
            if y >= self.rows or self.grid[y][x] != background:
                can_move = False
                break
        if can_move:
            self._current = new_coords
        else:
            # Einfrieren des Teils
            for (x, y) in self._current:
                if 0 <= x < self.columns and 0 <= y < self.rows:
                    self.grid[y][x] = self.current_color

            # Sobald ein Block platziert ist, wird für jede Farbe geprüft,
            # ob es eine durchgehende Fläche gibt und die Blöcke dieser Farbe entfernt.
            for color in self.colors:
                self.remove_connected_color_if_path_exists(color)

            self.score += 10 # +10 Punkte für das Platzieren von Blöcken

            # Neues Teil generieren
            self._current = self.get_new_piece()
        return self

    def remove_connected_color_if_path_exists(self, color):
        """
        Überprüft, ob es eine zusammenhängende Fläche von Blöcken der übergebenen Farbe gibt,
        die vom linken bis zum rechten Spielfeldrand reicht.

        Falls ja, werden **alle zusammenhängenden Blöcke dieser Farbe**, nicht nur der direkte
        Verbindungspfad, vom Spielfeld entfernt.
        """
        visited = set()  # Set für bereits besuchte Zellen aus allen Aufrufen

        def dfs(x, y):
            """
            Rekursive Tiefensuche ab gegebener Position. Fügt alle zusammenhängenden Blöcke
            gleicher Farbe zu 'visited' hinzu.

            Args:
                x (int): Spalte
                y (int): Zeile
            """
            if (x, y) in visited:
                return
            if not (0 <= x < self.columns and 0 <= y < self.rows):
                return
            if self.grid[y][x] != color:
                return

            visited.add((x, y))

            # Suche in alle 4 Richtungen weiter
            dfs(x + 1, y)
            dfs(x - 1, y)
            dfs(x, y + 1)
            dfs(x, y - 1)

        # Finde alle Farbinseln der gewünschten Farbe, die am linken Rand starten
        for y in range(self.rows):
            if self.grid[y][0] == color and (0, y) not in visited:
                component = set()

                # speichert den Zustand von visited, bevor er für eine neue Startzelle am linken Rand aufgerufen wird
                visited_before = visited.copy()

                # dfs wird von der nächsten Zelle aus aufgerufen
                dfs(0, y)

                # component ist der neu hinzugekommene Bereich, mit dem neusten Aufruf
                # wird verwendet, um zu prüfen, ob die aktuelle Farbinsel die rechte Seite erreicht.
                component = visited - visited_before

                # Prüfen, ob eine Zelle in diesem Cluster die rechte Seite berührt
                reaches_right = any(x == self.columns - 1 for (x, _) in component)
                if reaches_right:
                    # Entferne alle Blöcke dieser Farb-Insel
                    for (x, y) in component:
                        self.grid[y][x] = background

                    # Punktevergabe je Block (optional einstellbar)
                    self.score += len(component) * 50
                    return True  # Pfad erfolgreich entfernt

        return False  # Kein vollständiger Pfad gefunden

    def prInput(self, input):
        """
        Verarbeitet die Tastatureingabe.
         - Mit Input.Left und Input.Right werden alle Blöcke des aktuellen Teils lateral verschoben, falls das Ziel frei ist.
         - Mit Input.RotateLeft bzw. Input.RotateRight wird das Teil um einen Pivotpunkt (den ersten Block) gedreht.
         - Mit Input.Fall wird das Teil beschleunigt (Soft Drop) nach unten bewegt,
           indem pro Eingabe mehrere Schritte ausgeführt werden, ohne sofort alle Zeilen zu überspringen.
        """
        if input == Input.Left:
            proposed = [(x - 1, y) for (x, y) in self._current]
            if all(0 <= x < self.columns and self.grid[y][x] == background for (x, y) in proposed):
                self._current = proposed

        elif input == Input.Right:
            proposed = [(x + 1, y) for (x, y) in self._current]
            if all(0 <= x < self.columns and self.grid[y][x] == background for (x, y) in proposed):
                self._current = proposed

        elif input == Input.RotateLeft:
            # Drehung gegen den Uhrzeigersinn; benutze den ersten Block als Drehpunkt.
            pivot = self._current[0]
            new_coords = []
            for (x, y) in self._current:
                new_x = pivot[0] - (y - pivot[1])
                new_y = pivot[1] + (x - pivot[0])
                new_coords.append((new_x, new_y))
            if all(0 <= new_x < self.columns and 0 <= new_y < self.rows and self.grid[new_y][new_x] == background
                   for (new_x, new_y) in new_coords):
                self._current = new_coords

        elif input == Input.RotateRight:
            # Drehung im Uhrzeigersinn; benutzte ebenfalls den ersten Block als Drehpunkt.
            pivot = self._current[0]
            new_coords = []
            for (x, y) in self._current:
                new_x = pivot[0] + (y - pivot[1])
                new_y = pivot[1] - (x - pivot[0])
                new_coords.append((new_x, new_y))
            if all(0 <= new_x < self.columns and 0 <= new_y < self.rows and self.grid[new_y][new_x] == background
                   for (new_x, new_y) in new_coords):
                self._current = new_coords

        elif input == Input.Fall:
            # Hier wird jetzt schrittweise gedroppt und nicht mehr instant nach unten gewarped.
            steps = 3  # Anzahl der Schritte pro Frame bei gedrückter Leertaste
            for _ in range(steps):
                proposed = [(x, y + 1) for (x, y) in self._current]
                if all((y + 1) < self.rows and self.grid[y + 1][x] == background for (x, y) in self._current):
                    self._current = proposed
                else:
                    # Kann der Block nicht weiterfallen, wird er eingefroren.
                    self.move()
                    break
        return self


def playTetris(tetris, block_size=30, fps=60):
    """
    Diese Funktion initialisiert Pygame, erstellt ein Fenster entsprechend der
    Spielfeldgröße von Tetris und startet die Hauptspielschleife.
    """
    pygame.init()
    width = tetris.columns * block_size
    height = tetris.rows * block_size
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()

    # Define fail line at 80% from the top
    fail_line_y = int(tetris.rows * 0.2)

    # Initialize fonts
    large_font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 36)
    score_font = pygame.font.Font(None, 40)

    # Game timing
    drop_time = 0
    drop_interval = 200  # milliseconds

    # Game state variables
    game_over = False
    paused = False

    # Create overlays
    pause_overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    pause_overlay.fill((0, 0, 0, 128))
    game_over_overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    game_over_overlay.fill((0, 0, 0, 192))

    running = True
    while running:
        dt = clock.tick(fps)
        drop_time += dt

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and not game_over:
                    paused = not paused
                if event.key == pygame.K_q:
                    if paused or game_over:
                        running = False
                if event.key == pygame.K_e and game_over:
                    tetris = MehrsteinTetris(columns=tetris.columns, rows=tetris.rows)
                    game_over = False

        # Checks if Game is paused
        if not paused and not game_over:
            # Handle input
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                tetris.prInput(Input.Left)
            if keys[pygame.K_RIGHT]:
                tetris.prInput(Input.Right)
            if keys[pygame.K_UP]:
                tetris.prInput(Input.RotateLeft)
            if keys[pygame.K_DOWN]:
                tetris.prInput(Input.RotateRight)
            if keys[pygame.K_SPACE]:
                tetris.prInput(Input.Fall)

            # Automatic drop
            if drop_time >= drop_interval:
                tetris.move()
                drop_time = 0

            # Check game over
            for x in range(tetris.columns):
                if tetris.grid[fail_line_y][x] != background:
                    game_over = True
                    break

        # Rendering
        screen.fill(background)

        # Draw fail line
        pygame.draw.line(screen, "Red",
                         (0, fail_line_y * block_size),
                         (width, fail_line_y * block_size),
                         3)

        # Draw fixed blocks
        for row in range(tetris.rows):
            for col in range(tetris.columns):
                color = tetris.grid[row][col]
                if color != background:
                    rect = (col * block_size, row * block_size, block_size, block_size)
                    pygame.draw.rect(screen, color, rect)
                    pygame.draw.rect(screen, "Black", rect, 1)

        # Draw current piece
        if not game_over:
            for (col, row) in tetris.current():
                rect = (col * block_size, row * block_size, block_size, block_size)
                pygame.draw.rect(screen, tetris.current_color, rect)
                pygame.draw.rect(screen, "Black", rect, 1)

        # Draw score (always visible)
        score_text = score_font.render(f'Score: {tetris.score}', True, 'White')
        score_rect = score_text.get_rect(topleft=(10, 10))
        screen.blit(score_text, score_rect)

        # Draw pause screen
        if paused and not game_over:
            screen.blit(pause_overlay, (0, 0))
            pause_text = large_font.render("PAUSED", True, 'White')
            pause_rect = pause_text.get_rect(center=(width // 2, height // 2 - 25))
            screen.blit(pause_text, pause_rect)

            pause_continue = small_font.render("Press ESC to continue", True, 'White')
            pause_continue_rect = pause_continue.get_rect(center=(width // 2, height // 2 + 25))
            screen.blit(pause_continue, pause_continue_rect)

            pause_quit = small_font.render("Press Q to quit", True, 'White')
            pause_quit_rect = pause_quit.get_rect(center=(width // 2, height // 2 + 60))
            screen.blit(pause_quit, pause_quit_rect)

        # Draw game over screen
        if game_over:
            screen.blit(game_over_overlay, (0, 0))
            game_over_text = large_font.render('GAME OVER', True, 'White')
            game_over_rect = game_over_text.get_rect(center=(width // 2, height // 2 - 25))
            screen.blit(game_over_text, game_over_rect)

            final_score = score_font.render(f'Final Score: {tetris.score}', True, 'White')
            final_score_rect = final_score.get_rect(center=(width // 2, height // 2 + 25))
            screen.blit(final_score, final_score_rect)

            continue_text = small_font.render('Press Q to quit or E to play again', True, 'White')
            continue_rect = continue_text.get_rect(center=(width // 2, height // 2 + 75))
            screen.blit(continue_text, continue_rect)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    # Erzeuge eine neue Tetris-Partie und starte die Spielschleife.
    game = MehrsteinTetris(columns=20, rows=30)
    playTetris(game, block_size=30, fps=10)