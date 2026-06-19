from mazegen.mazegenerator import MazeGenerator
from arcade_Menu import MenuView
from parsing import Parsing
import arcade
import sys


if __name__ == "__main__":
    try:
        parser = Parsing(sys.argv[1])
        dicr = parser.parse()
        w = dicr['width']
        h = dicr['height']
        grids = []
        for i in range(10):
            my_maze = MazeGenerator(
                (w, h), False, (0, 0), (0, 0), dicr['seed']
            )
            my_maze.generate(dicr['seed'])
            grid = my_maze.maze
            grid = grid[::-1]
            grids.append(grid)
            w += 1
            h += 1
        window = arcade.Window(fullscreen=True, title="Pac-Man")
        menu = MenuView(grids, dicr)
        window.show_view(menu)
        arcade.run()
    except ValueError as e:
        print(e)
    except KeyboardInterrupt:
        print("\nNOOOOOOO the process was killed")
    # except Exception as e:
    #     print(e)
