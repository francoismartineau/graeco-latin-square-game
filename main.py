from grid import Grid, GRID_SIZE


def solve_grid(grid):
    while not grid.is_solved():
        for char in "ABCDE12345":
            for row in range(GRID_SIZE):
                candidate_cells = set()
                if grid.char_in_row(char, row):
                    continue
                for column in range(GRID_SIZE):
                    unsolved_associations = grid.get_unsolved_associations(row, column)
                    if len(unsolved_associations) == 1:
                        grid.set_char(row, column, next(iter(unsolved_associations)), True)
                    if not grid.is_taken(row, column, char) and not grid.char_in_column(char, column):
                        candidate_value = grid.get_new_cell_value(row, column, char)
                        if not grid.is_already_solved(candidate_value):
                            candidate_cells.add(column)
                        if len(candidate_cells) > 1:
                            break
                if len(candidate_cells) == 1:
                    column = next(iter(candidate_cells))
                    grid.set_char(row, column, char, True)

            # for column in range(GRID_SIZE):
            #     candidate_cells = set()
            #     if grid.char_in_column(char, column):
            #         continue
            #     for row in range(GRID_SIZE):
            #         if not grid.is_taken(row, column, char) \
            #                 and not grid.char_in_row(char, row) \
            #                 and not grid.is_solved(row, column, char):
            #             candidate_cells.add(row)
            #     if len(candidate_cells) == 1:
            #         row = next(iter(candidate_cells))
            #         grid.set_char(row, column, char, True)

    print(grid.solved_values)


if __name__ == "__main__":
    grid = Grid(1, True)
    grid.display()
    solve_grid(grid)
