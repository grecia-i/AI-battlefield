import random

class GoalBasedAgent:
    def __init__(self, board_size=10):
        self.board_size = board_size
        self.mode = "hunt"       # hunt or target
        self.hits_queue = []     # cells to try when in target mode
        self.last_hits = []      # continuous line of hits
        self.orientation = None  # "horizontal", "vertical", or None

    def reset(self):
        self.mode = "hunt"
        self.hits_queue.clear()
        self.last_hits.clear()
        self.orientation = None

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

            # CHECKS
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
    # -------------------------------
    # Decide next shot
    def choose_shot(self, game_board):
        if self.mode == "hunt":
            return self._hunt_mode(game_board)
        else:
            return self._target_mode(game_board)

    def _hunt_mode(self, game_board):
        """Pick random valid cell in a checkerboard pattern for efficiency."""
        candidates = [(r, c) for r in range(self.board_size)
                            for c in range(self.board_size)
                            if (r + c) % 2 == 0 and game_board.grid[r][c] not in ('H', 'M')]
        if not candidates:
            candidates = [(r, c) for r in range(self.board_size)
                                for c in range(self.board_size)
                                if game_board.grid[r][c] not in ('H', 'M')]
        return random.choice(candidates)

    def _target_mode(self, game_board):
        """Shoot around known hits to sink the ship."""
        while self.hits_queue:
            r, c = self.hits_queue.pop(0)
            if 0 <= r < self.board_size and 0 <= c < self.board_size:
                if game_board.grid[r][c] not in ('H', 'M'):
                    return (r, c)
        # No adjacents left → back to hunt
        self.mode = "hunt"
        self.orientation = None
        self.last_hits.clear()
        return self._hunt_mode(game_board)

    # -------------------------------
    def report_result(self, coords, result):
        r, c = coords
        if result == "H":
            self.mode = "target"
            self.last_hits.append(coords)
            if len(self.last_hits) >= 2 and self.orientation is None:
                r1, c1 = self.last_hits[-2]
                r2, c2 = self.last_hits[-1]
                if r1 == r2:
                    self.orientation = "horizontal"
                elif c1 == c2:
                    self.orientation = "vertical"

            # Add adjacent cells to hits_queue
            if self.orientation == "horizontal":
                self.hits_queue.extend([(r, c - 1), (r, c + 1)])
            elif self.orientation == "vertical":
                self.hits_queue.extend([(r - 1, c), (r + 1, c)])
            else:
                self.hits_queue.extend([(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)])

        elif result == "S":  # Ship sunk
            self.mode = "hunt"
            self.hits_queue.clear()
            self.last_hits.clear()
            self.orientation = None

        elif result == "M":  # Miss → continue with remaining targets
            pass
