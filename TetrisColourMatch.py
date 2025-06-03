import pygame
import random
from enum import Enum

# Globale Definitionen
background = 'Black'
Input = Enum('Input', ['Left', 'Right', 'RotateLeft', 'RotateRight', 'Fall'])


class MehrsteinTetris:
    def __init__(self, columns=20, rows=30):
        self.columns = columns
        self.rows = rows
        # Erstelle das Raster (Grid) als Liste von Zeilen, die mit der Hintergrundfarbe gefüllt sind.
        self.grid = [[background for _ in range(columns)] for _ in range(rows)]
        # Definiere eine Liste möglicher Farben für die Tetris-Teile.
        self.colors = ["Purple", "Cyan", "White"]
        ## "Yellow", "Magenta", "Cyan", "Orange, "Red", "Green","Blue""
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
            if x < 0 or x >= self.columns or y >= self.rows or self.grid[y][x] != background:
                can_move = False
                break
        if can_move:
            self._current = new_coords
        else:
            # "Einfrieren" des Teils ins Raster mit der aktuellen Farbe
            for (x, y) in self._current:
                if 0 <= x < self.columns and 0 <= y < self.rows:
                    self.grid[y][x] = self.current_color

            # Add this line to check and remove connected pieces
            self.remove_connected_lines()

            # Erzeuge ein neues Teil mit zufälliger Farbe.
            self._current = self.get_new_piece()
        return self

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

    def find_connected_blocks(self, grid, color, start_x, start_y, visited):
        """Helper function to find all connected blocks of the same color using DFS."""
        if (start_x < 0 or start_x >= self.columns or 
            start_y < 0 or start_y >= self.rows or 
            (start_x, start_y) in visited or 
            grid[start_y][start_x] != color):
            return set()
        
        visited.add((start_x, start_y))
        connected = {(start_x, start_y)}
        
        # Check all 4 directions
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dx, dy in directions:
            new_x, new_y = start_x + dx, start_y + dy
            connected.update(self.find_connected_blocks(grid, color, new_x, new_y, visited))
        
        return connected

    def spans_width(self, blocks):
        """
        Check if the blocks span the entire width of the game field.
        Returns True if for each column there is at least one block.
        """
        columns_covered = set()
        for x, _ in blocks:
            columns_covered.add(x)
        return len(columns_covered) == self.columns

    def remove_connected_lines(self):
        """Find and remove connected blocks of the same color that span the width."""
        visited = set()
        all_blocks_to_remove = set()
        
        # Find all connected components
        for y in range(self.rows):
            for x in range(self.columns):
                if (x, y) not in visited and self.grid[y][x] != background:
                    connected = self.find_connected_blocks(self.grid, self.grid[y][x], x, y, visited)
                    if self.spans_width(connected):
                        all_blocks_to_remove.update(connected)
        
        # If we found blocks to remove
        if all_blocks_to_remove:
            # Remove the blocks
            for x, y in all_blocks_to_remove:
                self.grid[y][x] = background
        
            # Let blocks above fall down
            for col in range(self.columns):
                # Create a temporary column to store non-removed blocks
                temp_column = []
            
                # Collect all non-removed blocks in this column from bottom to top
                for row in range(self.rows - 1, -1, -1):
                    if (col, row) not in all_blocks_to_remove and self.grid[row][col] != background:
                        temp_column.append(self.grid[row][col])
            
                # Fill the column from bottom to top
                row = self.rows - 1
                # Place collected blocks
                for color in temp_column:
                    self.grid[row][col] = color
                    row -= 1
                # Fill remaining spaces with background
                while row >= 0:
                    self.grid[row][col] = background
                    row -= 1

            return True
        return False


def playTetris(tetris, block_size=30, fps=60, drop_speed=1.0):
    pygame.init()
    width = tetris.columns * block_size
    height = tetris.rows * block_size
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()

    # Initialize font for pause menu
    font = pygame.font.Font(None, 74)

    # Timing controls
    drop_interval = 1000 / drop_speed
    last_drop_time = pygame.time.get_ticks()
    
    # Fast fall settings
    fast_fall_interval = 50  # Time between fast falls in milliseconds
    last_fast_fall_time = 0
    
    # Movement delay controls
    move_delay = 100
    rotate_delay = 150
    last_move_time = {
        'left': 0,
        'right': 0,
        'rotate_left': 0,
        'rotate_right': 0
    }

    # Pause state
    paused = False
    pause_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    pause_surface.fill((0, 0, 0, 128))  # Semi-transparent black
    pause_text = font.render("PAUSED", True, (255, 255, 255))
    pause_rect = pause_text.get_rect(center=(width // 2, height // 2))

    running = True
    while running:
        clock.tick(fps)
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = not paused

        if not paused:
            # Handle keyboard input with delays
            keys = pygame.key.get_pressed()
            
            if keys[pygame.K_LEFT] and current_time - last_move_time['left'] >= move_delay:
                tetris.prInput(Input.Left)
                last_move_time['left'] = current_time
                
            if keys[pygame.K_RIGHT] and current_time - last_move_time['right'] >= move_delay:
                tetris.prInput(Input.Right)
                last_move_time['right'] = current_time
                
            if keys[pygame.K_UP] and current_time - last_move_time['rotate_left'] >= rotate_delay:
                tetris.prInput(Input.RotateLeft)
                last_move_time['rotate_left'] = current_time
                
            if keys[pygame.K_DOWN] and current_time - last_move_time['rotate_right'] >= rotate_delay:
                tetris.prInput(Input.RotateRight)
                last_move_time['rotate_right'] = current_time
            
            # Handle fast fall (space) with time-based movement
            if keys[pygame.K_SPACE] and current_time - last_fast_fall_time >= fast_fall_interval:
                tetris.prInput(Input.Fall)
                last_fast_fall_time = current_time

            # Normal drop timing
            if current_time - last_drop_time >= drop_interval:
                tetris.move()
                last_drop_time = current_time

        # Render game
        screen.fill(background)
        
        # Draw fixed blocks
        for row in range(tetris.rows):
            for col in range(tetris.columns):
                color = tetris.grid[row][col]
                if color != background:
                    rect = (col * block_size, row * block_size, block_size, block_size)
                    pygame.draw.rect(screen, color, rect)
                    pygame.draw.rect(screen, "Black", rect, 1)
                    
        # Draw current piece
        for (col, row) in tetris.current():
            rect = (col * block_size, row * block_size, block_size, block_size)
            pygame.draw.rect(screen, tetris.current_color, rect)
            pygame.draw.rect(screen, "Black", rect, 1)

        # Draw pause menu if game is paused
        if paused:
            screen.blit(pause_surface, (0, 0))
            screen.blit(pause_text, pause_rect)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    game = MehrsteinTetris(columns=20, rows=40)
    playTetris(game, 
               block_size=30,
               fps=60,
               drop_speed=10
    )