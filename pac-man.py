from mazegen.mazegenerator import MazeGenerator
from Hone_3melna_arcade import Game
from parsing import Parsing
import sys


if __name__ == "__main__":
    try:
        parser = Parsing(sys.argv[1])
        dicr = parser.parse()
        w = dicr['width']
        h = dicr['height']
        grids = []
        for i in range(4):
            my_maze = MazeGenerator((w, h), False, (0,0), (0,0), dicr['seed'])
            my_maze.generate(dicr['seed'])
            grid = my_maze.maze
            grid = grid[::-1]
            grids.append(grid)
            w += 1
            h += 1
        game = Game(grids, dicr)
        game.run()
    except ValueError as e:
        print(e)
    except KeyboardInterrupt:
        print("\nNOOOOOOO the code was killed")
    except Exception as e:
        print(e)
