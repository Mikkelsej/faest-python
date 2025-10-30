import random


class SudokuGenerator:
    """Generates Sudoku puzzles and their solutions."""

    def __init__(self, size=9):
        self.size = size
        self.board = [[0 for _ in range(size)] for _ in range(size)]
        self.generate()
        self.solution = [row[:] for row in self.board]
        self.part_sudoku = self.remove_numbers(40)

    def generate(self):
        """Generate a complete Sudoku board."""
        self._fill_board()
        return self.board

    def _fill_board(self):
        """Fill the board with a valid Sudoku solution using backtracking."""
        # use module-level random

        def is_valid(num, row, col):
            for x in range(self.size):
                if self.board[row][x] == num or self.board[x][col] == num:
                    return False
            start_row, start_col = 3 * (row // 3), 3 * (col // 3)
            for i in range(3):
                for j in range(3):
                    if self.board[i + start_row][j + start_col] == num:
                        return False
            return True

        def solve():
            for i in range(self.size):
                for j in range(self.size):
                    if self.board[i][j] == 0:
                        random_nums = list(range(1, self.size + 1))
                        random.shuffle(random_nums)
                        for num in random_nums:
                            if is_valid(num, i, j):
                                self.board[i][j] = num
                                if solve():
                                    return True
                                self.board[i][j] = 0
                        return False
            return True

        solve()

    def remove_numbers(self, count):
        """Remove numbers from the board to create a puzzle."""
        attempts = count
        while attempts > 0:
            r = random.randint(0, self.size - 1)
            c = random.randint(0, self.size - 1)
            if self.board[r][c] != 0:
                self.board[r][c] = 0
                attempts -= 1
        return self.board


generator = SudokuGenerator()
puzzle = generator.part_sudoku
solution = generator.solution


if __name__ == "__main__":
    # use module-level generator when running as script
    for row in solution:
        print(row)
    print("\nSudoku Puzzle:")
    for row in puzzle:
        print(row)
