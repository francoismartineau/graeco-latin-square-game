import csv
from pathlib import Path

import colorama

colorama.init(autoreset=True)
GRIDS_PATH = Path(__file__).resolve().parent / "grids"
GRID_SIZE = 5
VALID_CHARS = "ABCDE12345 "


class Grid:
    def __init__(self, grid_id, load_solution=False):
        self.matrix = self.load_file(str(grid_id).zfill(2) + ".csv")
        if load_solution:
            self.solution_matrix = self.load_file(str(grid_id).zfill(2) + "_solution.csv")
        self.remove_underscores(self.matrix)
        self.solved_values = Grid.SolvedValues()
        self.move_count = 0
        self.solved_count = 0
        self.__scan_solved_values()

    def __scan_solved_values(self):
        for row in self.matrix:
            for value in row:
                if self.__is_solved_value(value):
                    self.__save_solved_value(value)

    # TODO: decorator to validate grid
    #   5 * 5
    #   2 chars per cell
    #   supported chars:
    #       1st pos: ABCDE_
    #       2nd pos: 12345_
    @staticmethod
    def load_file(grid_file_name):
        grid_path = GRIDS_PATH / grid_file_name
        try:
            with open(grid_path, newline="", encoding="utf-8") as f:
                return list(csv.reader(f))
        except FileNotFoundError:
            raise SystemExit(f"Error: grid_id '{grid_path}' doesn't exist.")

    @staticmethod
    def remove_underscores(matrix):
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                matrix[y][x] = matrix[y][x].replace("_", " ")

    def get_row(self, index):
        return self.matrix[index]

    def get_column(self, index):
        return [row[index] for row in self.matrix]

    @staticmethod
    def __char_in_cells(char, cells):
        for cell in cells:
            if char in cell:
                return True
        return False

    def char_in_row(self, char, index):
        return self.__char_in_cells(char, self.get_row(index))

    def char_in_column(self, char, index):
        return self.__char_in_cells(char, self.get_column(index))

    def set_char(self, row, column, char, display=False):
        self.__validate_char(char)
        self.__validate_is_not_occupied(row, column, char)

        new_value = self.get_new_cell_value(row, column, char)
        if self.solution_matrix is not None:
            self.__validate_move(row, column, char)

        self.matrix[row][column] = new_value
        if self.__is_solved_value(new_value):
            self.__save_solved_value(new_value)
        self.move_count += 1
        if display:
            self.display(row, column, char)
            print(self.move_count, "moves")

    def __validate_char(self, char):
        if len(char) != 1 or char not in VALID_CHARS:
            raise ValueError(f"Invalid char [char: '{char}']")

    def __validate_is_not_occupied(self, row, column, char):
        if self.__is_occupied(row, column, char):
            raise ValueError(
                f"Cell is already occupied [y='{row}', x='{column}', cell='{self.matrix[row][column]}', char='{char}']")

    def __is_occupied(self, row, column, char):
        index = self.__get_index_in_cell(char)
        return self.matrix[row][column][index] != " "

    def get_new_cell_value(self, row, column, new_char):
        index = self.__get_index_in_cell(new_char)
        current_value = self.matrix[row][column]
        return current_value[:index] + new_char + current_value[index + 1:]

    def __validate_move(self, row, column, char):
        index = self.__get_index_in_cell(char)
        if char != self.solution_matrix[row][column][index]:
            raise ValueError(
                f"Wrong value inserted [y='{row}', x='{column}', insert='{char}', expected='{self.solution_matrix[row][column][index]}']"
            )

    def __get_index_in_cell(self, char):
        return 0 if char.isalpha() else 1

    def __is_solved_value(self, value):
        return not " " in value

    def is_already_solved(self, value):
        if not self.__is_solved_value(value):
            return False
        letter = value[0]
        digit = value[1]
        return digit in self.solved_values.letters[letter]

    def __save_solved_value(self, value):
        letter = value[0]
        digit = value[1]
        self.solved_values.letters[letter].append(digit)
        self.solved_values.digits[digit].append(letter)
        self.solved_count += 1

    def is_taken(self, row, column, char):
        index = self.__get_index_in_cell(char)
        return self.matrix[row][column][index] != " "

    def display(self, accent_row=None, accent_column=None, accent_char=None):
        def row_separator():
            print(GRID_SIZE * "----" + (GRID_SIZE + 1) * "-")

        def print_accent(s, y, x, char, end="\n"):
            if y == accent_row and x == accent_column:
                s = s.replace(char, colorama.Fore.GREEN + char + colorama.Style.RESET_ALL)
            print(s, end=end)

        row_separator()
        for y in range(GRID_SIZE):
            print("|", end="")
            for x in range(GRID_SIZE):
                print_accent(f" {self.matrix[y][x]} |", y, x, accent_char, end="")
            print()
            row_separator()

    def get_unsolved_associations(self, row, column):
        cell_value = self.matrix[row][column]
        char = cell_value.strip()
        if len(char) != 1:
            return set()
        return self.solved_values.get_unsolved_associations(char)

    def is_solved(self):
        return self.solved_count == GRID_SIZE ** 2

    class SolvedValues:
        def __init__(self):
            self.letters = {}
            for letter in "ABCDE":
                self.letters[letter] = []
            self.digits = {}
            for digit in "12345":
                self.digits[digit] = []

        def __getitem__(self, char):
            if char.isalpha():
                return self.letters[char]
            return self.digits[char]

        def get_unsolved_associations(self, char):
            if char.isalpha():
                return set(self.letters[char]) ^ set("12345")
            return set(self.digits[char]) ^ set("ABCDE")

        def __str__(self):
            res = "Solved values:\n"
            for letter in "ABCDE":
                res += "| "
                for digit in "12345":
                    if digit in self.letters[letter]:
                        res += letter + digit
                    else:
                        res += "  "
                    res += " | "
                res += "\n"
            return res
