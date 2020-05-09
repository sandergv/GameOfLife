import pygame
import time
import os

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

VERSION_MAJOR = 0
VERSION_MINOR = 1
VERSION_PATCH = 0

TITLE = "Game Of Life"
SCREEN_SIZE = (710, 640)
GRID_SCREEN_SIZE = (600, 600)
GRID_MARGIN = (10, 10)
TEXT_SIZE = 12
LOGS_SCREEN_SIZE = ()

WINDOW_COLOR = (40, 40, 40)
GRID_BG_COLOR = (25, 25, 25)
CELLS_COLOR = (255, 255, 255)  # (200, 240, 100)
TEXT_COLOR = (255, 255, 255)

pygame.init()
FONT_FILE = f"{BASE_PATH}/OpenSans-Regular.ttf"
FONT = pygame.font.Font(FONT_FILE, TEXT_SIZE)  # change


class Text:

    def __init__(self, text, pos_x, pos_y, text_color, callback=True):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.callback = callback
        self.callback_text = text if callback else None
        self.text = text if not callback else ''
        self.text_color = text_color

    def draw(self, screen) -> None:
        screen.blit(
            FONT.render(
                self.callback_text() if self.callback_text else self.text,
                True,
                self.text_color
            ),
            (self.pos_x, self.pos_y)
        )


class Button:

    _color = (62, 62, 62)
    _selected_color = (100, 100, 100)

    def __init__(self, label, pos_x, pos_y, width, height):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.label = label
        self.width = width
        self.height = height
        self.text = FONT.render(label, True, TEXT_COLOR)
        rx = 20 if len(label) == 7 else 13  # temporal fix
        self.text_pos = (pos_x + rx, pos_y + 6)
        self.selected = False
        self.rect = pygame.Rect(self.pos_x, self.pos_y, self.width, self.height)

    def in_range(self, x, y):
        if self.pos_x < x < self.pos_x + self.width:
            if self.pos_y < y < self.pos_y + self.height:
                return True

        return False

    def draw(self, screen) -> None:
        pygame.draw.rect(
            screen,
            self._color if not self.selected else self._selected_color,
            self.rect
        )
        screen.blit(self.text, self.text_pos)


class Cell:

    def __init__(self, pos_x, pos_y, state=0):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.state = state
        self.next_state = state
        self.step = 0
        self.neighbors = []

    # this method consume more memory (I think that is not that much). Find a solution
    def save_neighbors(self, grid) -> None:
        """
        Save neighbors on a list
        :param grid:
        """
        for x in range(self.pos_x - 1, self.pos_x + 2):
            for y in range(self.pos_y - 1, self.pos_y + 2):
                if not (self.pos_x == x and self.pos_y == y):
                    self.neighbors.append(grid.grid[x % grid.width][y % grid.height])

    def sum_neighbors(self) -> int:
        """
        Sum the states of the neighbors.
        This method require each cell with theirs neighbors in a neighbor list,
        it's a little faster than the other method, although it use more memory.
        (maybe it's not too much the difference but there are two ways to do it).
        """
        sn = 0
        for n in self.neighbors:
            sn += n.state

        return sn


class Grid:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = []

        self.active_cells = []
        self.next_active_cells = []
        self.to_update = []

    def init(self) -> None:
        """
        Initialize grid and save every neighbor for each cell.
        (Save the neighbors only if the cell's sum_neighbor is used)
        """
        self.grid = [[Cell(x, y) for y in range(self.width)] for x in range(self.height)]
        for x in range(self.width):
            for y in range(self.height):
                self.grid[x][y].save_neighbors(self)

    def sum_neighbors(self, x, y) -> int:
        """
        Sum the states of the neighbors. This method does not require the neighbor list in each cell
        but take a little more time to calculate.
        :param x:
        :param y:
        :return int:
        """
        sn = 0
        for n in self.get_neighbors(x, y):
            sn += n.state
        return sn

    def get_neighbors(self, x, y) -> iter:
        """
        Get the neighbors when are needed.
        This method is necessary when the grid sum_neighbors is used.
        :param x:
        :param y:
        """
        yield self.grid[(x - 1) % self.width][(y - 1) % self.height]
        yield self.grid[(x - 1) % self.width][y % self.height]
        yield self.grid[(x - 1) % self.width][(y + 1) % self.height]
        yield self.grid[x % self.width][(y - 1) % self.height]
        yield self.grid[x % self.width][(y + 1) % self.height]
        yield self.grid[(x + 1) % self.width][(y - 1) % self.height]
        yield self.grid[(x + 1) % self.width][y % self.height]
        yield self.grid[(x + 1) % self.width][(y + 1) % self.height]

    def update(self) -> None:
        """
        Update the grid to the next state and clean temporal lists
        """
        for c in self.to_update:
            c.state = c.next_state

        self.active_cells = self.next_active_cells
        self.next_active_cells = []
        self.to_update = []

    def activate_cell(self, x, y) -> None:
        """
        Activate cell on the given coordinate
        :param x:
        :param y:
        """
        cell = self.grid[x][y]
        if cell not in self.active_cells:
            cell.state = 1
            self.active_cells.append(cell)

    def deactivate_cell(self, x, y) -> None:
        """
        Deactivate cell on the given coordinate
        :param x:
        :param y:
        """
        cell = self.grid[x][y]
        if cell in self.active_cells:
            cell.state = 0
            self.active_cells.remove(cell)

    def clean_grid(self) -> None:
        """
        Clean the grid returning all states to 0
        """
        for c in self.active_cells:
            c.next_state = 0

        for x in range(self.width):
            for y in range(self.height):
                if self.grid[x][y].step != 0:
                    self.grid[x][y].step = 0

                if self.grid[x][y].state:
                    self.grid[x][y].state = 0

        self.update()

    def get_cell(self, x, y) -> Cell:
        """
        Return the cell on the given coordinate
        :param x:
        :param y:
        :return Cell:
        """
        return self.grid[x][y]

    def insert_pattern(self) -> None:
        pass


class GameOfLife:

    def __init__(self, grid_width=100, grid_height=100):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.grid_width_dim = GRID_SCREEN_SIZE[0] // grid_width
        self.grid_height_dim = GRID_SCREEN_SIZE[1] // grid_height
        self.block_size = GRID_SCREEN_SIZE[0] // grid_width  # check
        self.grid = Grid(grid_width, grid_height)
        self.step = 0
        self.population = 0
        self.exit = False
        self.pause = True
        self.draw_pause = False
        self.screen = None
        self.background = None
        self.font = None
        self.texts = []
        self.buttons = []
        self.version = '.'.join(map(str, [VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH]))

    def init(self) -> None:
        """
        Initialize pygame, the grid and others parameters.
        """
        pygame.display.set_caption(TITLE)
        screen = pygame.display.set_mode(SCREEN_SIZE)
        screen.fill(WINDOW_COLOR)
        self.screen = screen
        self.background = pygame.Surface((GRID_SCREEN_SIZE[0], GRID_SCREEN_SIZE[1])).convert()
        self.screen.blit(self.background, (GRID_MARGIN[0], GRID_MARGIN[1]))
        pygame.display.flip()
        self.grid.init()

        # Component initializations
        text_pos = SCREEN_SIZE[1] - 23
        self.texts.append(Text(lambda: f"Step: {self.step}", 35, text_pos, TEXT_COLOR))
        self.texts.append(Text(lambda: f"Population: {self.population}", 162, text_pos, TEXT_COLOR))
        self.texts.append(Text(lambda: f"To update {len(self.grid.to_update)}", 310, text_pos, TEXT_COLOR))
        self.texts.append(
            Text(lambda: f"Paused: {(self.pause or self.draw_pause)}", 470, text_pos, TEXT_COLOR)
        )
        self.texts.append(Text(f"Version: {self.version}", SCREEN_SIZE[0] - 88, text_pos, TEXT_COLOR, False))
        self.texts.append(Text("Grid size:", SCREEN_SIZE[0] - 88, 20, TEXT_COLOR, False))

        iab = Button("60 x 60", SCREEN_SIZE[0] - 90, 40, 80, 30)  # Initial selected button
        iab.selected = True
        self.buttons.append(iab)
        self.buttons.append(Button("100 x 100", SCREEN_SIZE[0] - 90, 80, 80, 30))
        self.buttons.append(Button("150 x 150", SCREEN_SIZE[0] - 90, 120, 80, 30))
        self.buttons.append(Button("200 x 200", SCREEN_SIZE[0] - 90, 160, 80, 30))

    def apply_rules(self, cell) -> None:
        """
        Apply the game of life rules.
        :param cell:
        """
        n = cell.sum_neighbors()
        if (n > 3 or n < 2) and cell.state:
            cell.next_state = 0
            self.grid.to_update.append(cell)

        elif n == 3 and not cell.state:
            cell.next_state = 1
            self.grid.next_active_cells.append(cell)
            self.grid.to_update.append(cell)

        elif (n == 2 or n == 3) and cell.state:
            cell.next_state = 1
            self.grid.next_active_cells.append(cell)

    def random_pattern(self):
        pass

    def clean(self) -> None:
        """
        Call the clean grid, reset step value and pause the game
        """
        self.step = 0
        self.pause = True
        self.grid.clean_grid()

    def resize_grid(self, width, height):
        self.clean()
        self.grid_width = width
        self.grid_height = height
        self.grid_width_dim = GRID_SCREEN_SIZE[0] // width
        self.grid_height_dim = GRID_SCREEN_SIZE[1] // height
        self.block_size = GRID_SCREEN_SIZE[0] // width  # check
        self.grid = Grid(width, height)
        self.grid.init()

    def check_events(self) -> None:
        """
        Evaluate pygame events
        """
        for event in pygame.event.get():
            m = pygame.mouse.get_pressed()

            if sum(m) > 0:
                px, py = pygame.mouse.get_pos()
                pcx, pcy = (px - GRID_MARGIN[0]) // self.grid_width_dim, (py - GRID_MARGIN[1]) // self.grid_height_dim

                if px > GRID_MARGIN[0] + 1 and py > GRID_MARGIN[1] + 1:
                    if pcx < self.grid_width and pcy < self.grid_height:
                        self.draw_pause = True
                        if m[0] > 0:
                            self.grid.activate_cell(pcx, pcy)

                        elif m[2] > 0:
                            self.grid.deactivate_cell(pcx, pcy)

                # temporal solution
                for b in self.buttons:
                    if b.in_range(px, py):
                        self.pause = True
                        b.selected = True
                        g = int(b.label[0]+b.label[1]) if len(b.label) == 7 else int(b.label[0]+b.label[1]+b.label[2])
                        self.resize_grid(g, g)
                        c = self.buttons.copy()
                        c.remove(b)
                        for bc in c:
                            bc.selected = False

            elif self.draw_pause:
                self.draw_pause = False

            if event.type == pygame.QUIT:
                self.exit = True

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.pause = not self.pause
                elif event.key == pygame.K_c:
                    self.clean()

    def draw_cell(self, cell) -> None:
        """
        Draw the given active cell
        :param cell:
        """
        pygame.draw.rect(self.screen,
                         CELLS_COLOR,
                         pygame.Rect(((cell.pos_x * self.block_size) + GRID_MARGIN[0]),
                                     ((cell.pos_y * self.block_size) + GRID_MARGIN[1]),
                                     self.block_size - 1,
                                     self.block_size - 1))

    def draw_components(self) -> None:
        """
        Draw the components in the components list
        """
        for t in self.texts:
            t.draw(self.screen)
        for b in self.buttons:
            b.draw(self.screen)

    def run(self) -> None:
        """
        main execution of the game
        """
        self.init()
        while not self.exit:
            self.screen.fill(WINDOW_COLOR)
            self.screen.blit(self.background, GRID_MARGIN)
            self.check_events()
            self.population = len(self.grid.active_cells)
            self.step += 1 if not self.pause and not self.draw_pause else 0
            for cell in self.grid.active_cells:
                self.draw_cell(cell)
                if not self.pause and not self.draw_pause:
                    self.apply_rules(cell)
                    for n in cell.neighbors:  # self.grid.get_neighbors(cell.pos_x, cell.pos_y):
                        if not n.state and n.step != self.step:
                            self.apply_rules(n)
                            n.step = self.step

            self.draw_components()
            if not self.pause and not self.draw_pause:
                time.sleep(0.03)
                self.grid.update()

            pygame.display.flip()


if __name__ == '__main__':
    GameOfLife(60, 60).run()
