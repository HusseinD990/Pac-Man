import arcade
from typing import Tuple, Dict, Callable, Any, List
import random
import time
import math
import sys
from collections import deque
import json
from arcade_Cheats import Cheats

SCREEN_WIDTH = 2000
SCREEN_HEIGHT = 1000
CELL_SIZE = 50


def load_highscores(path: str) -> Dict:
    """Load and sort high scores from a JSON file.

    Args:
        path: Path to the high-score file.

    Returns:
        Dictionary sorted by descending score.
    """
    with open(path, 'r') as f:
        content = json.load(f)
    sorted_content = dict(
        sorted(content.items(), key=lambda item: item[1], reverse=True)
    )
    return sorted_content


def swap_state() -> Callable:
    """Create a Pac-Man animation state generator.

    Returns:
        A callable that returns the next animation frame index.
    """
    i = -1
    timer = 0

    def update_state() -> int:
        nonlocal i
        nonlocal timer
        if timer == 4:
            timer = 0
            i += 1
            if i == 8:
                i = 0
        timer += 1
        return i
    return update_state


def swap_coin_state() -> Callable:
    """Create a coin animation state generator.

    Returns:
        A callable that returns the next coin frame index.
    """
    i = -1
    timer = 0

    def update_coin_state() -> int:
        nonlocal i
        nonlocal timer
        if timer == 8:
            timer = 0
            i += 1
            if i == 6:
                i = 0
        timer += 1
        return i
    return update_coin_state


def swap_color_state() -> Callable:
    """Create a ghost color animation state generator.

    Returns:
        A callable that alternates between ghost color frames.
    """
    i = -1
    timer = 0

    def update_color_state() -> int:
        nonlocal i
        nonlocal timer
        if timer == 8:
            timer = 0
            i += 1
            if i == 2:
                i = 0
        timer += 1
        return i
    return update_color_state


def swap_super_coin_state() -> Callable:
    """Create a super coin animation state generator.

    Returns:
        A callable that returns the next super coin frame index.
    """
    i = -1
    timer = 0

    def update_super_coin_state() -> int:
        nonlocal i
        nonlocal timer
        if timer == 6:
            timer = 0
            i += 1
            if i == 8:
                i = 0
        timer += 1
        return i
    return update_super_coin_state


def create_pac_gums(
        grid: Any, nb_pac_gums: int, height: int, width: int
        ) -> tuple:
    """Generate collectible pac-gums on the map.

    Args:
        grid: Current level grid.
        nb_pac_gums: Desired number of pac-gums.
        height: Grid height.
        width: Grid width.

    Returns:
        A tuple containing the coin matrix and the actual
        number of generated pac-gums.
    """
    forbiden = [
        (0, 0),
        (height - 1, 0),
        (0, width - 1),
        (height - 1, width - 1)
    ]
    count = 0
    coins = []
    for row in range(height):
        coins.append([0] * width)
    if height > 9 and width > 13:
        if nb_pac_gums > height * width - 22:
            nb_pac_gums = height * width - 22
    else:
        if nb_pac_gums > height * width - 4:
            nb_pac_gums = height * width - 4
    while count < nb_pac_gums:
        h = random.randint(0, height - 1)
        w = random.randint(0, width - 1)

        if (h, w) not in forbiden:
            if coins[h][w] == 0 and grid[h][w] != 15:
                coins[h][w] = 1
                count += 1
    return coins, nb_pac_gums


def opp(cur: str, prev: str) -> bool:
    """Determine whether two directions are opposites.

    Args:
        cur: Current direction.
        prev: Previous direction.

    Returns:
        True if the directions are opposite, otherwise False.
    """
    if cur == "down" and prev == "up":
        return True
    if cur == "up" and prev == "down":
        return True
    if cur == "left" and prev == "right":
        return True
    if cur == "right" and prev == "left":
        return True
    return False


def get_pac_pan_pos(width: int, height: int) -> tuple:
    """Compute the starting position of Pac-Man.

    Args:
        width: Level width.
        height: Level height.

    Returns:
        Coordinates of the starting position.
    """
    ft_small = [[1, 0, 0, 0, 1, 1, 1],
                [1, 0, 0, 0, 0, 0, 1],
                [1, 1, 1, 0, 1, 1, 1],
                [0, 0, 1, 0, 1, 0, 0],
                [0, 0, 1, 0, 1, 1, 1]
                ]
    if len(ft_small)*2 > height or len(ft_small[0])*2 > width:
        return width // 2, height // 2
    posy = int((height - len(ft_small)) / 2 + 3)
    posx = int((width - len(ft_small[0])) / 2 + 3)
    return posx, posy


class CountdownTimer:
    """Simple countdown timer with pause and resume support."""
    def __init__(self, seconds: float) -> None:
        """Initialize the timer."""
        self.initial = seconds
        self.remaining = seconds
        self._start = 0.0
        self.running = False

    def start(self) -> None:
        """Start the timer."""
        self._start = time.perf_counter()
        self.remaining = self.initial
        self.running = True

    def pause(self) -> None:
        """Pause the timer."""
        if self.running:
            self.remaining -= time.perf_counter() - self._start
            self.running = False

    def resume(self) -> None:
        """Resume a paused timer."""
        if not self.running:
            self._start = time.perf_counter()
            self.running = True

    def time_left(self) -> float:
        """Get the remaining time.

        Returns:
            Number of seconds remaining.
        """
        if self.running:
            return max(0, self.remaining - (time.perf_counter() - self._start))
        return max(0, self.remaining)

    def is_finished(self) -> bool:
        """Check whether the timer has expired.

        Returns:
            True if no time remains, otherwise False.
        """
        return self.time_left() <= 0


class Ghost:
    """Represents a ghost enemy in the Pac-Man game."""
    def __init__(self, x: int, y: int, color: str) -> None:
        """Initialize a ghost.

        Args:
            x: Initial x-coordinate.
            y: Initial y-coordinate.
            color: Ghost color.
        """
        self.x = float(x)
        self.y = float(y)
        self.timer = CountdownTimer(5)
        self.move = ""
        self.originalColor = color
        self.color = color
        self.is_alive = True
        self.life_timer = 0.0
        self.original_x = x
        self.original_y = y
        self.is_edible = False

    def find_path(
            self,
            grid: Any,
            start: tuple,
            end: tuple, width: int,
            height: int
            ) -> Any:
        """Find the next move toward a target using BFS.

        Args:
            grid: Maze grid.
            start: Ghost position.
            end: Target position.
            width: Grid width.
            height: Grid height.

        Returns:
            Direction of the first step in the shortest path,
            or an empty string if no path exists.
        """
        sx, sy = int(round(start[0])), int(round(start[1]))
        ex, ey = int(round(end[0])),   int(round(end[1]))

        if (sx, sy) == (ex, ey):
            return ""

        directions = [
            (0,  1, "up",    1),
            (0, -1, "down",  4),
            (1,  0, "right", 2),
            (-1,  0, "left",  8),
        ]

        queue: deque = deque()
        visited = set()
        parent: Dict = {}

        queue.append((sx, sy))
        visited.add((sx, sy))

        while queue:
            x, y = queue.popleft()

            if (x, y) == (ex, ey):
                cur = (x, y)
                while True:
                    prev, direction = parent[cur]
                    if prev == (sx, sy):
                        return direction
                    cur = prev

            cell = grid[y][x]

            for dx, dy, letter, wall_bit in directions:
                nx, ny = x + dx, y + dy

                if (0 <= nx < width and 0 <= ny < height):
                    if (cell & wall_bit) == 0 and (nx, ny) not in visited:
                        queue.append((nx, ny))
                        visited.add((nx, ny))
                        parent[(nx, ny)] = ((x, y), letter)

        return ""


class Game(arcade.View):
    """Main game view containing all gameplay logic."""
    def __init__(self, grids: list[list[list[int]]], dicr: Dict) -> None:
        """Initialize a new game session.

        Args:
            grids: List of level layouts.
            dicr: Game configuration dictionary.
        """
        super().__init__()
        self.cheats = Cheats()
        self.pause = True
        self.lives = dicr['lives']
        self.grids = grids
        self.dicr = dicr
        self.current_level = 0
        self.__width = dicr['width'] + self.current_level
        self.__height = dicr['height'] + self.current_level
        self.pac_man_pos = get_pac_pan_pos(self.__width, self.__height)
        self.pac_man_state = swap_state()
        self.current_grid = grids[self.current_level]
        self.pac_man_direction = 0
        self.coins, self.remaining_points = create_pac_gums(
            self.current_grid,
            dicr['pacgums'],
            self.__height,
            self.__width
        )
        self.coin_state = swap_coin_state()
        self.actual_coins_state = 0
        self.walk: str = ""
        self.previous_direction = self.walk
        self.current_direction = self.walk
        mod = self.current_level
        self.super_coins = [
            (0, 0),
            (0, self.__height - 1 + mod),
            (self.__width - 1 + mod, 0),
            (self.__width - 1 + mod, self.__height - 1 + mod)
        ]
        self.super_coin_state = swap_super_coin_state()
        self.super_actual_coins_state = 0
        self.remaining_super_points = 4
        self.ghosts = self.init_phantome()
        self.camera = arcade.camera.Camera2D()
        self.valid_camera = self.__width > 37 or self.__height >= 20
        self.score = 0
        self.time_left = CountdownTimer(dicr["level_max_time"] + 5)
        self.intro_timer = CountdownTimer(4.1)
        self.intro_timer.start()
        self.time_left.start()
        self.winning_sound = arcade.sound.load_sound(
            "pacmanPack/winning.wav"
        )
        self.super_coin_sound = arcade.sound.load_sound(
            "pacmanPack/super_coin.wav"
        )
        self.intro_sound = arcade.sound.load_sound(
            "pacmanPack/pacman_intro.wav"
        )
        self.eaten_sound = arcade.sound.load_sound(
            "pacmanPack/vine-boom.wav"
        )
        self.player = arcade.sound.play_sound(self.intro_sound)
        self.start = True
        self.coin_sound = arcade.sound.load_sound("pacmanPack/coin.wav")

    def init_phantome(self) -> List[Ghost]:
        """Create and position all ghosts.

        Returns:
            List of initialized ghosts.
        """
        ghosts = []
        x, y = 0, 0
        ghosts.append(Ghost(x, y, "red"))
        x, y = 0, self.__height - 1
        ghosts.append(Ghost(x, y, "orange"))
        x, y = self.__width - 1, 0
        ghosts.append(Ghost(x, y, "green"))
        x, y = self.__width - 1, self.__height - 1
        ghosts.append(Ghost(x, y, "yellow"))
        return ghosts

    def switch_level(self) -> None:
        """Advance to the next level or finish the game."""
        self.current_level += 1
        if self.current_level >= len(self.grids):
            if self.player:
                arcade.sound.stop_sound(self.player)
            arcade.sound.play_sound(self.winning_sound)
            from arcade_Ending import EndView
            self.window.show_view(EndView(
                self.score,
                self.dicr['highscore_filename'],
                self.grids,
                self.dicr)
            )
        else:
            self.__height += 1
            self.__width += 1
            self.current_grid = self.grids[self.current_level]
            self.coins, self.remaining_points = create_pac_gums(
                self.current_grid,
                self.dicr['pacgums'],
                self.__height,
                self.__width
            )
            self.pac_man_pos = get_pac_pan_pos(self.__width, self.__height)
            self.walk = ""
            self.previous_direction = self.walk
            self.current_direction = self.walk
            self.pac_man_direction = 0
            self.super_coins = [(0, 0),
                                (0, self.__height - 1),
                                (self.__width - 1, 0),
                                (self.__width - 1, self.__height - 1)]
            self.remaining_super_points = 4
            self.ghosts = self.init_phantome()
            self.valid_camera = self.__width > 37 or self.__height >= 20
            self.time_left = CountdownTimer(self.dicr["level_max_time"])
            self.time_left.start()

    # press on the keyboard
    def on_key_press(self, key: Any, modifiers: Any) -> None:
        """Handle keyboard input during gameplay.

        Args:
            key: Key pressed by the player.
            modifiers: Active modifier keys.
        """
        if key == arcade.key.F1:
            self.lives += 1
        if key == arcade.key.F2:
            self.switch_level()
        if key == arcade.key.F3:
            self.cheats.speed = not self.cheats.speed
        if key == arcade.key.F4:
            self.cheats.freeze_gost = not self.cheats.freeze_gost
        if key == arcade.key.F5:
            self.cheats.invincibility = not self.cheats.invincibility
        if key == arcade.key.F6:
            self.cheats.wall_pass = not self.cheats.wall_pass
            if not self.cheats.wall_pass:
                self.pac_man_pos = get_pac_pan_pos(self.__width, self.__height)
        if key == arcade.key.F7:
            self.cheats.pause_time = not self.cheats.pause_time
            if self.cheats.pause_time:
                self.time_left.pause()
            else:
                self.time_left.resume()
        if key == arcade.key.ESCAPE:
            self.window.close()
        if self.intro_timer.is_finished():
            if self.pause:
                if key == arcade.key.LEFT or key == arcade.key.A:
                    self.current_direction = "left"
                elif key == arcade.key.RIGHT or key == arcade.key.D:
                    self.current_direction = "right"
                elif key == arcade.key.UP or key == arcade.key.W:
                    self.current_direction = "up"
                elif key == arcade.key.DOWN or key == arcade.key.S:
                    self.current_direction = "down"
            if key == arcade.key.SPACE:
                self.pause = not self.pause
                if self.time_left.running:
                    self.time_left.pause()
                    for g in self.ghosts:
                        g.timer.pause()
                else:
                    self.time_left.resume()
                    for g in self.ghosts:
                        g.timer.resume()

    # scaling on the arcade screen
    def _get_screen_pos(self, x: float, y: float) -> Tuple[float, float]:
        """Convert grid coordinates to screen coordinates.

        Args:
            x: Grid x-coordinate.
            y: Grid y-coordinate.

        Returns:
            Screen-space coordinates.
        """
        num_rows = len(self.current_grid)
        num_cols = len(self.current_grid[0])
        total_grid_width = num_cols * CELL_SIZE
        total_grid_height = num_rows * CELL_SIZE
        start_x = (SCREEN_WIDTH / 2) - (total_grid_width / 2)
        start_y = (SCREEN_HEIGHT / 2) - (total_grid_height / 2)
        return (start_x + (x * CELL_SIZE), start_y + (y * CELL_SIZE))

    def on_update(self, delta_time: float) -> None:
        """Update game state.

        Args:
            delta_time: Time elapsed since the previous frame.
        """
        def _move(c: float) -> float:
            forbiden = [0.0625,
                        0.1875,
                        0.3125,
                        0.4375,
                        0.5625,
                        0.6875,
                        0.8125,
                        0.9375]
            x = 1/16
            if self.cheats.speed:
                x = 1/8
                if (abs(c - int(c)) in forbiden):
                    x -= 1/16
            return x

        x, y = self.pac_man_pos
        px, py = self._get_screen_pos(*self.pac_man_pos)
        if self.pause:
            if self.valid_camera:
                self.camera.position = (px, py)
            if self.walk != self.current_direction:
                if opp(self.current_direction, self.walk):
                    if self.current_direction == "left" and (
                        self.cheats.wall_pass or
                        not self.current_grid[int(y)][math.ceil(x)] & 8
                    ):
                        x -= _move(x)
                        self.pac_man_pos = x, y
                        self.pac_man_direction = 180
                    if self.current_direction == "right" and (
                        self.cheats.wall_pass or
                        not self.current_grid[int(y)][math.floor(x)] & 2
                    ):
                        x += _move(x)
                        self.pac_man_pos = x, y
                        self.pac_man_direction = 0
                    if self.current_direction == "up" and (
                        self.cheats.wall_pass or
                        not self.current_grid[math.floor(y)][int(x)] & 1
                    ):
                        y += _move(y)
                        self.pac_man_pos = x, y
                        self.pac_man_direction = 270
                    if self.current_direction == "down" and (
                        self.cheats.wall_pass or
                        not self.current_grid[math.ceil(y)][int(x)] & 4
                    ):
                        y -= _move(y)
                        self.pac_man_pos = x, y
                        self.pac_man_direction = 90
                    self.walk = self.current_direction
                else:
                    self.previous_direction = self.walk
                    if self.previous_direction == "left" and (
                        self.cheats.wall_pass or not
                        self.current_grid[int(y)][math.ceil(x)] & 8
                    ):
                        x -= _move(x)
                        self.pac_man_pos = x, y
                        self.pac_man_direction = 180
                    if self.previous_direction == "right" and (
                        self.cheats.wall_pass or not
                        self.current_grid[int(y)][math.floor(x)] & 2
                    ):
                        x += _move(x)
                        self.pac_man_pos = x, y
                        self.pac_man_direction = 0
                    if self.previous_direction == "up" and (
                        self.cheats.wall_pass or not
                        self.current_grid[math.floor(y)][int(x)] & 1
                    ):
                        y += _move(y)
                        self.pac_man_pos = x, y
                        self.pac_man_direction = 270
                    if self.previous_direction == "down" and (
                        self.cheats.wall_pass or not
                        self.current_grid[math.ceil(y)][int(x)] & 4
                    ):
                        y -= _move(y)
                        self.pac_man_pos = x, y
                        self.pac_man_direction = 90
                    if x % 1 == 0 and y % 1 == 0:
                        if (
                            self.cheats.wall_pass or not
                            self.current_grid[int(y)][int(x)] & 8
                        ) and self.current_direction == "left":
                            self.walk = self.current_direction
                        if (
                            self.cheats.wall_pass or not
                            self.current_grid[int(y)][int(x)] & 2
                        ) and self.current_direction == "right":
                            self.walk = self.current_direction
                        if (
                            self.cheats.wall_pass or not
                            self.current_grid[int(y)][int(x)] & 1
                        ) and self.current_direction == "up":
                            self.walk = self.current_direction
                        if (
                            self.cheats.wall_pass or not
                            self.current_grid[int(y)][int(x)] & 4
                        ) and self.current_direction == "down":
                            self.walk = self.current_direction
            else:
                if self.walk == "left" and (
                    self.cheats.wall_pass or not
                    self.current_grid[int(y)][math.ceil(x)] & 8
                ):
                    x -= _move(x)
                    self.pac_man_pos = x, y
                    self.pac_man_direction = 180
                if self.walk == "right" and (
                    self.cheats.wall_pass or not
                    self.current_grid[int(y)][math.floor(x)] & 2
                ):
                    x += _move(x)
                    self.pac_man_pos = x, y
                    self.pac_man_direction = 0
                if self.walk == "up" and (
                    self.cheats.wall_pass or not
                    self.current_grid[math.floor(y)][int(x)] & 1
                ):
                    y += _move(y)
                    self.pac_man_pos = x, y
                    self.pac_man_direction = 270
                if self.walk == "down" and (
                    self.cheats.wall_pass or not
                    self.current_grid[math.ceil(y)][int(x)] & 4
                ):
                    y -= _move(y)
                    self.pac_man_pos = x, y
                    self.pac_man_direction = 90
        if self.pause and self.intro_timer.is_finished():
            for g in self.ghosts:
                possible_moves = []
                if g.x % 1 == 0 and g.y % 1 == 0:
                    if not self.current_grid[math.ceil(g.y)][int(g.x)] & 4:
                        possible_moves.append("down")
                    if not self.current_grid[math.floor(g.y)][int(g.x)] & 1:
                        possible_moves.append("up")
                    if not self.current_grid[int(g.y)][math.ceil(g.x)] & 8:
                        possible_moves.append("left")
                    if not self.current_grid[int(g.y)][math.floor(g.x)] & 2:
                        possible_moves.append("right")
                    gx_int = int(round(g.x))
                    gy_int = int(round(g.y))
                    pac_x, pac_y = int(x), int(y)
                    next_step = g.find_path(
                        self.current_grid,
                        (gx_int, gy_int),
                        (pac_x, pac_y),
                        self.__width,
                        self.__height
                    )
                    g.move = next_step
                    if g.is_edible:
                        if len(possible_moves) > 1:
                            if next_step in possible_moves:
                                possible_moves.remove(next_step)
                            g.move = random.choice(possible_moves)
                if not self.cheats.freeze_gost:
                    if g.move == "right":
                        g.x += 1/16
                    if g.move == "left":
                        g.x -= 1/16
                    if g.move == "up":
                        g.y += 1/16
                    if g.move == "down":
                        g.y -= 1/16
                x, y = self.pac_man_pos

                if x - 0.2 <= g.x <= x + 0.2 and y - 0.2 <= g.y <= y + 0.2:
                    if not g.is_edible and not self.cheats.invincibility:
                        self.lives -= 1
                        arcade.sound.play_sound(self.eaten_sound)
                        self.ghosts = self.init_phantome()
                        self.pac_man_pos = get_pac_pan_pos(
                            self.__width,
                            self.__height
                        )
                        if self.lives == 0:
                            from arcade_Ending import EndView
                            self.window.show_view(EndView(
                                self.score,
                                self.dicr['highscore_filename'],
                                self.grids, self.dicr)
                            )
        for g in self.ghosts:
            if g.timer.is_finished():
                g.is_edible = False

    def on_draw(self) -> None:
        """Render the current game state."""
        self.clear()

        with self.camera.activate():
            coin_sheet = arcade.SpriteSheet("pacmanPack/Coin.png")
            coin_textures = coin_sheet.get_texture_grid(
                size=(16, 16),
                columns=8,
                count=8
            )

            super_coin_sheet = arcade.SpriteSheet("pacmanPack/BigCoin.png")
            super_coin_textures = super_coin_sheet.get_texture_grid(
                size=(16, 16),
                columns=8,
                count=8
            )

        # draw the walls
            grid = self.current_grid
            for row_idx, row in enumerate(grid):
                for col_idx, col in enumerate(row):
                    x, y = self._get_screen_pos(col_idx, row_idx)
                    if grid[row_idx][col_idx] & 1:
                        arcade.draw_line(
                            x - CELL_SIZE/2,
                            y + CELL_SIZE/2,
                            x + CELL_SIZE/2,
                            y + CELL_SIZE/2,
                            arcade.color.NEON_GREEN, 5
                        )
                    if grid[row_idx][col_idx] & 2:
                        arcade.draw_line(
                            x + CELL_SIZE/2,
                            y - CELL_SIZE/2,
                            x + CELL_SIZE/2,
                            y + CELL_SIZE/2,
                            arcade.color.NEON_GREEN, 5
                        )
                    if grid[row_idx][col_idx] & 4:
                        arcade.draw_line(
                            x - CELL_SIZE/2,
                            y - CELL_SIZE/2,
                            x + CELL_SIZE/2,
                            y - CELL_SIZE/2,
                            arcade.color.NEON_GREEN, 5
                        )
                    if grid[row_idx][col_idx] & 8:
                        arcade.draw_line(
                            x - CELL_SIZE/2,
                            y - CELL_SIZE/2,
                            x - CELL_SIZE/2,
                            y + CELL_SIZE/2,
                            arcade.color.NEON_GREEN, 5
                        )

            # draw the coins
            for row_idx in range(len(self.coins)):
                for col_idx in range(len(self.coins[row_idx])):
                    px, py = self.pac_man_pos
                    if (
                        col_idx - 0.2 <= px <= col_idx + 0.2 and
                        row_idx - 0.2 <= py <= row_idx + 0.2
                    ):
                        if self.coins[row_idx][col_idx] == 1:
                            self.coins[row_idx][col_idx] = 0
                            arcade.sound.play_sound(self.coin_sound)
                            self.remaining_points -= 1
                            self.score += self.dicr['points_per_pacgum']
                        if (
                            self.remaining_points == 0 and
                            self.remaining_super_points == 0
                        ):
                            self.switch_level()

                    if self.coins[row_idx][col_idx] == 1:
                        x, y = self._get_screen_pos(col_idx, row_idx)
                        coin_rect = arcade.LBWH(
                            left=x - CELL_SIZE/4,
                            bottom=y - CELL_SIZE/4,
                            width=50 - CELL_SIZE/2,
                            height=50 - CELL_SIZE/2
                        )
                        arcade.draw_texture_rect(
                            texture=coin_textures[self.actual_coins_state],
                            rect=coin_rect,
                        )
            self.actual_coins_state = self.coin_state()

            if self.time_left.is_finished():
                sys.exit(1)

            # draw the super coins
            for row_idx in range(len(self.coins)):
                for col_idx in range(len(self.coins[row_idx])):
                    if (col_idx, row_idx) in self.super_coins:
                        x, y = self._get_screen_pos(col_idx, row_idx)
                        super_coin_rect = arcade.LBWH(
                            left=x - CELL_SIZE/4 - 3,
                            bottom=y - CELL_SIZE/4 - 3,
                            width=55 - CELL_SIZE/2,
                            height=55 - CELL_SIZE/2
                        )

                        arcade.draw_texture_rect(
                            texture=super_coin_textures[
                                self.super_actual_coins_state
                            ],
                            rect=super_coin_rect
                        )
                    x, y = self.pac_man_pos
                    if self.pac_man_pos in self.super_coins:
                        self.super_coins.remove((x, y))
                        self.score += self.dicr['points_per_super_pacgum']
                        self.remaining_super_points -= 1
                        arcade.sound.play_sound(self.super_coin_sound)
                        for g in self.ghosts:
                            g.timer = CountdownTimer(5)
                            if not g.timer.running:
                                g.timer.start()
                            g.is_edible = True
            self.super_actual_coins_state = self.super_coin_state()

            # draw the Pac-Man
            tempx, tempy = self.pac_man_pos
            x, y = self._get_screen_pos(tempx, tempy)
            sheet = arcade.SpriteSheet("pacmanPack/PacMan.png")
            textures = sheet.get_texture_grid(
                size=(16, 16),
                columns=8,
                count=8
            )

            pacman_rect = arcade.LBWH(
                left=x - CELL_SIZE/4,
                bottom=y - CELL_SIZE/4,
                width=45 - CELL_SIZE/2,
                height=45 - CELL_SIZE/2
            )

            # draw ghosts
            for g in self.ghosts:
                if g.is_edible and g.timer.time_left() > 2:
                    g.color = "blue"
                elif (
                    g.is_edible and
                    g.timer.time_left() <= 2 and
                    g.timer.time_left() > 0
                ):
                    colors = ["blue", g.originalColor]
                    if math.floor(time.time() * 10) % 2 == 0:
                        g.color = colors[0]
                    else:
                        g.color = colors[1]
                else:
                    g.color = g.originalColor
                tempx, tempy = self._get_screen_pos(g.x, g.y)
                sheet = arcade.SpriteSheet(f"pacmanPack/{g.color}Ghost.png")
                ghost_textures = sheet.get_texture_grid(
                    size=(16, 16),
                    columns=8,
                    count=8
                )

                rect = arcade.LBWH(
                    left=tempx - CELL_SIZE/4,
                    bottom=tempy - CELL_SIZE/4,
                    width=50 - CELL_SIZE/2,
                    height=50 - CELL_SIZE/2
                )
                if g.is_alive:
                    arcade.draw_texture_rect(
                        texture=ghost_textures[self.super_actual_coins_state],
                        rect=rect,
                    )

                px, py = self.pac_man_pos
                if (
                    g.is_edible and
                    px - 0.2 <= g.x <= px + 0.2 and
                    py - 0.2 <= g.y <= py + 0.2
                ):
                    g.x = -1
                    g.y = -1
                    g.is_alive = False
                    self.score += self.dicr['points_per_ghost']
                    g.life_timer = time.time() + 5

                if not g.is_alive and time.time() >= g.life_timer:
                    g.color = g.originalColor
                    g.is_alive = True
                    g.is_edible = False
                    g.x = g.original_x
                    g.y = g.original_y
            if self.pac_man_direction != 180:
                arcade.draw_texture_rect(
                    texture=textures[self.pac_man_state()],
                    rect=pacman_rect,
                    color=arcade.color.WHITE,
                    angle=self.pac_man_direction
                )
            else:
                arcade.draw_texture_rect(
                    texture=textures[self.pac_man_state()].flip_left_right(),
                    rect=pacman_rect,
                    color=arcade.color.WHITE,
                    angle=0
                )

        score_text = arcade.Text(
            f"Score: {self.score}",
            10, 10,
            arcade.color.NEON_GREEN,
            20
        )

        lives_text = arcade.Text(
            f"Lives: {self.lives}",
            1820, 1020,
            arcade.color.RED,
            16
        )
        timer_text = arcade.Text(
            f"{math.floor(self.time_left.time_left()) // 60:02}"
            f":{math.floor(self.time_left.time_left()) % 60:02}",
            1850, 10,
            arcade.color.WHITE,
            16
        )

        lives_text.draw()
        score_text.draw()
        timer_text.draw()
