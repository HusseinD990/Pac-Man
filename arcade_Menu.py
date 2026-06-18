import arcade
from typing import Dict
from arcade_Game import swap_color_state, swap_state, load_highscores
from arcade_Game import Ghost, Game

SCREEN_WIDTH = 2000
SCREEN_HEIGHT = 1000
CELL_SIZE = 50

class MenuView(arcade.View):
    def __init__(self, grids: list[list[list[int]]], dicr: Dict) -> None:
        super().__init__()
        self.dicr = dicr
        self.grids = grids
        self.pac_man_pos = (-10, self.window.height / 2 + 400)
        self.pac_man_state = swap_state()
        self.state = 0
        self.modifier = 8
        self.g_modifier = 8
        self.g_state = swap_color_state()
        self.ghosts = []
        self.hgihscores_x = SCREEN_WIDTH

    def on_draw(self):
        self.clear()

        text = arcade.Text(
            "Press Enter To Start",
            self.window.width / 2,
            self.window.height / 2 + 200,
            color=arcade.color.WHITE,
            font_size=30,
            anchor_x="center",
            anchor_y="center"
        )
        text.draw()
        
        p_sheet = arcade.SpriteSheet("pacmanPack/PacMan.png")
        colors = ["green", "red", "yellow", "orange"]
        i = 1
        if not self.ghosts:
            for color in colors:
                self.ghosts.append(Ghost(
                    -100 * i,
                    self.window.height / 2 + 400,
                    color
                ))
                i += 1
        
        p_texture = p_sheet.get_texture_grid(
            size=(16,16),
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
            arcade.draw_texture_rect(texture=p_texture[self.state], rect=p_rect)
        
        if x <= -250 and self.modifier < 0:
            self.modifier *= -1
            y -= 600
            self.pac_man_pos = (x, y)
        
        for g in self.ghosts:
            g_sheet = arcade.SpriteSheet(f"pacmanPack/{g.color}Ghost.png")
            g_textures = g_sheet.get_texture_grid(size=(16,16),
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
        content = load_highscores("highscore.json")
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


    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            self.window.show_view(Game(self.grids, self.dicr))
        if key == arcade.key.ESCAPE:
            self.window.close()