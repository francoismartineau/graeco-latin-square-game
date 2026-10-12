from grid import Grid, GRID_SIZE

DISPLAY_MOVES = False


def solve_grid(grid):
    while not grid.is_solved():
        for char in "ABCDE12345":
            complementary_chars = grid.get_unsolved_complementary_chars(char)
            cells_containing_char = grid.get_cells(char)
            if len(cells_containing_char) != GRID_SIZE:
                continue
            for complementary_char in complementary_chars:
                candidate_cells = set()
                for cell_containing_char in cells_containing_char:
                    if cell_containing_char.is_solved():
                        continue
                    if not grid.char_in_row(complementary_char, cell_containing_char.row) \
                            and not grid.char_in_column(complementary_char, cell_containing_char.column):
                        candidate_cells.add(cell_containing_char)
                        if len(candidate_cells) > 1:
                            break
                if len(candidate_cells) == 1:
                    cell = next(iter(candidate_cells))
                    grid.set_char(cell.row, cell.column, complementary_char, DISPLAY_MOVES)

        for char in "ABCDE12345":
            for row in range(GRID_SIZE):
                candidate_cells = set()
                if grid.char_in_row(char, row):
                    continue
                for column in range(GRID_SIZE):
                    unsolved_associations = grid.get_unsolved_associations(row, column)
                    if len(unsolved_associations) == 1:
                        grid.set_char(row, column, next(iter(unsolved_associations)), DISPLAY_MOVES)
                    if not grid.is_taken(row, column, char) and not grid.char_in_column(char, column):
                        candidate_value = Grid.Value.from_value(grid.get_cell(row, column), char)
                        if not grid.is_solved_value(candidate_value):
                            candidate_cells.add(column)
                            if len(candidate_cells) > 1:
                                break
                if len(candidate_cells) == 1:
                    column = next(iter(candidate_cells))
                    grid.set_char(row, column, char, DISPLAY_MOVES)
    grid.display()


if __name__ == "__main__":
    grid = Grid(4, True)
    grid.display()
    solve_grid(grid)
