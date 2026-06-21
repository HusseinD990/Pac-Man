import arcade
import json
from arcade_Game import swap_state, load_highscores, swap_color_state
from arcade_Game import Ghost
from typing import Dict, Any, List
from resourcer import resource_path

SCREEN_WIDTH = 2000
SCREEN_HEIGHT = 1000
CELL_SIZE = 50


def add_score(path: str, name: str, score: int) -> None:
    """Store a player's score in the high-score file.

    Args:
        path: Path to the JSON high-score file.
        name: Player name.
        score: Score achieved by the player.
    """
    with open(path, 'r') as f:
        data = json.load(f)
    val = data.get(name, 0)
    if score > val:
        data[name] = score

    with open(path, 'w') as f:
        json.dump(data, f, indent=4)


class EndView(arcade.View):
    """Game-over view.

    Allows the player to enter their name and save
    their score to the high-score table.
    """
    def __init__(self, score: int, path: str, grids: Any, dicr: Dict) -> None:
        """Initialize the end screen.

        Args:
            score: Final player score.
            path: Path to the high-score file.
            grids: List of game levels.
            dicr: Game configuration dictionary.
        """
        super().__init__()
        self.name = ""
        self.grids = grids
        self.dicr = dicr
        self.score = score
        self.path = path
        self.valid = "abcdefghijklmnopqrstuvwxyz"
        self.valid += "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "
        self.pac_man_pos = (-10, self.window.height / 2 + 400)
        self.pac_man_state = swap_state()
        self.state = 0
        self.modifier = 8
        self.g_modifier = 8
        self.g_state = swap_color_state()
        self.ghosts: List[Ghost] = []
        self.hgihscores_x = SCREEN_WIDTH

    def on_draw(self) -> None:
        """Render the end screen and animations."""
        self.clear()

        text = arcade.Text(
            f"Enter your name: {self.name}",
            self.window.width / 2,
            self.window.height / 2 + 200,
            color=arcade.color.WHITE,
            font_size=30,
            anchor_x="center",
            anchor_y="center"
        )
        text.draw()

        p_sheet = arcade.SpriteSheet(resource_path("pacmanPack/PacMan.png"))
        colors = ["green", "red", "yellow", "orange"]
        i = 1
        if not self.ghosts:
            for color in colors:
                self.ghosts.append(Ghost(
                    -100 * i,
                    self.window.height // 2 + 400,
                    color
                ))
                i += 1

        p_texture = p_sheet.get_texture_grid(
            size=(16, 16),
            columns=8,
            count=8
        )
        x, y = self.pac_man_pos
        p_rect = arcade.LBWH(
            left=x - CELL_SIZE/4,
            bottom=y - CELL_SIZE/2,
            width=60,
            height=60
        )
        self.pac_man_pos = (x + self.modifier, y)
        if x >= SCREEN_WIDTH + 500 and self.modifier > 0:
            self.modifier *= -1
        self.state = self.pac_man_state()
        if self.modifier < 0:
            arcade.draw_texture_rect(
                    texture=p_texture[self.state].flip_left_right(),
                    rect=p_rect,
                    color=arcade.color.WHITE,
                    angle=0
                )
        else:
            arcade.draw_texture_rect(
                texture=p_texture[self.state],
                rect=p_rect
            )

        if x <= -250 and self.modifier < 0:
            self.modifier *= -1
            y -= 600
            self.pac_man_pos = (x, y)

        for g in self.ghosts:
            g_sheet = arcade.SpriteSheet(resource_path(
                f"pacmanPack/{g.color}Ghost.png")
            )
            g_textures = g_sheet.get_texture_grid(
                size=(16, 16),
                columns=8,
                count=8
            )
            g_rect = arcade.LBWH(
                left=g.x - CELL_SIZE/4,
                bottom=g.y - CELL_SIZE/2,
                width=60,
                height=60
            )
            arcade.draw_texture_rect(
                texture=g_textures[self.state],
                rect=g_rect
            )
            if g.x >= SCREEN_WIDTH + 400:
                self.g_modifier *= -1
                for g2 in self.ghosts:
                    g2.color = "blue"
            if g.x <= -650 and self.g_modifier < 0:
                self.g_modifier *= -1
                for g2 in self.ghosts:
                    g2.y -= 600
                    g2.color = colors[0]
                    colors.pop(0)
            g.x += self.g_modifier
        content = load_highscores(self.dicr["highscore_filename"])
        s = ""
        i = 1
        for scorer, high_score in content.items():
            s += f"    {i}- {scorer}: {high_score}"
            i += 1
            if i == 11:
                break
        score_text = arcade.Text(
            s[4:],
            self.hgihscores_x,
            30,
            font_size=20
        )
        score_text.draw()
        self.hgihscores_x -= 5
        if self.hgihscores_x < -3130:
            self.hgihscores_x = SCREEN_WIDTH

    def on_text(self, text: str) -> None:
        """Handle text entered by the player.

        Args:
            text: Character entered by the user.
        """
        if len(self.name) < 10 and text in self.valid:
            self.name += text

    def on_key_press(self, key: Any, modifiers: Any) -> None:
        """Handle keyboard input on the end screen.

        Args:
            key: Key pressed by the user.
            modifiers: Active modifier keys.
        """
        if key == arcade.key.BACKSPACE:
            self.name = self.name[:-1]

        elif key == arcade.key.ENTER:
            if self.name.strip():
                add_score(self.path, self.name, self.score)
            from arcade_Menu import MenuView
            self.window.show_view(MenuView(self.grids, self.dicr))
        if key == arcade.key.ESCAPE:
            self.window.close()
