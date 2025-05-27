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
            [(2, 0), (0, 1), (1, 1), (2, 1)]   # L-Form
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
        return new_piece

    def move(self):
        """
        Bewegt das aktuelle fallende Teil eine Zeile nach unten,
        sofern alle Felder direkt unter dem Teil frei und innerhalb
        des Spielfelds liegen.

        Falls mindestens ein Block nicht weiter nach unten bewegt
        werden kann, wird das Teil "eingefroren":
         - Die Zellen des Teils werden im Raster mit einer festen Farbe (hier "Red") markiert.
         - Voll belegte Zeilen werden erkannt und entfernt (neue leere Zeilen werden oben eingefügt).
         - Anschließend wird ein neues fallendes Teil mittels get_new_piece() erzeugt.
        """
        new_coords = [(x, y + 1) for (x, y) in self._current]
        can_move = True
        for (x, y) in new_coords:
            if y >= self.rows or self.grid[y][x] != background:
                can_move = False
                break
        if can_move:
            self._current = new_coords
        else:
            # "Einfrieren" des Teils ins Raster
            for (x, y) in self._current:
                if 0 <= x < self.columns and 0 <= y < self.rows:
                    self.grid[y][x] = "Red"
            # Entferne volle Zeilen (Zeilen, die nicht mehr die Hintergrundfarbe enthalten)
            notFull = [row for row in self.grid if any(cell == background for cell in row)]
            missing_rows = self.rows - len(notFull)
            new_rows = [[background for _ in range(self.columns)] for _ in range(missing_rows)]
            self.grid = new_rows + notFull
            # Erzeuge ein neues Teil
            self._current = self.get_new_piece()
        return self

    def prInput(self, input):
        """
        Verarbeitet die Tastatureingabe.
         - Mit Input.Left und Input.Right werden alle Blöcke des
           aktuellen Teils lateral verschoben, falls das Ziel frei ist.
         - Mit Input.RotateLeft bzw. Input.RotateRight wird das
           Teil um einen Pivotpunkt (dem ersten Block) gedreht.
         - Mit Input.Fall wird das Teil sofort (Hard Drop) nach unten bewegt.
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
            # Beim Hard Drop wird das Teil so weit nach unten bewegt, bis es nicht mehr möglich ist.
            while True:
                proposed = [(x, y + 1) for (x, y) in self._current]
                if all((y + 1) < self.rows and self.grid[y + 1][x] == background for (x, y) in self._current):
                    self._current = proposed
                else:
                    break
            # Anschließend wird das Teil dauerhaft eingefroren.
            self.move()
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

    # Für einen automatischen Drop des fallenden Teils alle 500 ms (z.B.)
    drop_time = 0
    drop_interval = 200  # Millisekunden

    running = True
    while running:
        dt = clock.tick(fps)  # dt ist die verstrichene Zeit in Millisekunden seit dem letzten Frame
        drop_time += dt

        # Ereignisse abarbeiten (z.B. Schließen des Fensters)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Tastatureingaben abfragen und an das Spiel weiterleiten
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

        # Automatischer Drop: Nach Ablauf des Intervalls wird das Teil eine Zeile nach unten bewegt.
        if drop_time >= drop_interval:
            tetris.move()
            drop_time = 0

        # Zeichnen des Spielfelds
        screen.fill(background)
        # Bereits festgesetzte Blöcke im Raster malen
        for row in range(tetris.rows):
            for col in range(tetris.columns):
                color = tetris.grid[row][col]
                if color != background:
                    pygame.draw.rect(screen, color,
                                     (col * block_size, row * block_size, block_size, block_size))
        # Den aktuellen fallenden Stein zeichnen (hier in "Red")
        for (col, row) in tetris.current():
            pygame.draw.rect(screen, "Red",
                             (col * block_size, row * block_size, block_size, block_size))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    # Erzeuge eine neue Tetris-Partie und starte die Spielschleife.
    game = MehrsteinTetris(columns=20, rows=30)
    playTetris(game, block_size=30, fps=10)
