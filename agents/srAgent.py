import random

class SimpleReflexAgent:
    def __init__(self):
        pass

    def choose_shot(self, game_board):
        valid_shots = game_board.valid_shots()
        return random.choice(valid_shots)
    
    def report_result(self, coords, result):
        pass

    def choose_ship_placement(self, board, ship):
        attempts = 0
        while True:
            horizontal = random.choice([True, False])
            if horizontal:
                x = random.randint(0, board.size - ship.length)
                y = random.randint(0, board.size - 1)
            else:
                x = random.randint(0, board.size - 1)
                y = random.randint(0, board.size - ship.length)

            valid = True
            for i in range(ship.length):
                xi = x + i if horizontal else x
                yi = y if horizontal else y + i

                if not (0 <= xi < board.size and 0 <= yi < board.size):
                    valid = False
                    break
                if board.grid[yi][xi] == 'ship':
                    valid = False
                    break

            if valid:
                ship.horizontal = horizontal
                return (x, y, horizontal)

            attempts += 1
            if attempts > 1000:
                raise RuntimeError(f"Failed to place ship {ship.name} after 1000 attempts.")